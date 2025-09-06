# #!/usr/bin/env python3
# """
# API MCP Server
# Provides tools for making HTTP API requests with various methods and configurations
# """

# import asyncio
# import json
# import logging
# from typing import Any, Dict, Optional, List
# import aiohttp
# from mcp.server.models import InitializeResult
# from mcp.server.lowlevel import NotificationOptions, Server
# from mcp.server import stdio
# from mcp.types import (
#     Resource, Tool, TextContent, ImageContent, EmbeddedResource
# )

# # Set up logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger("api-mcp-server")

# class APIMCPServer:
#     def __init__(self):
#         self.server = Server("api-mcp-server")
#         self.session: Optional[aiohttp.ClientSession] = None
#         self.setup_handlers()

#     async def ensure_session(self):
#         """Ensure we have an active aiohttp session"""
#         if self.session is None or self.session.closed:
#             timeout = aiohttp.ClientTimeout(total=30)
#             self.session = aiohttp.ClientSession(timeout=timeout)

#     async def cleanup_session(self):
#         """Clean up the aiohttp session"""
#         if self.session and not self.session.closed:
#             await self.session.close()

#     def setup_handlers(self):
#         """Set up MCP server handlers"""

#         @self.server.list_tools()
#         async def handle_list_tools() -> List[Tool]:
#             """Return available API tools"""
#             return [
#                 Tool(
#                     name="api_get",
#                     description="Make a GET request to an API endpoint",
#                     inputSchema={
#                         "type": "object",
#                         "properties": {
#                             "url": {
#                                 "type": "string",
#                                 "description": "The API endpoint URL"
#                             },
#                             "headers": {
#                                 "type": "object",
#                                 "description": "Optional headers to include",
#                                 "default": {}
#                             },
#                             "params": {
#                                 "type": "object", 
#                                 "description": "Optional query parameters",
#                                 "default": {}
#                             }
#                         },
#                         "required": ["url"]
#                     }
#                 ),
#                 Tool(
#                     name="api_post",
#                     description="Make a POST request to an API endpoint",
#                     inputSchema={
#                         "type": "object",
#                         "properties": {
#                             "url": {
#                                 "type": "string",
#                                 "description": "The API endpoint URL"
#                             },
#                             "data": {
#                                 "type": "object",
#                                 "description": "JSON data to send in request body",
#                                 "default": {}
#                             },
#                             "headers": {
#                                 "type": "object",
#                                 "description": "Optional headers to include",
#                                 "default": {}
#                             }
#                         },
#                         "required": ["url"]
#                     }
#                 ),
#                 Tool(
#                     name="api_put",
#                     description="Make a PUT request to an API endpoint",
#                     inputSchema={
#                         "type": "object",
#                         "properties": {
#                             "url": {
#                                 "type": "string",
#                                 "description": "The API endpoint URL"
#                             },
#                             "data": {
#                                 "type": "object",
#                                 "description": "JSON data to send in request body",
#                                 "default": {}
#                             },
#                             "headers": {
#                                 "type": "object",
#                                 "description": "Optional headers to include",
#                                 "default": {}
#                             }
#                         },
#                         "required": ["url"]
#                     }
#                 ),
#                 Tool(
#                     name="api_delete",
#                     description="Make a DELETE request to an API endpoint",
#                     inputSchema={
#                         "type": "object",
#                         "properties": {
#                             "url": {
#                                 "type": "string",
#                                 "description": "The API endpoint URL"
#                             },
#                             "headers": {
#                                 "type": "object",
#                                 "description": "Optional headers to include",
#                                 "default": {}
#                             }
#                         },
#                         "required": ["url"]
#                     }
#                 ),
#                 Tool(
#                     name="api_patch",
#                     description="Make a PATCH request to an API endpoint",
#                     inputSchema={
#                         "type": "object",
#                         "properties": {
#                             "url": {
#                                 "type": "string",
#                                 "description": "The API endpoint URL"
#                             },
#                             "data": {
#                                 "type": "object",
#                                 "description": "JSON data to send in request body",
#                                 "default": {}
#                             },
#                             "headers": {
#                                 "type": "object",
#                                 "description": "Optional headers to include",
#                                 "default": {}
#                             }
#                         },
#                         "required": ["url"]
#                     }
#                 ),
#                 Tool(
#                     name="api_request_with_auth",
#                     description="Make an authenticated API request with Bearer token",
#                     inputSchema={
#                         "type": "object",
#                         "properties": {
#                             "url": {
#                                 "type": "string",
#                                 "description": "The API endpoint URL"
#                             },
#                             "method": {
#                                 "type": "string",
#                                 "enum": ["GET", "POST", "PUT", "DELETE", "PATCH"],
#                                 "description": "HTTP method to use"
#                             },
#                             "token": {
#                                 "type": "string",
#                                 "description": "Bearer token for authentication"
#                             },
#                             "data": {
#                                 "type": "object",
#                                 "description": "JSON data to send in request body",
#                                 "default": {}
#                             },
#                             "headers": {
#                                 "type": "object",
#                                 "description": "Additional headers to include",
#                                 "default": {}
#                             }
#                         },
#                         "required": ["url", "method", "token"]
#                     }
#                 )
#             ]

#         @self.server.call_tool()
#         async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
#             """Handle tool calls"""
#             try:
#                 await self.ensure_session()

#                 if name == "api_get":
#                     return await self._handle_get_request(arguments)
#                 elif name == "api_post":
#                     return await self._handle_post_request(arguments)
#                 elif name == "api_put":
#                     return await self._handle_put_request(arguments)
#                 elif name == "api_delete":
#                     return await self._handle_delete_request(arguments)
#                 elif name == "api_patch":
#                     return await self._handle_patch_request(arguments)
#                 elif name == "api_request_with_auth":
#                     return await self._handle_auth_request(arguments)
#                 else:
#                     return [TextContent(type="text", text=f"Unknown tool: {name}")]

#             except Exception as e:
#                 logger.error(f"Error in tool {name}: {e}")
#                 return [TextContent(type="text", text=f"Error: {str(e)}")]

#     async def _handle_get_request(self, args: Dict[str, Any]) -> List[TextContent]:
#         """Handle GET requests"""
#         url = args["url"]
#         headers = args.get("headers", {})
#         params = args.get("params", {})

#         try:
#             async with self.session.get(url, headers=headers, params=params) as response:
#                 response_data = {
#                     "status": response.status,
#                     "headers": dict(response.headers),
#                     "url": str(response.url)
#                 }
                
#                 # Try to get JSON response, fall back to text
#                 try:
#                     body = await response.json()
#                     response_data["body"] = body
#                 except:
#                     body = await response.text()
#                     response_data["body"] = body

#                 return [TextContent(
#                     type="text",
#                     text=f"GET {url}\nStatus: {response.status}\nResponse: {json.dumps(response_data, indent=2)}"
#                 )]

#         except Exception as e:
#             return [TextContent(type="text", text=f"GET request failed: {str(e)}")]

#     async def _handle_post_request(self, args: Dict[str, Any]) -> List[TextContent]:
#         """Handle POST requests"""
#         url = args["url"]
#         data = args.get("data", {})
#         headers = args.get("headers", {})
        
#         # Set default content type if not specified
#         if "Content-Type" not in headers:
#             headers["Content-Type"] = "application/json"

#         try:
#             json_data = data if headers.get("Content-Type") == "application/json" else None
#             async with self.session.post(url, json=json_data, headers=headers) as response:
#                 response_data = {
#                     "status": response.status,
#                     "headers": dict(response.headers),
#                     "url": str(response.url)
#                 }
                
#                 try:
#                     body = await response.json()
#                     response_data["body"] = body
#                 except:
#                     body = await response.text()
#                     response_data["body"] = body

#                 return [TextContent(
#                     type="text",
#                     text=f"POST {url}\nStatus: {response.status}\nResponse: {json.dumps(response_data, indent=2)}"
#                 )]

#         except Exception as e:
#             return [TextContent(type="text", text=f"POST request failed: {str(e)}")]

#     async def _handle_put_request(self, args: Dict[str, Any]) -> List[TextContent]:
#         """Handle PUT requests"""
#         url = args["url"]
#         data = args.get("data", {})
#         headers = args.get("headers", {})
        
#         if "Content-Type" not in headers:
#             headers["Content-Type"] = "application/json"

#         try:
#             json_data = data if headers.get("Content-Type") == "application/json" else None
#             async with self.session.put(url, json=json_data, headers=headers) as response:
#                 response_data = {
#                     "status": response.status,
#                     "headers": dict(response.headers),
#                     "url": str(response.url)
#                 }
                
#                 try:
#                     body = await response.json()
#                     response_data["body"] = body
#                 except:
#                     body = await response.text()
#                     response_data["body"] = body

#                 return [TextContent(
#                     type="text",
#                     text=f"PUT {url}\nStatus: {response.status}\nResponse: {json.dumps(response_data, indent=2)}"
#                 )]

#         except Exception as e:
#             return [TextContent(type="text", text=f"PUT request failed: {str(e)}")]

#     async def _handle_delete_request(self, args: Dict[str, Any]) -> List[TextContent]:
#         """Handle DELETE requests"""
#         url = args["url"]
#         headers = args.get("headers", {})

#         try:
#             async with self.session.delete(url, headers=headers) as response:
#                 response_data = {
#                     "status": response.status,
#                     "headers": dict(response.headers),
#                     "url": str(response.url)
#                 }
                
#                 try:
#                     body = await response.json()
#                     response_data["body"] = body
#                 except:
#                     body = await response.text()
#                     response_data["body"] = body

#                 return [TextContent(
#                     type="text",
#                     text=f"DELETE {url}\nStatus: {response.status}\nResponse: {json.dumps(response_data, indent=2)}"
#                 )]

#         except Exception as e:
#             return [TextContent(type="text", text=f"DELETE request failed: {str(e)}")]

#     async def _handle_patch_request(self, args: Dict[str, Any]) -> List[TextContent]:
#         """Handle PATCH requests"""
#         url = args["url"]
#         data = args.get("data", {})
#         headers = args.get("headers", {})
        
#         if "Content-Type" not in headers:
#             headers["Content-Type"] = "application/json"

#         try:
#             json_data = data if headers.get("Content-Type") == "application/json" else None
#             async with self.session.patch(url, json=json_data, headers=headers) as response:
#                 response_data = {
#                     "status": response.status,
#                     "headers": dict(response.headers),
#                     "url": str(response.url)
#                 }
                
#                 try:
#                     body = await response.json()
#                     response_data["body"] = body
#                 except:
#                     body = await response.text()
#                     response_data["body"] = body

#                 return [TextContent(
#                     type="text",
#                     text=f"PATCH {url}\nStatus: {response.status}\nResponse: {json.dumps(response_data, indent=2)}"
#                 )]

#         except Exception as e:
#             return [TextContent(type="text", text=f"PATCH request failed: {str(e)}")]

#     async def _handle_auth_request(self, args: Dict[str, Any]) -> List[TextContent]:
#         """Handle authenticated requests with Bearer token"""
#         url = args["url"]
#         method = args["method"].upper()
#         token = args["token"]
#         data = args.get("data", {})
#         headers = args.get("headers", {})
        
#         # Add Authorization header
#         headers["Authorization"] = f"Bearer {token}"
        
#         if method in ["POST", "PUT", "PATCH"] and "Content-Type" not in headers:
#             headers["Content-Type"] = "application/json"

#         try:
#             json_data = None
#             if method in ["POST", "PUT", "PATCH"] and data:
#                 json_data = data if headers.get("Content-Type") == "application/json" else None

#             # Make request based on method
#             if method == "GET":
#                 async with self.session.get(url, headers=headers) as response:
#                     result = await self._format_response(method, url, response)
#             elif method == "POST":
#                 async with self.session.post(url, json=json_data, headers=headers) as response:
#                     result = await self._format_response(method, url, response)
#             elif method == "PUT":
#                 async with self.session.put(url, json=json_data, headers=headers) as response:
#                     result = await self._format_response(method, url, response)
#             elif method == "DELETE":
#                 async with self.session.delete(url, headers=headers) as response:
#                     result = await self._format_response(method, url, response)
#             elif method == "PATCH":
#                 async with self.session.patch(url, json=json_data, headers=headers) as response:
#                     result = await self._format_response(method, url, response)
#             else:
#                 return [TextContent(type="text", text=f"Unsupported method: {method}")]

#             return result

#         except Exception as e:
#             return [TextContent(type="text", text=f"Authenticated {method} request failed: {str(e)}")]

#     async def _format_response(self, method: str, url: str, response) -> List[TextContent]:
#         """Format HTTP response for display"""
#         response_data = {
#             "status": response.status,
#             "headers": dict(response.headers),
#             "url": str(response.url)
#         }
        
#         try:
#             body = await response.json()
#             response_data["body"] = body
#         except:
#             body = await response.text()
#             response_data["body"] = body

#         return [TextContent(
#             type="text",
#             text=f"{method} {url}\nStatus: {response.status}\nResponse: {json.dumps(response_data, indent=2)}"
#         )]

#     async def run(self):
#         """Run the MCP server"""
#         try:
#             async with stdio.stdio_server() as (read_stream, write_stream):
#                 await self.server.run(
#                     read_stream,
#                     write_stream,
#                     InitializeResult(
#                         protocolVersion="2024-11-05",
#                         capabilities=self.server.get_capabilities(
#                             notification_options=NotificationOptions(),
#                             experimental_capabilities={},
#                         ),
#                         serverInfo={
#                             "name": "api-mcp-server",
#                             "version": "0.1.0",
#                         },
#                     ),
#                 )
#         finally:
#             await self.cleanup_session()

# async def main():
#     """Main entry point"""
#     server = APIMCPServer()
#     await server.run()

# if __name__ == "__main__":
#     asyncio.run(main())

#!/usr/bin/env python3
"""
API MCP Server
Provides tools for making HTTP API requests with various methods and configurations
"""

import asyncio
import json
import logging
from typing import Any, Dict, Optional, List
import aiohttp
from mcp.server.models import InitializationOptions

from mcp.server.lowlevel import NotificationOptions, Server
from mcp.server import stdio
from mcp.types import (
    Resource, Tool, TextContent, ImageContent, EmbeddedResource
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api-mcp-server")

class APIMCPServer:
    def __init__(self):
        self.server = Server("api-mcp-server")
        self.session: Optional[aiohttp.ClientSession] = None
        self.setup_handlers()

    async def ensure_session(self):
        """Ensure we have an active aiohttp session"""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(timeout=timeout)

    async def cleanup_session(self):
        """Clean up the aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()

    def setup_handlers(self):
        """Set up MCP server handlers"""

        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """Return available API tools"""
            return [
                Tool(
                    name="api_get",
                    description="Make a GET request to an API endpoint",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "The API endpoint URL"
                            },
                            "headers": {
                                "type": "object",
                                "description": "Optional headers to include",
                                "default": {}
                            },
                            "params": {
                                "type": "object", 
                                "description": "Optional query parameters",
                                "default": {}
                            }
                        },
                        "required": ["url"]
                    }
                ),
                Tool(
                    name="api_post",
                    description="Make a POST request to an API endpoint",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "The API endpoint URL"
                            },
                            "data": {
                                "type": "object",
                                "description": "JSON data to send in request body",
                                "default": {}
                            },
                            "headers": {
                                "type": "object",
                                "description": "Optional headers to include",
                                "default": {}
                            }
                        },
                        "required": ["url"]
                    }
                ),
                Tool(
                    name="api_put",
                    description="Make a PUT request to an API endpoint",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "The API endpoint URL"
                            },
                            "data": {
                                "type": "object",
                                "description": "JSON data to send in request body",
                                "default": {}
                            },
                            "headers": {
                                "type": "object",
                                "description": "Optional headers to include",
                                "default": {}
                            }
                        },
                        "required": ["url"]
                    }
                ),
                Tool(
                    name="api_delete",
                    description="Make a DELETE request to an API endpoint",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "The API endpoint URL"
                            },
                            "headers": {
                                "type": "object",
                                "description": "Optional headers to include",
                                "default": {}
                            }
                        },
                        "required": ["url"]
                    }
                ),
                Tool(
                    name="api_patch",
                    description="Make a PATCH request to an API endpoint",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "The API endpoint URL"
                            },
                            "data": {
                                "type": "object",
                                "description": "JSON data to send in request body",
                                "default": {}
                            },
                            "headers": {
                                "type": "object",
                                "description": "Optional headers to include",
                                "default": {}
                            }
                        },
                        "required": ["url"]
                    }
                ),
                Tool(
                    name="api_request_with_auth",
                    description="Make an authenticated API request with Bearer token",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "The API endpoint URL"
                            },
                            "method": {
                                "type": "string",
                                "enum": ["GET", "POST", "PUT", "DELETE", "PATCH"],
                                "description": "HTTP method to use"
                            },
                            "token": {
                                "type": "string",
                                "description": "Bearer token for authentication"
                            },
                            "data": {
                                "type": "object",
                                "description": "JSON data to send in request body",
                                "default": {}
                            },
                            "headers": {
                                "type": "object",
                                "description": "Additional headers to include",
                                "default": {}
                            }
                        },
                        "required": ["url", "method", "token"]
                    }
                )
            ]

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Handle tool calls"""
            try:
                await self.ensure_session()

                if name == "api_get":
                    return await self._handle_get_request(arguments)
                elif name == "api_post":
                    return await self._handle_post_request(arguments)
                elif name == "api_put":
                    return await self._handle_put_request(arguments)
                elif name == "api_delete":
                    return await self._handle_delete_request(arguments)
                elif name == "api_patch":
                    return await self._handle_patch_request(arguments)
                elif name == "api_request_with_auth":
                    return await self._handle_auth_request(arguments)
                else:
                    return [TextContent(type="text", text=f"Unknown tool: {name}")]

            except Exception as e:
                logger.error(f"Error in tool {name}: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]

    async def _handle_get_request(self, args: Dict[str, Any]) -> List[TextContent]:
        """Handle GET requests"""
        url = args["url"]
        headers = args.get("headers", {})
        params = args.get("params", {})

        try:
            async with self.session.get(url, headers=headers, params=params) as response:
                response_data = {
                    "status": response.status,
                    "headers": dict(response.headers),
                    "url": str(response.url)
                }
                
                # Try to get JSON response, fall back to text
                try:
                    body = await response.json()
                    response_data["body"] = body
                except:
                    body = await response.text()
                    response_data["body"] = body

                return [TextContent(
                    type="text",
                    text=f"GET {url}\nStatus: {response.status}\nResponse: {json.dumps(response_data, indent=2)}"
                )]

        except Exception as e:
            return [TextContent(type="text", text=f"GET request failed: {str(e)}")]

    async def _handle_post_request(self, args: Dict[str, Any]) -> List[TextContent]:
        """Handle POST requests"""
        url = args["url"]
        data = args.get("data", {})
        headers = args.get("headers", {})
        
        # Set default content type if not specified
        if "Content-Type" not in headers:
            headers["Content-Type"] = "application/json"

        try:
            json_data = data if headers.get("Content-Type") == "application/json" else None
            async with self.session.post(url, json=json_data, headers=headers) as response:
                response_data = {
                    "status": response.status,
                    "headers": dict(response.headers),
                    "url": str(response.url)
                }
                
                try:
                    body = await response.json()
                    response_data["body"] = body
                except:
                    body = await response.text()
                    response_data["body"] = body

                return [TextContent(
                    type="text",
                    text=f"POST {url}\nStatus: {response.status}\nResponse: {json.dumps(response_data, indent=2)}"
                )]

        except Exception as e:
            return [TextContent(type="text", text=f"POST request failed: {str(e)}")]

    async def _handle_put_request(self, args: Dict[str, Any]) -> List[TextContent]:
        """Handle PUT requests"""
        url = args["url"]
        data = args.get("data", {})
        headers = args.get("headers", {})
        
        if "Content-Type" not in headers:
            headers["Content-Type"] = "application/json"

        try:
            json_data = data if headers.get("Content-Type") == "application/json" else None
            async with self.session.put(url, json=json_data, headers=headers) as response:
                response_data = {
                    "status": response.status,
                    "headers": dict(response.headers),
                    "url": str(response.url)
                }
                
                try:
                    body = await response.json()
                    response_data["body"] = body
                except:
                    body = await response.text()
                    response_data["body"] = body

                return [TextContent(
                    type="text",
                    text=f"PUT {url}\nStatus: {response.status}\nResponse: {json.dumps(response_data, indent=2)}"
                )]

        except Exception as e:
            return [TextContent(type="text", text=f"PUT request failed: {str(e)}")]

    async def _handle_delete_request(self, args: Dict[str, Any]) -> List[TextContent]:
        """Handle DELETE requests"""
        url = args["url"]
        headers = args.get("headers", {})

        try:
            async with self.session.delete(url, headers=headers) as response:
                response_data = {
                    "status": response.status,
                    "headers": dict(response.headers),
                    "url": str(response.url)
                }
                
                try:
                    body = await response.json()
                    response_data["body"] = body
                except:
                    body = await response.text()
                    response_data["body"] = body

                return [TextContent(
                    type="text",
                    text=f"DELETE {url}\nStatus: {response.status}\nResponse: {json.dumps(response_data, indent=2)}"
                )]

        except Exception as e:
            return [TextContent(type="text", text=f"DELETE request failed: {str(e)}")]

    async def _handle_patch_request(self, args: Dict[str, Any]) -> List[TextContent]:
        """Handle PATCH requests"""
        url = args["url"]
        data = args.get("data", {})
        headers = args.get("headers", {})
        
        if "Content-Type" not in headers:
            headers["Content-Type"] = "application/json"

        try:
            json_data = data if headers.get("Content-Type") == "application/json" else None
            async with self.session.patch(url, json=json_data, headers=headers) as response:
                response_data = {
                    "status": response.status,
                    "headers": dict(response.headers),
                    "url": str(response.url)
                }
                
                try:
                    body = await response.json()
                    response_data["body"] = body
                except:
                    body = await response.text()
                    response_data["body"] = body

                return [TextContent(
                    type="text",
                    text=f"PATCH {url}\nStatus: {response.status}\nResponse: {json.dumps(response_data, indent=2)}"
                )]

        except Exception as e:
            return [TextContent(type="text", text=f"PATCH request failed: {str(e)}")]

    async def _handle_auth_request(self, args: Dict[str, Any]) -> List[TextContent]:
        """Handle authenticated requests with Bearer token"""
        url = args["url"]
        method = args["method"].upper()
        token = args["token"]
        data = args.get("data", {})
        headers = args.get("headers", {})
        
        # Add Authorization header
        headers["Authorization"] = f"Bearer {token}"
        
        if method in ["POST", "PUT", "PATCH"] and "Content-Type" not in headers:
            headers["Content-Type"] = "application/json"

        try:
            json_data = None
            if method in ["POST", "PUT", "PATCH"] and data:
                json_data = data if headers.get("Content-Type") == "application/json" else None

            # Make request based on method
            if method == "GET":
                async with self.session.get(url, headers=headers) as response:
                    result = await self._format_response(method, url, response)
            elif method == "POST":
                async with self.session.post(url, json=json_data, headers=headers) as response:
                    result = await self._format_response(method, url, response)
            elif method == "PUT":
                async with self.session.put(url, json=json_data, headers=headers) as response:
                    result = await self._format_response(method, url, response)
            elif method == "DELETE":
                async with self.session.delete(url, headers=headers) as response:
                    result = await self._format_response(method, url, response)
            elif method == "PATCH":
                async with self.session.patch(url, json=json_data, headers=headers) as response:
                    result = await self._format_response(method, url, response)
            else:
                return [TextContent(type="text", text=f"Unsupported method: {method}")]

            return result

        except Exception as e:
            return [TextContent(type="text", text=f"Authenticated {method} request failed: {str(e)}")]

    async def _format_response(self, method: str, url: str, response) -> List[TextContent]:
        """Format HTTP response for display"""
        response_data = {
            "status": response.status,
            "headers": dict(response.headers),
            "url": str(response.url)
        }
        
        try:
            body = await response.json()
            response_data["body"] = body
        except:
            body = await response.text()
            response_data["body"] = body

        return [TextContent(
            type="text",
            text=f"{method} {url}\nStatus: {response.status}\nResponse: {json.dumps(response_data, indent=2)}"
        )]

    async def run(self):
        """Run the MCP server"""
        try:
            async with stdio.stdio_server() as (read_stream, write_stream):
                await self.server.run(
                    read_stream,
                    write_stream,
                    InitializationOptions(
                        server_name="api-mcp-server",
                        server_version="0.1.0",
                        capabilities=self.server.get_capabilities(
                            notification_options=NotificationOptions(),
                            experimental_capabilities={},
                            ),
                        ),
                    ),
        finally:
            await self.cleanup_session()

async def main():
    """Main entry point"""
    server = APIMCPServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())