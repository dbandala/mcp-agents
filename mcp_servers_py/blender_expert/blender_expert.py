## This is a blender expert agent that can assist with Blender-related tasks.
# these functions are exposed trhough mcp.resource decorators and can be called
# by a client using the official MCP layer protocol.

import os
import json
from typing import List
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from openai import OpenAI

from tools.parser import parse_command
from tools.knowledge_base import query_vector_db_codebase, query_vector_db_manual, query_vector_db_examples
from tools.web_resources import scrape_static_page

# Load environment variables from .env file
load_dotenv()

# initialize FastMCP server
mcp = FastMCP("blender-expert")


# tool for retrieving Blender code base information
@mcp.tool(
    name="get_blender_codebase",
    description="Retrieves information about Blender's main code base, written in C++. This tool can be used to understand how Blender works under the hood.",
    annotations=ToolAnnotations(parameters={ # type: ignore
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The query to search in the Blender code base."
            }
        },
        "required": ["query"],
        "additionalProperties": False
    }))
def get_blender_codebase(query: str) -> str:
    """
    Retrieves information about Blender's code base.
    Args:
        query: The query to search in the Blender code base.
    Returns:
        A string containing relevant information from the Blender code base.
    """
    # Validate the input query
    if not query:
        raise ValueError("The query cannot be empty.")
    
    # For simplicity, we return a static list of Blender commands and descriptions
    # In a real application, this would query a database or knowledge base
    codebase = query_vector_db_codebase(query)
    if not codebase:
        return "No relevant information found in the Blender code base for the given query."
    
    return codebase

# tool for retrieving Blender manual information
@mcp.tool(
    name="get_blender_api_reference",
    description="Retrieves information about Blender Python API documentation, including commands, their descriptions and how to use them effectively.",
    annotations=ToolAnnotations(parameters={ # type: ignore
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The query to search in the Blender Python API documentation."
            }
        },
        "required": ["query"],
        "additionalProperties": False
    }))
def get_blender_api_reference(query: str) -> str:
    """
    Retrieves information about Blender Python API documentation, including commands, their descriptions and how to use them.
    Args:
        query: The query to search in the Blender Python API documentation.
    Returns:
        A string containing relevant information from the Blender manual.
    """
    # Validate the input query
    if not query:
        raise ValueError("The query cannot be empty.")
    
    # query the vector database for Blender manual information
    api_reference = query_vector_db_manual(query)
    if not api_reference:
        return "No relevant information found in the Blender Python API documentation for the given query."
    
    return api_reference



# tool for retrieving Blender example scripts
@mcp.tool(
    name="get_blender_example_scripts",
    description="Retrieves example scripts for Blender Python API usage, including code snippets and explanations.",
    annotations=ToolAnnotations(parameters={  # type: ignore
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The query to search for relevant Blender example scripts."
            }
        },
        "required": ["query"],
        "additionalProperties": False
    }))
def get_blender_example_scripts(query: str) -> str:
    """
    Retrieves example scripts for Blender Python API usage.
    Args:
        query: The query to search for relevant Blender example scripts.
    Returns:
        A string containing relevant example scripts and explanations.
    """
    if not query:
        raise ValueError("The query cannot be empty.")

    # For demonstration, reuse the manual vector DB for example scripts
    # In a real application, this would query a dedicated example scripts database
    examples = query_vector_db_examples(query + " example script")
    if not examples:
        return "No relevant Blender example scripts found for the given query."

    return examples


# resource for getting an overview of the Blender Python API
@mcp.resource(
    uri="web:://python_api/overview",
    name="get_python_api_overview",
    description="Retrieves an overview of the Blender Python API, including its structure and key components.",
    mime_type="application/text"
)
def get_python_api_overview() -> str:
    """
    Retrieves an overview of the Blender Python API, including its structure and key components.
    Returns:
        A string containing the overview of the Blender Python API.
    """
    # Scrape the static page for the Blender Python API overview
    url = "https://docs.blender.org/api/current/info_overview.html"
    selector = "body"
    try:
        overview = scrape_static_page(url, selector)
        return "\n".join(overview)
    except Exception as e:
        return f"Error retrieving Blender Python API overview: {str(e)}"
    

# resource for getting an API reference usage page content
@mcp.resource(
    uri="web:://python_api/reference_usage",
    name="get_api_reference_usage",
    description="Retrieves the content of the Blender Python API reference usage page.",
    mime_type="application/text"
)
def get_api_reference_usage() -> str:
    """
    Retrieves the content of the Blender Python API reference usage page.
    Returns:
        A string containing the content of the Blender Python API reference usage page.
    """
    # Scrape the static
    url = "https://docs.blender.org/api/current/info_api_reference.html"
    selector = "body"
    try:
        usage_content = scrape_static_page(url, selector)
        return "\n".join(usage_content)
    except Exception as e:
        return f"Error retrieving Blender Python API reference usage content: {str(e)}"