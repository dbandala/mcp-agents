import chainlit as cl
from mcp import ClientSession

@cl.on_mcp_connect
async def on_mcp_connect(connection, session: ClientSession):
    """Called when an MCP connection is established"""
    # Your connection initialization code here
    # This handler is required for MCP to work

@cl.on_mcp_disconnect
async def on_mcp_disconnect(name: str, session: ClientSession):
    """Called when an MCP connection is terminated"""
    # Optional handler: Cleanup your code here