from mcp.server.fastmcp import FastMCP

mcp = FastMCP("My App")

# Resources are how you expose data to LLMs. They're similar to GET endpoints in a REST API - they provide data but shouldn't perform significant computation or have side effects:
# They're defined with a URI template, and the LLM can request data from them using the URI.
# The URI template is a string that contains placeholders for the resource's parameters.
# The placeholders are enclosed in curly braces and are replaced with the actual values when the resource is requested.
# The resource function is a coroutine that returns the data for the resource.
# The resource function can be async.
# The resource function can return a string, a dictionary, or a list.
# The resource function can return a MCPMessage object.
@mcp.resource("config://app")
def get_config() -> str:
    """Static configuration data"""
    return "App configuration here"


@mcp.resource("users://{user_id}/profile")
def get_user_profile(user_id: str) -> str:
    """Dynamic user data"""
    return f"Profile data for user {user_id}"