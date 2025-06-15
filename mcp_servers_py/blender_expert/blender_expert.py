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
from tools.knowledge_base import query_vector_db_codebase, query_vector_db_manual

# Load environment variables from .env file
load_dotenv()

# initialize FastMCP server
mcp = FastMCP("blender_expert")

# llm client
llm_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)


# tool for retrieving Blender code base information
@mcp.tool(
    name="get_blender_codebase",
    description="Retrieves information about Blender's code base. This tool can be used to understand how Blender works under the hood.",
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
    Retrieves information about Blender's code base, including commands and their descriptions.
    This tool can be used to understand how Blender commands work and how to use them effectively.
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
    name="get_blender_manual",
    description="Retrieves information about Blender Python API documentation, including commands, their descriptions and how to use them. This tool provides reference to the Python API and explains how Blender commands work in order to use them effectively.",
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
def get_blender_manual(query: str) -> str:
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
    


@mcp.tool(
    name="parse_command",
    description="Parse a Blender command and extract its components.",
    annotations=ToolAnnotations(parameters={ # type: ignore
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "The Blender command to parse."
            }
        },
        "required": ["command"],
        "additionalProperties": False
    }))
def parse_command(operation_text: str) -> dict:
    """
        Converts natural language input into actionable intents and parameters.
        Parse a Blender command and extract its components.
        Args:
            operation_text: The Blender command to parse.
        The command should be a string that describes an operation in Blender, such as moving an object, scaling, or rotating it.
        The command should be in a natural language format, such as "move the cube 2 units on the x-axis" or "rotate the sphere 90 degrees around the y-axis".
        Returns:
            A dictionary containing the action, target, value, and axis extracted from the command.
    """
    # Validate the input command
    if not operation_text:
        raise ValueError("The command cannot be empty.")
    



    json_example = """
        {
            "name": "Extrude Faces",
            "identifier": "mesh.extrude_region_move",
            "mode": "EDIT_MESH",
            "keybinding": "E",
            "description": "Duplicates selected faces (and edges) and moves them along normals or specified axis, creating new geometry connected to original mesh.",
            "input": {
                "interactive": true,
                "numeric_value": true,
                "axis_lock": ["X", "Y", "Z"],
                "proportional_editing": { "supported": true }
            },
            "options": {
                "use_normal_flip": { "type": "boolean", "default": false },
                "use_dissolve_ortho_edges": { "type": "boolean", "default": false },
                "mirror": { "type": "boolean", "default": false }
            },
            "behavior": {
                "default_direction": "average face normal",
                "axis_constraint": "locked to single axis when specified",
                "geometry_connection": "new faces connect border loop to original",
                "inner_region_behaviour": "moved with extrusion, not separated"
            },
            "python_api": {
                "operator_call": "bpy.ops.mesh.extrude_region_move",
                "example": "bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={\"value\": (0,0,1)})",
                "bmesh_ops": [
                {
                    "function": "bmesh.ops.extrude_face_region",
                    "args": ["bm", "geom=selected_faces"]
                },
                {
                    "function": "bmesh.ops.translate",
                    "args": ["bm", "verts=extruded_verts", "vec=(x,y,z)"]
                }
                ]
            },
            "data_flow": {
                "input_selection": ["BMFace", "BMEdge"],
                "extrude_output": {
                "new_geometry": ["BMVert", "BMEdge", "BMFace"],
                "returned_in": "output['geom']"
                },
                "post_translate": "apply to vertices only"
            },
            "advanced_modes": [
                {
                "mode": "extrude individual faces",
                "identifier": "mesh.extrude_faces_move",
                "behavior": "extrudes each face along its own normal",
                "python_flag": "MESH_OT_extrude_faces_indiv"
                },
                {
                "mode": "extrude faces along normals",
                "identifier": "mesh.extrude_region_shrink_fatten",
                "behavior": "locks movement along local normals",
                "option": "OFFSET_EVEN"
                }
            ],
            "use_cases": [
                "box modeling (e.g. walls, limbs)",
                "branching geometry from base mesh",
                "creating architectural details"
            ],
            "references": {
                "manual": "Extends faces along normals with optional dissolve & normal flipping" ,
                "api": "bmesh.ops.extrude_face_region + translate",
                "documentation": [
                "Extrude Faces — Blender Manual" ,
                "bmesh.ops documentation"
                ]
            }
        }
    """
    
    # parse command using openai llm client and return a json object with the parsed components
    response = llm_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a Blender expert."},
            {"role": "user", "content": f"""Parse this command: {operation_text} into a JSON schema representing the blender command. Return only the JSON object without any additional text."""},
            {"role": "user", "content": f"Here is an example of a JSON schema for a Blender command: {json_example}"}
        ],
        max_tokens=1024,
        temperature=0.0
    )
    # Extract the response text
    response_text = response.choices[0].message.content

    # Parse the response text as JSON
    try:
        parsed_command = json.loads(response_text or "{}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse the command: {e}")
    # Validate the parsed command structure
    # required_keys = ["action", "target"]
    # for key in required_keys:
    #     if key not in parsed_command:
    #         raise ValueError(f"Missing required key: {key} in the parsed command.")
    
    # Return the parsed command
    return parsed_command

