#!/usr/bin/env python3
"""
Simple Local Voice Assistant using Groq Cloud API
This is a basic implementation for learning purposes.
"""
from dotenv import load_dotenv
load_dotenv()

import os
import tempfile
import wave
import pyaudio
import threading
import queue
from groq import Groq
import pyttsx3  # For local TTS as backup
import speech_recognition as sr
from datetime import datetime

class SimpleVoiceAssistant:
    def __init__(self):
        # Initialize Groq client
        self.groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

        # Initialize text-to-speech
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 160)  # Speed of speech

        # Conversation history
        self.conversation_history = []
        self.system_prompt = """You are a helpful AI assistant. 
        Keep your responses concise and conversational, 
        suitable for voice interaction (under 100 words)."""

        print("🎤 Groq Voice Assistant initialized!")
        print("Say 'exit' or 'quit' to stop the assistant.")

    def listen_for_audio(self):
        """Capture audio from microphone"""
        try:
            print("\n🎧 Listening...")
            with self.microphone as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                # Listen for audio
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
            # Convert audio to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
                temp_audio.write(audio_data.get_wav_data())
                temp_audio_path = temp_audio.name

            # Transcribe using Groq
            with open(temp_audio_path, "rb") as audio_file:
                transcription = self.groq_client.audio.transcriptions.create(
                    file=audio_file,
                    model="whisper-large-v3-turbo",
                    response_format="text",
                    language="en",
                    temperature=0.0
                )

            # Clean up temporary file
            os.unlink(temp_audio_path)

            return transcription.strip()

        except Exception as e:
            print(f"❌ Transcription error: {e}")
            return None

    def generate_response(self, user_input):
        """Generate AI response using Groq's LLM"""
        try:
            # Add user message to history
            self.conversation_history.append({"role": "user", "content": user_input})

            # Prepare messages for API call
            messages = [{"role": "system", "content": self.system_prompt}]
            # Keep last 6 messages for context (3 back-and-forth exchanges)
            messages.extend(self.conversation_history[-6:])

            print("🤔 Generating response...")

            # Generate response using Groq
            chat_completion = self.groq_client.chat.completions.create(
                messages=messages,
                model="llama-3.3-70b-versatile",  # Fast and capable model
                temperature=0.7,
                max_tokens=150,
                stream=False
            )

            response = chat_completion.choices[0].message.content

            # Add response to history
            self.conversation_history.append({"role": "assistant", "content": response})

            return response

        except Exception as e:
            print(f"❌ Error generating response: {e}")
            return "Sorry, I encountered an error processing your request."

    def speak_response(self, text):
        """Convert text to speech"""
        try:
            print(f"🗣️  Speaking: {text}")
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            print(f"❌ TTS Error: {e}")
            print(f"📝 Response: {text}")

    def run_conversation_loop(self):
        """Main conversation loop"""
        print("\n🚀 Voice Assistant is ready! Start speaking...")

        while True:
            try:
                # Step 1: Listen for audio
                audio = self.listen_for_audio()
                if audio is None:
                    continue

                # Step 2: Transcribe audio
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

                # Step 3: Generate AI response
                ai_response = self.generate_response(user_text)

                # Step 4: Speak the response
                self.speak_response(ai_response)

            except KeyboardInterrupt:
                print("\n\n👋 Assistant stopped by user.")
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                continue

def main():
    """Main function to run the voice assistant"""
    # Check if API key is set
    if not os.environ.get("GROQ_API_KEY"):
        print("❌ Error: GROQ_API_KEY environment variable not set!")
        print("Please set your Groq API key:")
        print("export GROQ_API_KEY='your-api-key-here'")
        return

    # Create and run assistant
    assistant = SimpleVoiceAssistant()
    assistant.run_conversation_loop()

if __name__ == "__main__":
    main()