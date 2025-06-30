## This is a blender expert agent that can assist with Blender-related tasks.
# these functions are exposed trhough mcp.resource decorators and can be called
# by a client using the official MCP layer protocol.

import os
import json
from typing import List
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

import subprocess 


# Load environment variables from .env file
load_dotenv()

# initialize FastMCP server
mcp = FastMCP("github-assistant")

# tool to analyze file changes in a given repository
@mcp.tool(
    name="analyze_file_changes",
    description="Analyze file changes in a given repository",
    annotations=ToolAnnotations(parameters={  # type: ignore
        "type": "object",
        "properties": {
            "repo_url": {
                "type": "string",
                "description": "The URL of the repository to analyze."
            },
            "base_branch": {
                "type": "string",
                "default": "main",
                "description": "The base branch to compare against. Defaults to 'main'."
            },
            "include_diff": {
                "type": "boolean",
                "default": True,
                "description": "Whether to include the diff in the response."
            },
            "max_diff_lines": {
                "type": "integer",
                "default": 500,
                "description": "The maximum number of lines to include in the diff."
            }
        },
        "required": ["repo_url", "file_path"],
        "additionalProperties": False
    })
)
async def analyze_file_changes(base_dir,  base_branch: str = "main", include_diff: bool = True, max_diff_lines: int = 500) -> str:
    """
    Analyzes file changes in a given repository.
    Args:
        base_dir: The base directory of the repository to analyze.
        base_branch: The base branch to compare against.
        include_diff: Whether to include the diff in the response.
        max_diff_lines: The maximum number of lines to include in the diff.
    Returns:
        A string containing the analysis of file changes.
    """
    # Validate the base directory
    if not base_dir or not os.path.isdir(base_dir):
        raise ValueError("The base directory must be a valid directory path.")
    # Validate the input parameters
    if not base_branch:
        raise ValueError("The base branch cannot be empty.")
    
    try:
        # Get the diff
        result = subprocess.run(
            ["git", "diff", f"{base_branch}...HEAD", "--", base_dir],
            cwd=base_dir,
            capture_output=True, 
            text=True
        )

        print(f"Running git diff in {base_dir} against {base_branch}...HEAD")
        print(f"Command output: {result.stdout}")
        
        diff_output = result.stdout
        diff_lines = diff_output.split('\n')
        
        # Smart truncation if needed
        if len(diff_lines) > max_diff_lines:
            truncated_diff = '\n'.join(diff_lines[:max_diff_lines])
            truncated_diff += f"\n\n... Output truncated. Showing {max_diff_lines} of {len(diff_lines)} lines ..."
            diff_output = truncated_diff
        
        # Get summary statistics
        stats_result = subprocess.run(
            ["git", "diff", "--stat", f"{base_branch}...HEAD"],
            capture_output=True,
            text=True
        )
        
        return json.dumps({
            "stats": stats_result.stdout,
            "total_lines": len(diff_lines),
            "diff": diff_output if include_diff else "Use include_diff=true to see diff",
            "files_changed": len(diff_lines) if include_diff else "Use include_diff=true to see files changed"
        })
        
    except Exception as e:
        return json.dumps({"error": str(e)})


