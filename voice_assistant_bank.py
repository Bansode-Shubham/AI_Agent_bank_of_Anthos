#!/usr/bin/env python3
"""
Voice Assistant with MCP Integration including Bank of Anthos
Complete working version
"""
from dotenv import load_dotenv
load_dotenv()

import os
import tempfile
import wave
import pyaudio
import threading
import queue
import json
import asyncio
from groq import Groq
import pyttsx3
import speech_recognition as sr
from datetime import datetime
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class MCPVoiceAssistant:
    def __init__(self):
        # Initialize Groq client
        self.groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

        # Initialize text-to-speech
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 160)

        # Conversation history
        self.conversation_history = []
        
        # MCP clients for different servers
        self.mcp_sessions = {}
        self.available_tools = {}
        
        # Set Bank of Anthos URL
        os.environ["BANK_ANTHOS_URL"] = "http://127.0.0.1:56992"
        
        # Enhanced system prompt with banking capabilities
        self.system_prompt = """You are a helpful AI assistant with access to various tools through MCP.
        When a user asks for something that might require tool usage, determine if you have an appropriate tool available.
        Keep responses concise and conversational for voice interaction.
        
        You have access to:
        - Banking operations via Bank of Anthos:
          * Login: TOOL_CALL[bank:bank_login]{"username": "alice", "password": "alicepassword"}
          * Check balance: TOOL_CALL[bank:bank_get_balance]{"account_id": "1234567890"}
          * Send payment: TOOL_CALL[bank:bank_send_payment]{"to_account": "9876543210", "amount": "50.00"}
          * View transactions: TOOL_CALL[bank:bank_get_transactions]{"account_id": "1234567890"}
        - API requests for other services
        - File system operations
        
        For banking, common demo users are:
        - alice / alicepassword
        - bob / bobpassword  
        - eve / evepassword
        - testuser / bankofanthos
        
        Always state what you're doing before using tools."""

        print("🎤 MCP Voice Assistant initialized!")
        print("🏦 Bank of Anthos URL:", os.environ.get("BANK_ANTHOS_URL"))
        print("🔧 Loading MCP servers...")
        
        # Initialize MCP connections
        asyncio.run(self.setup_mcp_connections())

    async def setup_mcp_connections(self):
        """Initialize connections to MCP servers"""
        # Define MCP servers to connect to
        mcp_servers = {
            "bank": {
                "command": "python",
                "args": ["bank_anthos_mcp_server.py"]
            },
            "api": {
                "command": "python", 
                "args": ["api_mcp_server.py"]
            }
        }

        for server_name, config in mcp_servers.items():
            try:
                # Create server parameters
                server_params = StdioServerParameters(
                    command=config["command"],
                    args=config["args"]
                )

                # Create and initialize session
                async with stdio_client(server_params) as (read, write):
                    async with ClientSession(read, write) as session:
                        # Initialize the session
                        await session.initialize()
                        
                        # List available tools
                        tools_result = await session.list_tools()
                        
                        # Store session and tools
                        self.mcp_sessions[server_name] = session
                        self.available_tools[server_name] = tools_result.tools
                        
                        print(f"✅ Connected to {server_name} MCP server")
                        for tool in tools_result.tools:
                            print(f"   📋 Tool: {tool.name}")
                            
            except Exception as e:
                print(f"❌ Failed to connect to {server_name} MCP server: {e}")

    def get_tools_context(self):
        """Generate context about available tools for the LLM"""
        if not self.available_tools:
            return ""
        
        tools_context = "\n\nAvailable tools:\n"
        for server_name, tools in self.available_tools.items():
            for tool in tools:
                tools_context += f"- {tool.name}: {tool.description}\n"
                if tool.inputSchema:
                    tools_context += f"  Parameters: {json.dumps(tool.inputSchema, indent=2)}\n"
        
        return tools_context

    async def call_mcp_tool(self, server_name, tool_name, arguments):
        """Call an MCP tool"""
        try:
            if server_name not in self.mcp_sessions:
                return f"Error: {server_name} server not available"
            
            session = self.mcp_sessions[server_name]
            result = await session.call_tool(tool_name, arguments)
            
            if result.isError:
                return f"Tool error: {result.content}"
            else:
                return result.content
                
        except Exception as e:
            return f"Error calling tool {tool_name}: {e}"

    def parse_tool_calls(self, response_text):
        """Parse potential tool calls from LLM response"""
        tool_calls = []
        
        # Look for patterns like: TOOL_CALL[server:tool_name]{arguments}
        import re
        pattern = r'TOOL_CALL\[(\w+):(\w+)\]\{([^}]*)\}'
        matches = re.findall(pattern, response_text)
        
        for match in matches:
            server_name, tool_name, args_str = match
            try:
                arguments = json.loads(args_str) if args_str else {}
                tool_calls.append((server_name, tool_name, arguments))
            except json.JSONDecodeError:
                continue
                
        return tool_calls

    def listen_for_audio(self):
        """Capture audio from microphone"""
        try:
            print("\n🎧 Listening...")
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
            return audio
        except sr.WaitTimeoutError:
            print("⏰ No speech detected, please try again.")
            return None
        except Exception as e:
            print(f"❌ Error capturing audio: {e}")
            return None

    def transcribe_with_groq(self, audio_data):
        """Transcribe audio using Groq's Whisper model"""
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
                temp_audio.write(audio_data.get_wav_data())
                temp_audio_path = temp_audio.name

            with open(temp_audio_path, "rb") as audio_file:
                transcription = self.groq_client.audio.transcriptions.create(
                    file=audio_file,
                    model="whisper-large-v3-turbo",
                    response_format="text",
                    language="en",
                    temperature=0.0
                )

            os.unlink(temp_audio_path)
            return transcription.strip()

        except Exception as e:
            print(f"❌ Transcription error: {e}")
            return None

    async def generate_response_with_tools(self, user_input):
        """Generate AI response with potential tool usage"""
        try:
            # Add user message to history
            self.conversation_history.append({"role": "user", "content": user_input})

            # Prepare messages with tool context
            tools_context = self.get_tools_context()
            enhanced_system_prompt = self.system_prompt + tools_context
            
            messages = [{"role": "system", "content": enhanced_system_prompt}]
            messages.extend(self.conversation_history[-6:])

            print("🤔 Generating response...")

            # Generate initial response
            chat_completion = self.groq_client.chat.completions.create(
                messages=messages,
                model="llama-3.3-70b-versatile",
                temperature=0.7,
                max_tokens=300,
                stream=False
            )

            response = chat_completion.choices[0].message.content

            # Check for tool calls in the response
            tool_calls = self.parse_tool_calls(response)
            
            if tool_calls:
                print("🔧 Executing tools...")
                tool_results = []
                
                for server_name, tool_name, arguments in tool_calls:
                    print(f"   🛠️ Calling {server_name}:{tool_name}")
                    result = await self.call_mcp_tool(server_name, tool_name, arguments)
                    tool_results.append(f"{tool_name} result: {result}")

                # Generate final response with tool results
                tool_context = "\n".join(tool_results)
                follow_up_messages = messages + [
                    {"role": "assistant", "content": response},
                    {"role": "user", "content": f"Tool results:\n{tool_context}\nPlease provide a final response based on these results."}
                ]

                final_completion = self.groq_client.chat.completions.create(
                    messages=follow_up_messages,
                    model="llama-3.3-70b-versatile",
                    temperature=0.7,
                    max_tokens=200,
                    stream=False
                )

                response = final_completion.choices[0].message.content

            # Add response to history
            self.conversation_history.append({"role": "assistant", "content": response})
            return response

        except Exception as e:
            print(f"❌ Error generating response: {e}")
            return "Sorry, I encountered an error processing your request."

    def generate_response(self, user_input):
        """Wrapper to run async response generation"""
        return asyncio.run(self.generate_response_with_tools(user_input))

    def speak_response(self, text):
        """Convert text to speech"""
        try:
            # Clean up any tool call syntax before speaking
            clean_text = text
            import re
            clean_text = re.sub(r'TOOL_CALL\[.*?\]\{.*?\}', '', clean_text)
            
            print(f"🗣️  Speaking: {clean_text}")
            self.tts_engine.say(clean_text)
            self.tts_engine.runAndWait()
        except Exception as e:
            print(f"❌ TTS Error: {e}")
            print(f"📝 Response: {text}")

    def run_conversation_loop(self):
        """Main conversation loop with MCP integration"""
        print("\n🚀 Voice Assistant with Bank of Anthos is ready!")
        print("💡 Try saying:")
        print("   'Login to my bank account with username alice and password alicepassword'")
        print("   'Check my account balance'")
        print("   'Send 25 dollars to Bob'")
        print("   'Show my transaction history'")

        while True:
            try:
                # Listen for audio
                audio = self.listen_for_audio()
                if audio is None:
                    continue

                # Transcribe audio
                user_text = self.transcribe_with_groq(audio)
                if user_text is None:
                    continue

                print(f"👤 You said: {user_text}")

                # Check for exit commands
                if user_text.lower() in ['exit', 'quit', 'goodbye', 'stop']:
                    self.speak_response("Goodbye! Thanks for chatting with me.")
                    break

                # Handle special commands
                if user_text.lower() == 'clear history':
                    self.conversation_history = []
                    self.speak_response("Conversation history cleared.")
                    continue

                if user_text.lower() == 'list tools':
                    tools_list = "Available tools: " + ", ".join([
                        f"{server}.{tool.name}" 
                        for server, tools in self.available_tools.items() 
                        for tool in tools
                    ])
                    self.speak_response(tools_list)
                    continue

                # Generate AI response with tool support
                ai_response = self.generate_response(user_text)

                # Speak the response
                self.speak_response(ai_response)

            except KeyboardInterrupt:
                print("\n\n👋 Assistant stopped by user.")
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                continue

    async def cleanup(self):
        """Clean up MCP connections"""
        for server_name, session in self.mcp_sessions.items():
            try:
                if hasattr(session, 'close'):
                    await session.close()
                print(f"🔌 Disconnected from {server_name} MCP server")
            except Exception as e:
                print(f"⚠️  Error cleaning up {server_name}: {e}")

def main():
    """Main function to run the voice assistant"""
    if not os.environ.get("GROQ_API_KEY"):
        print("❌ Error: GROQ_API_KEY environment variable not set!")
        print("Please set your Groq API key:")
        print("export GROQ_API_KEY='your-api-key-here'")
        return

    assistant = MCPVoiceAssistant()
    try:
        assistant.run_conversation_loop()
    finally:
        # Clean up MCP connections
        asyncio.run(assistant.cleanup())

if __name__ == "__main__":
    main()