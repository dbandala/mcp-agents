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

from parser import parse_command

# Load environment variables from .env file
load_dotenv()

# initialize FastMCP server
mcp = FastMCP("blender_expert")

# llm client
llm_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)


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




@mcp.tool(
    name="get_knowledge_base",
    description="Retrieves detailed information about Blender commands, objects, and concepts.",
    annotations=ToolAnnotations(parameters={ # type: ignore
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The query to search in the knowledge base."
            }
        },
        "required": ["query"],
        "additionalProperties": False
    }))
def get_knowledge_base(query: str) -> List[str]:
    """
    Retrieves detailed information about Blender commands, objects, and concepts.
    This function searches a knowledge base for relevant information based on the provided query.
    It fetches information that can help users understand how to use Blender effectively.
    It searches into a vector database or knowledge base for relevant information based on the provided query.
    Args:
        query: The query to search in the knowledge base.
    Returns:
        A list of relevant information from the knowledge base.
    """
    # Validate the input query
    if not query:
        raise ValueError("The query cannot be empty.")
    
    # For simplicity, we return a static list of Blender commands and descriptions
    # In a real application, this would query a database or knowledge base
    knowledge_base = [
        "Blender is a powerful open-source 3D creation suite.",
        "You can create 3D models, animations, and renderings using Blender.",
        "Blender supports Python scripting for automation and custom tools.",
        "Common operations include adding objects, modifying meshes, and rendering scenes."
    ]
    
    return [info for info in knowledge_base if query.lower() in info.lower()]



@mcp.tool(
    name="get_blender_commands",
    description="Get a list of Blender commands and their descriptions.",
    annotations=ToolAnnotations(parameters={ # type: ignore
        "type": "object",
        "properties": {},
        "required": [],
        "additionalProperties": False
    }))
def get_blender_commands() -> List[str]:
    """Get a list of Blender commands and their descriptions."""
    commands = [
        "bpy.ops.object.select_all(action='SELECT') - Select all objects in the scene.",
        "bpy.ops.object.delete() - Delete selected objects.",
        "bpy.ops.object.mode_set(mode='EDIT') - Switch to Edit Mode for the active object.",
        "bpy.ops.object.mode_set(mode='OBJECT') - Switch back to Object Mode.",
        "bpy.ops.mesh.primitive_cube_add() - Add a new cube to the scene.",
        "bpy.ops.mesh.primitive_uv_sphere_add() - Add a new UV sphere to the scene.",
        "bpy.ops.render.render() - Render the current scene.",
        "bpy.data.objects['Cube'].location.x += 1.0 - Move the Cube object along the X axis."
    ]
    return commands

