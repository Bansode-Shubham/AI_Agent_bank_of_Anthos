# #!/usr/bin/env python3
# """
# Bank of Anthos MCP Server
# Provides tools for interacting with Google Cloud's Bank of Anthos demo application
# """

# import asyncio
# import json
# import logging
# from typing import Any, Dict, Optional, List
# import aiohttp
# from mcp.server.models import InitializeResult
# # from mcp.server.server import NotificationOptions, Server
# from mcp.server.lowlevel import NotificationOptions, Server


# from mcp.server import stdio
# from mcp.types import (
#     Resource, Tool, TextContent, ImageContent, EmbeddedResource
# )

# # Set up logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger("bank-anthos-mcp-server")

# class BankAnthosMCPServer:
#     def __init__(self, base_url="http://localhost:8080"):
#         self.server = Server("bank-anthos-mcp-server")
#         self.session: Optional[aiohttp.ClientSession] = None
#         self.base_url = base_url
#         self.auth_token = None
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
#             """Return available Bank of Anthos tools"""
#             return [
#                 Tool(
#                     name="bank_login",
#                     description="Login to Bank of Anthos and get authentication token",
#                     inputSchema={
#                         "type": "object",
#                         "properties": {
#                             "username": {
#                                 "type": "string",
#                                 "description": "Username for login"
#                             },
#                             "password": {
#                                 "type": "string",
#                                 "description": "Password for login"
#                             }
#                         },
#                         "required": ["username", "password"]
#                     }
#                 ),
#                 Tool(
#                     name="bank_get_balance",
#                     description="Get account balance for authenticated user",
#                     inputSchema={
#                         "type": "object",
#                         "properties": {
#                             "account_id": {
#                                 "type": "string",
#                                 "description": "Account ID to check balance for"
#                             }
#                         },
#                         "required": ["account_id"]
#                     }
#                 ),
#                 Tool(
#                     name="bank_get_transactions",
#                     description="Get transaction history for an account",
#                     inputSchema={
#                         "type": "object",
#                         "properties": {
#                             "account_id": {
#                                 "type": "string",
#                                 "description": "Account ID to get transactions for"
#                             },
#                             "limit": {
#                                 "type": "integer",
#                                 "description": "Limit number of transactions returned",
#                                 "default": 10
#                             }
#                         },
#                         "required": ["account_id"]
#                     }
#                 ),
#                 Tool(
#                     name="bank_send_payment",
#                     description="Send payment to another account",
#                     inputSchema={
#                         "type": "object",
#                         "properties": {
#                             "to_account": {
#                                 "type": "string",
#                                 "description": "Recipient account number"
#                             },
#                             "amount": {
#                                 "type": "string",
#                                 "description": "Amount to send (e.g., '100.50')"
#                             },
#                             "label": {
#                                 "type": "string",
#                                 "description": "Optional label for the payment",
#                                 "default": ""
#                             }
#                         },
#                         "required": ["to_account", "amount"]
#                     }
#                 ),
#                 Tool(
#                     name="bank_deposit",
#                     description="Deposit money from external account",
#                     inputSchema={
#                         "type": "object",
#                         "properties": {
#                             "external_account": {
#                                 "type": "string",
#                                 "description": "External account number"
#                             },
#                             "external_routing": {
#                                 "type": "string",
#                                 "description": "External routing number"
#                             },
#                             "amount": {
#                                 "type": "string",
#                                 "description": "Amount to deposit (e.g., '100.50')"
#                             },
#                             "label": {
#                                 "type": "string",
#                                 "description": "Optional label for external account",
#                                 "default": ""
#                             }
#                         },
#                         "required": ["external_account", "external_routing", "amount"]
#                     }
#                 ),
#                 Tool(
#                     name="bank_get_contacts",
#                     description="Get user's contact list",
#                     inputSchema={
#                         "type": "object",
#                         "properties": {
#                             "username": {
#                                 "type": "string",
#                                 "description": "Username to get contacts for"
#                             }
#                         },
#                         "required": ["username"]
#                     }
#                 ),
#                 Tool(
#                     name="bank_add_contact",
#                     description="Add a new contact to user's contact list",
#                     inputSchema={
#                         "type": "object",
#                         "properties": {
#                             "username": {
#                                 "type": "string",
#                                 "description": "Username to add contact for"
#                             },
#                             "label": {
#                                 "type": "string",
#                                 "description": "Contact label/name"
#                             },
#                             "account_num": {
#                                 "type": "string",
#                                 "description": "Contact's account number"
#                             },
#                             "routing_num": {
#                                 "type": "string",
#                                 "description": "Contact's routing number"
#                             },
#                             "is_external": {
#                                 "type": "boolean",
#                                 "description": "Whether this is an external account",
#                                 "default": False
#                             }
#                         },
#                         "required": ["username", "label", "account_num", "routing_num"]
#                     }
#                 ),
#                 Tool(
#                     name="bank_create_user",
#                     description="Create a new user account",
#                     inputSchema={
#                         "type": "object",
#                         "properties": {
#                             "username": {
#                                 "type": "string",
#                                 "description": "Desired username"
#                             },
#                             "password": {
#                                 "type": "string",
#                                 "description": "Password for the account"
#                             },
#                             "password-repeat": {
#                                 "type": "string",
#                                 "description": "Password confirmation"
#                             },
#                             "firstname": {
#                                 "type": "string",
#                                 "description": "First name"
#                             },
#                             "lastname": {
#                                 "type": "string",
#                                 "description": "Last name"
#                             },
#                             "birthday": {
#                                 "type": "string",
#                                 "description": "Birthday in YYYY-MM-DD format"
#                             },
#                             "timezone": {
#                                 "type": "string",
#                                 "description": "Timezone (e.g., 'America/New_York')"
#                             },
#                             "address": {
#                                 "type": "string",
#                                 "description": "Street address"
#                             },
#                             "state": {
#                                 "type": "string",
#                                 "description": "State"
#                             },
#                             "zip": {
#                                 "type": "string",
#                                 "description": "ZIP code"
#                             },
#                             "ssn": {
#                                 "type": "string",
#                                 "description": "Social Security Number"
#                             }
#                         },
#                         "required": ["username", "password", "password-repeat", "firstname", "lastname", "birthday", "timezone", "address", "state", "zip", "ssn"]
#                     }
#                 )
#             ]

#         @self.server.call_tool()
#         async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
#             """Handle tool calls"""
#             try:
#                 await self.ensure_session()

#                 if name == "bank_login":
#                     return await self._handle_login(arguments)
#                 elif name == "bank_get_balance":
#                     return await self._handle_get_balance(arguments)
#                 elif name == "bank_get_transactions":
#                     return await self._handle_get_transactions(arguments)
#                 elif name == "bank_send_payment":
#                     return await self._handle_send_payment(arguments)
#                 elif name == "bank_deposit":
#                     return await self._handle_deposit(arguments)
#                 elif name == "bank_get_contacts":
#                     return await self._handle_get_contacts(arguments)
#                 elif name == "bank_add_contact":
#                     return await self._handle_add_contact(arguments)
#                 elif name == "bank_create_user":
#                     return await self._handle_create_user(arguments)
#                 else:
#                     return [TextContent(type="text", text=f"Unknown tool: {name}")]

#             except Exception as e:
#                 logger.error(f"Error in tool {name}: {e}")
#                 return [TextContent(type="text", text=f"Error: {str(e)}")]

#     async def _handle_login(self, args: Dict[str, Any]) -> List[TextContent]:
#         """Handle login request"""
#         username = args["username"]
#         password = args["password"]

#         try:
#             params = {
#                 'username': username,
#                 'password': password
#             }
            
#             async with self.session.get(
#                 f"{self.base_url}/login",
#                 params=params
#             ) as response:
#                 if response.status == 200:
#                     result = await response.json()
#                     self.auth_token = result.get('token')
#                     return [TextContent(
#                         type="text",
#                         text=f"Login successful for {username}. Token obtained."
#                     )]
#                 else:
#                     return [TextContent(
#                         type="text",
#                         text=f"Login failed: HTTP {response.status}"
#                     )]

#         except Exception as e:
#             return [TextContent(type="text", text=f"Login request failed: {str(e)}")]

#     async def _handle_get_balance(self, args: Dict[str, Any]) -> List[TextContent]:
#         """Handle balance request"""
#         if not self.auth_token:
#             return [TextContent(type="text", text="Error: Not authenticated. Please login first.")]

#         account_id = args["account_id"]
#         headers = {'Authorization': f'Bearer {self.auth_token}'}

#         try:
#             async with self.session.get(
#                 f"{self.base_url}/balances/{account_id}",
#                 headers=headers
#             ) as response:
#                 if response.status == 200:
#                     balance_data = await response.json()
#                     return [TextContent(
#                         type="text",
#                         text=f"Balance for account {account_id}: {json.dumps(balance_data, indent=2)}"
#                     )]
#                 else:
#                     return [TextContent(
#                         type="text",
#                         text=f"Failed to get balance: HTTP {response.status}"
#                     )]

#         except Exception as e:
#             return [TextContent(type="text", text=f"Balance request failed: {str(e)}")]

#     async def _handle_get_transactions(self, args: Dict[str, Any]) -> List[TextContent]:
#         """Handle transaction history request"""
#         if not self.auth_token:
#             return [TextContent(type="text", text="Error: Not authenticated. Please login first.")]

#         account_id = args["account_id"]
#         headers = {'Authorization': f'Bearer {self.auth_token}'}

#         try:
#             async with self.session.get(
#                 f"{self.base_url}/transactions/{account_id}",
#                 headers=headers
#             ) as response:
#                 if response.status == 200:
#                     transactions = await response.json()
#                     limit = args.get("limit", 10)
#                     limited_transactions = transactions[:limit] if isinstance(transactions, list) else transactions
                    
#                     return [TextContent(
#                         type="text",
#                         text=f"Transactions for account {account_id}:\n{json.dumps(limited_transactions, indent=2)}"
#                     )]
#                 else:
#                     return [TextContent(
#                         type="text",
#                         text=f"Failed to get transactions: HTTP {response.status}"
#                     )]

#         except Exception as e:
#             return [TextContent(type="text", text=f"Transaction request failed: {str(e)}")]

#     async def _handle_send_payment(self, args: Dict[str, Any]) -> List[TextContent]:
#         """Handle payment request"""
#         if not self.auth_token:
#             return [TextContent(type="text", text="Error: Not authenticated. Please login first.")]

#         headers = {
#             'Authorization': f'Bearer {self.auth_token}',
#             'Content-Type': 'application/x-www-form-urlencoded'
#         }

#         # Generate a simple UUID for the transaction
#         import uuid
#         transaction_uuid = str(uuid.uuid4())

#         form_data = {
#             'account_num': args["to_account"],
#             'amount': args["amount"],
#             'uuid': transaction_uuid
#         }

#         if args.get("label"):
#             form_data['contact_label'] = args["label"]

#         try:
#             async with self.session.post(
#                 f"{self.base_url}/payment",
#                 data=form_data,
#                 headers=headers,
#                 allow_redirects=False
#             ) as response:
#                 if response.status in [200, 303]:  # 303 is redirect on success
#                     return [TextContent(
#                         type="text",
#                         text=f"Payment of ${args['amount']} sent to account {args['to_account']} successfully. Transaction ID: {transaction_uuid}"
#                     )]
#                 else:
#                     response_text = await response.text()
#                     return [TextContent(
#                         type="text",
#                         text=f"Payment failed: HTTP {response.status} - {response_text}"
#                     )]

#         except Exception as e:
#             return [TextContent(type="text", text=f"Payment request failed: {str(e)}")]

#     async def _handle_deposit(self, args: Dict[str, Any]) -> List[TextContent]:
#         """Handle deposit request"""
#         if not self.auth_token:
#             return [TextContent(type="text", text="Error: Not authenticated. Please login first.")]

#         headers = {
#             'Authorization': f'Bearer {self.auth_token}',
#             'Content-Type': 'application/x-www-form-urlencoded'
#         }

#         import uuid
#         transaction_uuid = str(uuid.uuid4())

#         form_data = {
#             'account': 'add',
#             'external_account_num': args["external_account"],
#             'external_routing_num': args["external_routing"],
#             'amount': args["amount"],
#             'uuid': transaction_uuid
#         }

#         if args.get("label"):
#             form_data['external_label'] = args["label"]

#         try:
#             async with self.session.post(
#                 f"{self.base_url}/deposit",
#                 data=form_data,
#                 headers=headers,
#                 allow_redirects=False
#             ) as response:
#                 if response.status in [200, 303]:
#                     return [TextContent(
#                         type="text",
#                         text=f"Deposit of ${args['amount']} from external account {args['external_account']} successful. Transaction ID: {transaction_uuid}"
#                     )]
#                 else:
#                     response_text = await response.text()
#                     return [TextContent(
#                         type="text",
#                         text=f"Deposit failed: HTTP {response.status} - {response_text}"
#                     )]

#         except Exception as e:
#             return [TextContent(type="text", text=f"Deposit request failed: {str(e)}")]

#     async def _handle_get_contacts(self, args: Dict[str, Any]) -> List[TextContent]:
#         """Handle get contacts request"""
#         if not self.auth_token:
#             return [TextContent(type="text", text="Error: Not authenticated. Please login first.")]

#         username = args["username"]
#         headers = {'Authorization': f'Bearer {self.auth_token}'}

#         try:
#             async with self.session.get(
#                 f"{self.base_url}/contacts/{username}",
#                 headers=headers
#             ) as response:
#                 if response.status == 200:
#                     contacts = await response.json()
#                     return [TextContent(
#                         type="text",
#                         text=f"Contacts for {username}:\n{json.dumps(contacts, indent=2)}"
#                     )]
#                 else:
#                     return [TextContent(
#                         type="text",
#                         text=f"Failed to get contacts: HTTP {response.status}"
#                     )]

#         except Exception as e:
#             return [TextContent(type="text", text=f"Get contacts request failed: {str(e)}")]

#     async def _handle_add_contact(self, args: Dict[str, Any]) -> List[TextContent]:
#         """Handle add contact request"""
#         if not self.auth_token:
#             return [TextContent(type="text", text="Error: Not authenticated. Please login first.")]

#         username = args["username"]
#         headers = {
#             'Authorization': f'Bearer {self.auth_token}',
#             'Content-Type': 'application/json'
#         }

#         contact_data = {
#             'label': args["label"],
#             'account_num': args["account_num"],
#             'routing_num': args["routing_num"],
#             'is_external': args.get("is_external", False)
#         }

#         try:
#             async with self.session.post(
#                 f"{self.base_url}/contacts/{username}",
#                 json=contact_data,
#                 headers=headers
#             ) as response:
#                 if response.status in [200, 201]:
#                     return [TextContent(
#                         type="text",
#                         text=f"Contact '{args['label']}' added successfully for {username}"
#                     )]
#                 else:
#                     response_text = await response.text()
#                     return [TextContent(
#                         type="text",
#                         text=f"Failed to add contact: HTTP {response.status} - {response_text}"
#                     )]

#         except Exception as e:
#             return [TextContent(type="text", text=f"Add contact request failed: {str(e)}")]

#     async def _handle_create_user(self, args: Dict[str, Any]) -> List[TextContent]:
#         """Handle create user request"""
#         headers = {'Content-Type': 'application/x-www-form-urlencoded'}

#         try:
#             async with self.session.post(
#                 f"{self.base_url}/users",
#                 data=args,
#                 headers=headers
#             ) as response:
#                 if response.status == 201:
#                     return [TextContent(
#                         type="text",
#                         text=f"User '{args['username']}' created successfully"
#                     )]
#                 else:
#                     response_text = await response.text()
#                     return [TextContent(
#                         type="text",
#                         text=f"Failed to create user: HTTP {response.status} - {response_text}"
#                     )]

#         except Exception as e:
#             return [TextContent(type="text", text=f"Create user request failed: {str(e)}")]

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
#                             "name": "bank-anthos-mcp-server",
#                             "version": "0.1.0",
#                         },
#                     ),
#                 )
#         finally:
#             await self.cleanup_session()

# async def main():
#     """Main entry point"""
#     import os
#     base_url = os.getenv("BANK_ANTHOS_URL", "http://localhost:8080")
#     server = BankAnthosMCPServer(base_url=base_url)
#     await server.run()

# if __name__ == "__main__":
#     asyncio.run(main())


# #!/usr/bin/env python3
# """
# Bank of Anthos MCP Server
# Provides tools for interacting with Google Cloud's Bank of Anthos demo application
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
# logger = logging.getLogger("bank-anthos-mcp-server")

# class BankAnthosMCPServer:
#     def __init__(self, base_url="http://localhost:8080"):
#         self.server = Server("bank-anthos-mcp-server")
#         self.session: Optional[aiohttp.ClientSession] = None
#         self.base_url = base_url
#         self.auth_token = None
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
#             """Return available Bank of Anthos tools"""
#             return [
#                 Tool(
#                     name="bank_login",
#                     description="Login to Bank of Anthos and get authentication token",
#                     inputSchema={
#                         "type": "object",
#                         "properties": {
#                             "username": {
#                                 "type": "string",
#                                 "description": "Username for login"
#                             },
#                             "password": {
#                                 "type": "string",
#                                 "description": "Password for login"
#                             }
#                         },
#                         "required": ["username", "password"]
#                     }
#                 ),
#                 Tool(
#                     name="bank_get_balance",
#                     description="Get account balance for authenticated user",
#                     inputSchema={
#                         "type": "object",
#                         "properties": {
#                             "account_id": {
#                                 "type": "string",
#                                 "description": "Account ID to check balance for"
#                             }
#                         },
#                         "required": ["account_id"]
#                     }
#                 ),
#                 Tool(
#                     name="bank_get_transactions",
#                     description="Get transaction history for an account",
#                     inputSchema={
#                         "type": "object",
#                         "properties": {
#                             "account_id": {
#                                 "type": "string",
#                                 "description": "Account ID to get transactions for"
#                             },
#                             "limit": {
#                                 "type": "integer",
#                                 "description": "Limit number of transactions returned",
#                                 "default": 10
#                             }
#                         },
#                         "required": ["account_id"]
#                     }
#                 ),
#                 Tool(
#                     name="bank_send_payment",
#                     description="Send payment to another account",
#                     inputSchema={
#                         "type": "object",
#                         "properties": {
#                             "to_account": {
#                                 "type": "string",
#                                 "description": "Recipient account number"
#                             },
#                             "amount": {
#                                 "type": "string",
#                                 "description": "Amount to send (e.g., '100.50')"
#                             },
#                             "label": {
#                                 "type": "string",
#                                 "description": "Optional label for the payment",
#                                 "default": ""
#                             }
#                         },
#                         "required": ["to_account", "amount"]
#                     }
#                 ),
#                 Tool(
#                     name="bank_deposit",
#                     description="Deposit money from external account",
#                     inputSchema={
#                         "type": "object",
#                         "properties": {
#                             "external_account": {
#                                 "type": "string",
#                                 "description": "External account number"
#                             },
#                             "external_routing": {
#                                 "type": "string",
#                                 "description": "External routing number"
#                             },
#                             "amount": {
#                                 "type": "string",
#                                 "description": "Amount to deposit (e.g., '100.50')"
#                             },
#                             "label": {
#                                 "type": "string",
#                                 "description": "Optional label for external account",
#                                 "default": ""
#                             }
#                         },
#                         "required": ["external_account", "external_routing", "amount"]
#                     }
#                 ),
#                 Tool(
#                     name="bank_get_contacts",
#                     description="Get user's contact list",
#                     inputSchema={
#                         "type": "object",
#                         "properties": {
#                             "username": {
#                                 "type": "string",
#                                 "description": "Username to get contacts for"
#                             }
#                         },
#                         "required": ["username"]
#                     }
#                 ),
#                 Tool(
#                     name="bank_add_contact",
#                     description="Add a new contact to user's contact list",
#                     inputSchema={
#                         "type": "object",
#                         "properties": {
#                             "username": {
#                                 "type": "string",
#                                 "description": "Username to add contact for"
#                             },
#                             "label": {
#                                 "type": "string",
#                                 "description": "Contact label/name"
#                             },
#                             "account_num": {
#                                 "type": "string",
#                                 "description": "Contact's account number"
#                             },
#                             "routing_num": {
#                                 "type": "string",
#                                 "description": "Contact's routing number"
#                             },
#                             "is_external": {
#                                 "type": "boolean",
#                                 "description": "Whether this is an external account",
#                                 "default": False
#                             }
#                         },
#                         "required": ["username", "label", "account_num", "routing_num"]
#                     }
#                 ),
#                 Tool(
#                     name="bank_create_user",
#                     description="Create a new user account",
#                     inputSchema={
#                         "type": "object",
#                         "properties": {
#                             "username": {
#                                 "type": "string",
#                                 "description": "Desired username"
#                             },
#                             "password": {
#                                 "type": "string",
#                                 "description": "Password for the account"
#                             },
#                             "password-repeat": {
#                                 "type": "string",
#                                 "description": "Password confirmation"
#                             },
#                             "firstname": {
#                                 "type": "string",
#                                 "description": "First name"
#                             },
#                             "lastname": {
#                                 "type": "string",
#                                 "description": "Last name"
#                             },
#                             "birthday": {
#                                 "type": "string",
#                                 "description": "Birthday in YYYY-MM-DD format"
#                             },
#                             "timezone": {
#                                 "type": "string",
#                                 "description": "Timezone (e.g., 'America/New_York')"
#                             },
#                             "address": {
#                                 "type": "string",
#                                 "description": "Street address"
#                             },
#                             "state": {
#                                 "type": "string",
#                                 "description": "State"
#                             },
#                             "zip": {
#                                 "type": "string",
#                                 "description": "ZIP code"
#                             },
#                             "ssn": {
#                                 "type": "string",
#                                 "description": "Social Security Number"
#                             }
#                         },
#                         "required": ["username", "password", "password-repeat", "firstname", "lastname", "birthday", "timezone", "address", "state", "zip", "ssn"]
#                     }
#                 )
#             ]

#         @self.server.call_tool()
#         async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
#             """Handle tool calls"""
#             try:
#                 await self.ensure_session()

#                 if name == "bank_login":
#                     return await self._handle_login(arguments)
#                 elif name == "bank_get_balance":
#                     return await self._handle_get_balance(arguments)
#                 elif name == "bank_get_transactions":
#                     return await self._handle_get_transactions(arguments)
#                 elif name == "bank_send_payment":
#                     return await self._handle_send_payment(arguments)
#                 elif name == "bank_deposit":
#                     return await self._handle_deposit(arguments)
#                 elif name == "bank_get_contacts":
#                     return await self._handle_get_contacts(arguments)
#                 elif name == "bank_add_contact":
#                     return await self._handle_add_contact(arguments)
#                 elif name == "bank_create_user":
#                     return await self._handle_create_user(arguments)
#                 else:
#                     return [TextContent(type="text", text=f"Unknown tool: {name}")]

#             except Exception as e:
#                 logger.error(f"Error in tool {name}: {e}")
#                 return [TextContent(type="text", text=f"Error: {str(e)}")]

#     async def _handle_login(self, args: Dict[str, Any]) -> List[TextContent]:
#         """Handle login request"""
#         username = args["username"]
#         password = args["password"]

#         try:
#             params = {
#                 'username': username,
#                 'password': password
#             }
            
#             async with self.session.get(
#                 f"{self.base_url}/login",
#                 params=params
#             ) as response:
#                 if response.status == 200:
#                     result = await response.json()
#                     self.auth_token = result.get('token')
#                     return [TextContent(
#                         type="text",
#                         text=f"Login successful for {username}. Token obtained."
#                     )]
#                 else:
#                     return [TextContent(
#                         type="text",
#                         text=f"Login failed: HTTP {response.status}"
#                     )]

#         except Exception as e:
#             return [TextContent(type="text", text=f"Login request failed: {str(e)}")]

#     async def _handle_get_balance(self, args: Dict[str, Any]) -> List[TextContent]:
#         """Handle balance request"""
#         if not self.auth_token:
#             return [TextContent(type="text", text="Error: Not authenticated. Please login first.")]

#         account_id = args["account_id"]
#         headers = {'Authorization': f'Bearer {self.auth_token}'}

#         try:
#             async with self.session.get(
#                 f"{self.base_url}/balances/{account_id}",
#                 headers=headers
#             ) as response:
#                 if response.status == 200:
#                     balance_data = await response.json()
#                     return [TextContent(
#                         type="text",
#                         text=f"Balance for account {account_id}: {json.dumps(balance_data, indent=2)}"
#                     )]
#                 else:
#                     return [TextContent(
#                         type="text",
#                         text=f"Failed to get balance: HTTP {response.status}"
#                     )]

#         except Exception as e:
#             return [TextContent(type="text", text=f"Balance request failed: {str(e)}")]

#     async def _handle_get_transactions(self, args: Dict[str, Any]) -> List[TextContent]:
#         """Handle transaction history request"""
#         if not self.auth_token:
#             return [TextContent(type="text", text="Error: Not authenticated. Please login first.")]

#         account_id = args["account_id"]
#         headers = {'Authorization': f'Bearer {self.auth_token}'}

#         try:
#             async with self.session.get(
#                 f"{self.base_url}/transactions/{account_id}",
#                 headers=headers
#             ) as response:
#                 if response.status == 200:
#                     transactions = await response.json()
#                     limit = args.get("limit", 10)
#                     limited_transactions = transactions[:limit] if isinstance(transactions, list) else transactions
                    
#                     return [TextContent(
#                         type="text",
#                         text=f"Transactions for account {account_id}:\n{json.dumps(limited_transactions, indent=2)}"
#                     )]
#                 else:
#                     return [TextContent(
#                         type="text",
#                         text=f"Failed to get transactions: HTTP {response.status}"
#                     )]

#         except Exception as e:
#             return [TextContent(type="text", text=f"Transaction request failed: {str(e)}")]

#     async def _handle_send_payment(self, args: Dict[str, Any]) -> List[TextContent]:
#         """Handle payment request"""
#         if not self.auth_token:
#             return [TextContent(type="text", text="Error: Not authenticated. Please login first.")]

#         headers = {
#             'Authorization': f'Bearer {self.auth_token}',
#             'Content-Type': 'application/x-www-form-urlencoded'
#         }

#         # Generate a simple UUID for the transaction
#         import uuid
#         transaction_uuid = str(uuid.uuid4())

#         form_data = {
#             'account_num': args["to_account"],
#             'amount': args["amount"],
#             'uuid': transaction_uuid
#         }

#         if args.get("label"):
#             form_data['contact_label'] = args["label"]

#         try:
#             async with self.session.post(
#                 f"{self.base_url}/payment",
#                 data=form_data,
#                 headers=headers,
#                 allow_redirects=False
#             ) as response:
#                 if response.status in [200, 303]:  # 303 is redirect on success
#                     return [TextContent(
#                         type="text",
#                         text=f"Payment of ${args['amount']} sent to account {args['to_account']} successfully. Transaction ID: {transaction_uuid}"
#                     )]
#                 else:
#                     response_text = await response.text()
#                     return [TextContent(
#                         type="text",
#                         text=f"Payment failed: HTTP {response.status} - {response_text}"
#                     )]

#         except Exception as e:
#             return [TextContent(type="text", text=f"Payment request failed: {str(e)}")]

#     async def _handle_deposit(self, args: Dict[str, Any]) -> List[TextContent]:
#         """Handle deposit request"""
#         if not self.auth_token:
#             return [TextContent(type="text", text="Error: Not authenticated. Please login first.")]

#         headers = {
#             'Authorization': f'Bearer {self.auth_token}',
#             'Content-Type': 'application/x-www-form-urlencoded'
#         }

#         import uuid
#         transaction_uuid = str(uuid.uuid4())

#         form_data = {
#             'account': 'add',
#             'external_account_num': args["external_account"],
#             'external_routing_num': args["external_routing"],
#             'amount': args["amount"],
#             'uuid': transaction_uuid
#         }

#         if args.get("label"):
#             form_data['external_label'] = args["label"]

#         try:
#             async with self.session.post(
#                 f"{self.base_url}/deposit",
#                 data=form_data,
#                 headers=headers,
#                 allow_redirects=False
#             ) as response:
#                 if response.status in [200, 303]:
#                     return [TextContent(
#                         type="text",
#                         text=f"Deposit of ${args['amount']} from external account {args['external_account']} successful. Transaction ID: {transaction_uuid}"
#                     )]
#                 else:
#                     response_text = await response.text()
#                     return [TextContent(
#                         type="text",
#                         text=f"Deposit failed: HTTP {response.status} - {response_text}"
#                     )]

#         except Exception as e:
#             return [TextContent(type="text", text=f"Deposit request failed: {str(e)}")]

#     async def _handle_get_contacts(self, args: Dict[str, Any]) -> List[TextContent]:
#         """Handle get contacts request"""
#         if not self.auth_token:
#             return [TextContent(type="text", text="Error: Not authenticated. Please login first.")]

#         username = args["username"]
#         headers = {'Authorization': f'Bearer {self.auth_token}'}

#         try:
#             async with self.session.get(
#                 f"{self.base_url}/contacts/{username}",
#                 headers=headers
#             ) as response:
#                 if response.status == 200:
#                     contacts = await response.json()
#                     return [TextContent(
#                         type="text",
#                         text=f"Contacts for {username}:\n{json.dumps(contacts, indent=2)}"
#                     )]
#                 else:
#                     return [TextContent(
#                         type="text",
#                         text=f"Failed to get contacts: HTTP {response.status}"
#                     )]

#         except Exception as e:
#             return [TextContent(type="text", text=f"Get contacts request failed: {str(e)}")]

#     async def _handle_add_contact(self, args: Dict[str, Any]) -> List[TextContent]:
#         """Handle add contact request"""
#         if not self.auth_token:
#             return [TextContent(type="text", text="Error: Not authenticated. Please login first.")]

#         username = args["username"]
#         headers = {
#             'Authorization': f'Bearer {self.auth_token}',
#             'Content-Type': 'application/json'
#         }

#         contact_data = {
#             'label': args["label"],
#             'account_num': args["account_num"],
#             'routing_num': args["routing_num"],
#             'is_external': args.get("is_external", False)
#         }

#         try:
#             async with self.session.post(
#                 f"{self.base_url}/contacts/{username}",
#                 json=contact_data,
#                 headers=headers
#             ) as response:
#                 if response.status in [200, 201]:
#                     return [TextContent(
#                         type="text",
#                         text=f"Contact '{args['label']}' added successfully for {username}"
#                     )]
#                 else:
#                     response_text = await response.text()
#                     return [TextContent(
#                         type="text",
#                         text=f"Failed to add contact: HTTP {response.status} - {response_text}"
#                     )]

#         except Exception as e:
#             return [TextContent(type="text", text=f"Add contact request failed: {str(e)}")]

#     async def _handle_create_user(self, args: Dict[str, Any]) -> List[TextContent]:
#         """Handle create user request"""
#         headers = {'Content-Type': 'application/x-www-form-urlencoded'}

#         try:
#             async with self.session.post(
#                 f"{self.base_url}/users",
#                 data=args,
#                 headers=headers
#             ) as response:
#                 if response.status == 201:
#                     return [TextContent(
#                         type="text",
#                         text=f"User '{args['username']}' created successfully"
#                     )]
#                 else:
#                     response_text = await response.text()
#                     return [TextContent(
#                         type="text",
#                         text=f"Failed to create user: HTTP {response.status} - {response_text}"
#                     )]

#         except Exception as e:
#             return [TextContent(type="text", text=f"Create user request failed: {str(e)}")]

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
#                             "name": "bank-anthos-mcp-server",
#                             "version": "0.1.0",
#                         },
#                     ),
#                 )
#         finally:
#             await self.cleanup_session()

# async def main():
#     """Main entry point"""
#     import os
#     base_url = os.getenv("BANK_ANTHOS_URL", "http://localhost:8080")
#     server = BankAnthosMCPServer(base_url=base_url)
#     await server.run()

# if __name__ == "__main__":
#     asyncio.run(main())

#!/usr/bin/env python3
"""
Bank of Anthos MCP Server
Provides tools for interacting with Google Cloud's Bank of Anthos demo application
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
logger = logging.getLogger("bank-anthos-mcp-server")

class BankAnthosMCPServer:
    def __init__(self, base_url="http://localhost:8080"):
        self.server = Server("bank-anthos-mcp-server")
        self.session: Optional[aiohttp.ClientSession] = None
        self.base_url = base_url
        self.auth_token = None
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
            """Return available Bank of Anthos tools"""
            return [
                Tool(
                    name="bank_login",
                    description="Login to Bank of Anthos and get authentication token",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "username": {
                                "type": "string",
                                "description": "Username for login"
                            },
                            "password": {
                                "type": "string",
                                "description": "Password for login"
                            }
                        },
                        "required": ["username", "password"]
                    }
                ),
                Tool(
                    name="bank_get_balance",
                    description="Get account balance for authenticated user",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "account_id": {
                                "type": "string",
                                "description": "Account ID to check balance for"
                            }
                        },
                        "required": ["account_id"]
                    }
                ),
                Tool(
                    name="bank_get_transactions",
                    description="Get transaction history for an account",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "account_id": {
                                "type": "string",
                                "description": "Account ID to get transactions for"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Limit number of transactions returned",
                                "default": 10
                            }
                        },
                        "required": ["account_id"]
                    }
                ),
                Tool(
                    name="bank_send_payment",
                    description="Send payment to another account",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "to_account": {
                                "type": "string",
                                "description": "Recipient account number"
                            },
                            "amount": {
                                "type": "string",
                                "description": "Amount to send (e.g., '100.50')"
                            },
                            "label": {
                                "type": "string",
                                "description": "Optional label for the payment",
                                "default": ""
                            }
                        },
                        "required": ["to_account", "amount"]
                    }
                ),
                Tool(
                    name="bank_deposit",
                    description="Deposit money from external account",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "external_account": {
                                "type": "string",
                                "description": "External account number"
                            },
                            "external_routing": {
                                "type": "string",
                                "description": "External routing number"
                            },
                            "amount": {
                                "type": "string",
                                "description": "Amount to deposit (e.g., '100.50')"
                            },
                            "label": {
                                "type": "string",
                                "description": "Optional label for external account",
                                "default": ""
                            }
                        },
                        "required": ["external_account", "external_routing", "amount"]
                    }
                ),
                Tool(
                    name="bank_get_contacts",
                    description="Get user's contact list",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "username": {
                                "type": "string",
                                "description": "Username to get contacts for"
                            }
                        },
                        "required": ["username"]
                    }
                ),
                Tool(
                    name="bank_add_contact",
                    description="Add a new contact to user's contact list",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "username": {
                                "type": "string",
                                "description": "Username to add contact for"
                            },
                            "label": {
                                "type": "string",
                                "description": "Contact label/name"
                            },
                            "account_num": {
                                "type": "string",
                                "description": "Contact's account number"
                            },
                            "routing_num": {
                                "type": "string",
                                "description": "Contact's routing number"
                            },
                            "is_external": {
                                "type": "boolean",
                                "description": "Whether this is an external account",
                                "default": False
                            }
                        },
                        "required": ["username", "label", "account_num", "routing_num"]
                    }
                ),
                Tool(
                    name="bank_create_user",
                    description="Create a new user account",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "username": {
                                "type": "string",
                                "description": "Desired username"
                            },
                            "password": {
                                "type": "string",
                                "description": "Password for the account"
                            },
                            "password-repeat": {
                                "type": "string",
                                "description": "Password confirmation"
                            },
                            "firstname": {
                                "type": "string",
                                "description": "First name"
                            },
                            "lastname": {
                                "type": "string",
                                "description": "Last name"
                            },
                            "birthday": {
                                "type": "string",
                                "description": "Birthday in YYYY-MM-DD format"
                            },
                            "timezone": {
                                "type": "string",
                                "description": "Timezone (e.g., 'America/New_York')"
                            },
                            "address": {
                                "type": "string",
                                "description": "Street address"
                            },
                            "state": {
                                "type": "string",
                                "description": "State"
                            },
                            "zip": {
                                "type": "string",
                                "description": "ZIP code"
                            },
                            "ssn": {
                                "type": "string",
                                "description": "Social Security Number"
                            }
                        },
                        "required": ["username", "password", "password-repeat", "firstname", "lastname", "birthday", "timezone", "address", "state", "zip", "ssn"]
                    }
                )
            ]

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Handle tool calls"""
            try:
                await self.ensure_session()

                if name == "bank_login":
                    return await self._handle_login(arguments)
                elif name == "bank_get_balance":
                    return await self._handle_get_balance(arguments)
                elif name == "bank_get_transactions":
                    return await self._handle_get_transactions(arguments)
                elif name == "bank_send_payment":
                    return await self._handle_send_payment(arguments)
                elif name == "bank_deposit":
                    return await self._handle_deposit(arguments)
                elif name == "bank_get_contacts":
                    return await self._handle_get_contacts(arguments)
                elif name == "bank_add_contact":
                    return await self._handle_add_contact(arguments)
                elif name == "bank_create_user":
                    return await self._handle_create_user(arguments)
                else:
                    return [TextContent(type="text", text=f"Unknown tool: {name}")]

            except Exception as e:
                logger.error(f"Error in tool {name}: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]

    async def _handle_login(self, args: Dict[str, Any]) -> List[TextContent]:
        """Handle login request"""
        username = args["username"]
        password = args["password"]

        try:
            params = {
                'username': username,
                'password': password
            }
            
            async with self.session.get(
                f"{self.base_url}/login",
                params=params
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    self.auth_token = result.get('token')
                    return [TextContent(
                        type="text",
                        text=f"Login successful for {username}. Token obtained."
                    )]
                else:
                    return [TextContent(
                        type="text",
                        text=f"Login failed: HTTP {response.status}"
                    )]

        except Exception as e:
            return [TextContent(type="text", text=f"Login request failed: {str(e)}")]

    async def _handle_get_balance(self, args: Dict[str, Any]) -> List[TextContent]:
        """Handle balance request"""
        if not self.auth_token:
            return [TextContent(type="text", text="Error: Not authenticated. Please login first.")]

        account_id = args["account_id"]
        headers = {'Authorization': f'Bearer {self.auth_token}'}

        try:
            async with self.session.get(
                f"{self.base_url}/balances/{account_id}",
                headers=headers
            ) as response:
                if response.status == 200:
                    balance_data = await response.json()
                    return [TextContent(
                        type="text",
                        text=f"Balance for account {account_id}: {json.dumps(balance_data, indent=2)}"
                    )]
                else:
                    return [TextContent(
                        type="text",
                        text=f"Failed to get balance: HTTP {response.status}"
                    )]

        except Exception as e:
            return [TextContent(type="text", text=f"Balance request failed: {str(e)}")]

    async def _handle_get_transactions(self, args: Dict[str, Any]) -> List[TextContent]:
        """Handle transaction history request"""
        if not self.auth_token:
            return [TextContent(type="text", text="Error: Not authenticated. Please login first.")]

        account_id = args["account_id"]
        headers = {'Authorization': f'Bearer {self.auth_token}'}

        try:
            async with self.session.get(
                f"{self.base_url}/transactions/{account_id}",
                headers=headers
            ) as response:
                if response.status == 200:
                    transactions = await response.json()
                    limit = args.get("limit", 10)
                    limited_transactions = transactions[:limit] if isinstance(transactions, list) else transactions
                    
                    return [TextContent(
                        type="text",
                        text=f"Transactions for account {account_id}:\n{json.dumps(limited_transactions, indent=2)}"
                    )]
                else:
                    return [TextContent(
                        type="text",
                        text=f"Failed to get transactions: HTTP {response.status}"
                    )]

        except Exception as e:
            return [TextContent(type="text", text=f"Transaction request failed: {str(e)}")]

    async def _handle_send_payment(self, args: Dict[str, Any]) -> List[TextContent]:
        """Handle payment request"""
        if not self.auth_token:
            return [TextContent(type="text", text="Error: Not authenticated. Please login first.")]

        headers = {
            'Authorization': f'Bearer {self.auth_token}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        # Generate a simple UUID for the transaction
        import uuid
        transaction_uuid = str(uuid.uuid4())

        form_data = {
            'account_num': args["to_account"],
            'amount': args["amount"],
            'uuid': transaction_uuid
        }

        if args.get("label"):
            form_data['contact_label'] = args["label"]

        try:
            async with self.session.post(
                f"{self.base_url}/payment",
                data=form_data,
                headers=headers,
                allow_redirects=False
            ) as response:
                if response.status in [200, 303]:  # 303 is redirect on success
                    return [TextContent(
                        type="text",
                        text=f"Payment of ${args['amount']} sent to account {args['to_account']} successfully. Transaction ID: {transaction_uuid}"
                    )]
                else:
                    response_text = await response.text()
                    return [TextContent(
                        type="text",
                        text=f"Payment failed: HTTP {response.status} - {response_text}"
                    )]

        except Exception as e:
            return [TextContent(type="text", text=f"Payment request failed: {str(e)}")]

    async def _handle_deposit(self, args: Dict[str, Any]) -> List[TextContent]:
        """Handle deposit request"""
        if not self.auth_token:
            return [TextContent(type="text", text="Error: Not authenticated. Please login first.")]

        headers = {
            'Authorization': f'Bearer {self.auth_token}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        import uuid
        transaction_uuid = str(uuid.uuid4())

        form_data = {
            'account': 'add',
            'external_account_num': args["external_account"],
            'external_routing_num': args["external_routing"],
            'amount': args["amount"],
            'uuid': transaction_uuid
        }

        if args.get("label"):
            form_data['external_label'] = args["label"]

        try:
            async with self.session.post(
                f"{self.base_url}/deposit",
                data=form_data,
                headers=headers,
                allow_redirects=False
            ) as response:
                if response.status in [200, 303]:
                    return [TextContent(
                        type="text",
                        text=f"Deposit of ${args['amount']} from external account {args['external_account']} successful. Transaction ID: {transaction_uuid}"
                    )]
                else:
                    response_text = await response.text()
                    return [TextContent(
                        type="text",
                        text=f"Deposit failed: HTTP {response.status} - {response_text}"
                    )]

        except Exception as e:
            return [TextContent(type="text", text=f"Deposit request failed: {str(e)}")]

    async def _handle_get_contacts(self, args: Dict[str, Any]) -> List[TextContent]:
        """Handle get contacts request"""
        if not self.auth_token:
            return [TextContent(type="text", text="Error: Not authenticated. Please login first.")]

        username = args["username"]
        headers = {'Authorization': f'Bearer {self.auth_token}'}

        try:
            async with self.session.get(
                f"{self.base_url}/contacts/{username}",
                headers=headers
            ) as response:
                if response.status == 200:
                    contacts = await response.json()
                    return [TextContent(
                        type="text",
                        text=f"Contacts for {username}:\n{json.dumps(contacts, indent=2)}"
                    )]
                else:
                    return [TextContent(
                        type="text",
                        text=f"Failed to get contacts: HTTP {response.status}"
                    )]

        except Exception as e:
            return [TextContent(type="text", text=f"Get contacts request failed: {str(e)}")]

    async def _handle_add_contact(self, args: Dict[str, Any]) -> List[TextContent]:
        """Handle add contact request"""
        if not self.auth_token:
            return [TextContent(type="text", text="Error: Not authenticated. Please login first.")]

        username = args["username"]
        headers = {
            'Authorization': f'Bearer {self.auth_token}',
            'Content-Type': 'application/json'
        }

        contact_data = {
            'label': args["label"],
            'account_num': args["account_num"],
            'routing_num': args["routing_num"],
            'is_external': args.get("is_external", False)
        }

        try:
            async with self.session.post(
                f"{self.base_url}/contacts/{username}",
                json=contact_data,
                headers=headers
            ) as response:
                if response.status in [200, 201]:
                    return [TextContent(
                        type="text",
                        text=f"Contact '{args['label']}' added successfully for {username}"
                    )]
                else:
                    response_text = await response.text()
                    return [TextContent(
                        type="text",
                        text=f"Failed to add contact: HTTP {response.status} - {response_text}"
                    )]

        except Exception as e:
            return [TextContent(type="text", text=f"Add contact request failed: {str(e)}")]

    async def _handle_create_user(self, args: Dict[str, Any]) -> List[TextContent]:
        """Handle create user request"""
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        try:
            async with self.session.post(
                f"{self.base_url}/users",
                data=args,
                headers=headers
            ) as response:
                if response.status == 201:
                    return [TextContent(
                        type="text",
                        text=f"User '{args['username']}' created successfully"
                    )]
                else:
                    response_text = await response.text()
                    return [TextContent(
                        type="text",
                        text=f"Failed to create user: HTTP {response.status} - {response_text}"
                    )]

        except Exception as e:
            return [TextContent(type="text", text=f"Create user request failed: {str(e)}")]

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
    import os
    base_url = os.getenv("BANK_ANTHOS_URL", "http://localhost:8080")
    server = BankAnthosMCPServer(base_url=base_url)
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())