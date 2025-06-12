## Script for generating a vector database for Blender commands
import os
from typing import List, Dict
from mcp_servers_py.blender_expert.parser import parse_command

def download_code_base():
    """
    Downloads the code base for the Blender github repository.
    """
    # Placeholder for downloading or setting up the code base
    print("Downloading code base... (This is a placeholder function)")
    # Download git repo
    

def generate_vector_db(commands: List[str]) -> List[Dict]:
    """
    Generate a vector database from a list of Blender commands.

    Args:
        commands (List[str]): A list of Blender commands in natural language.

    Returns:
        List[Dict]: A list of dictionaries containing parsed command components.
    """
    vector_db = []
    
    for command in commands:
        try:
            parsed_command = parse_command(command)
            vector_db.append(parsed_command)
        except Exception as e:
            print(f"Error parsing command '{command}': {e}")
    
    return vector_db



if __name__ == "__main__":
    # Example commands to generate the vector database
    example_commands = [
        "Translate the cube on the x-axis by 2 units",
        "Rotate the camera around the z-axis by 45 degrees",
        "Scale the sphere uniformly by a factor of 1.5",
        "Move the light to the y-axis position of 3"
    ]
    
    vector_db = generate_vector_db(example_commands)
    
    # Print the generated vector database
    for entry in vector_db:
        print(entry)