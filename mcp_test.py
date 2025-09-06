#!/usr/bin/env python3
"""
Simple test script to verify MCP connectivity
"""
import asyncio
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

async def test_mcp_connection():
    """Test basic MCP filesystem server connection"""
    try:
        print("🔧 Testing MCP filesystem server connection...")
        
        # Create server parameters
        server_params = StdioServerParameters(
            command="npx",
            args=["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]
        )
        
        print("📡 Starting server...")
        
        # Create stdio client connection
        async with stdio_client(server_params) as (read_stream, write_stream):
            # Create client session
            session = ClientSession(read_stream, write_stream)
            
            print("🤝 Initializing session...")
            await session.initialize()
            
            print("🔍 Listing available tools...")
            tools_result = await session.list_tools()
            
            print(f"✅ Success! Found {len(tools_result.tools)} tools:")
            for tool in tools_result.tools:
                print(f"  📋 {tool.name}: {tool.description}")
            
            # Test a simple tool call
            print("\n🛠️  Testing file listing...")
            try:
                result = await session.call_tool("list_directory", {"path": "/tmp"})
                print(f"📁 Directory listing result: {result}")
            except Exception as e:
                print(f"⚠️  Tool call failed: {e}")
                
    except Exception as e:
        print(f"❌ MCP test failed: {e}")
        print("\nTroubleshooting tips:")
        print("1. Make sure Node.js is installed: node --version")
        print("2. Check if npm/npx is working: npx --version")
        print("3. Try manually: npx -y @modelcontextprotocol/server-filesystem /tmp")
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_mcp_connection())
    if success:
        print("\n🎉 MCP connection test successful! You can now run the voice assistant.")
    else:
        print("\n💥 MCP connection test failed. Please fix the issues above before running the voice assistant.")