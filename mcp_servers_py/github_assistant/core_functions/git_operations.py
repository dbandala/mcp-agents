import os
import json
import subprocess
from typing import List

def file_changes(base_dir,  base_branch: str = "main", include_diff: bool = True, max_diff_lines: int = 500) -> str:
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
    try:
        # Get the diff
        result = subprocess.run(
            ["git", "diff", base_branch],
            cwd=base_dir,
            capture_output=True, 
            text=True
        )
        
        diff_output = result.stdout
        diff_lines = diff_output.split('\n')
        
        # Smart truncation if needed
        if len(diff_lines) > max_diff_lines:
            truncated_diff = '\n'.join(diff_lines[:max_diff_lines])
            truncated_diff += f"\n\n... Output truncated. Showing {max_diff_lines} of {len(diff_lines)} lines ..."
            diff_output = truncated_diff
        
        # Get summary statistics
        stats_result = subprocess.run(
            ["git", "diff", "--stat", base_branch],
            cwd=base_dir,
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



if __name__ == "__main__":
    # Example usage
    base_dir = os.getcwd()  # Current working directory
    base_branch = "main"  # Default branch to compare against
    print(file_changes(base_dir, base_branch, include_diff=True, max_diff_lines=10))




