# blender_expert/parser.py
import re

def parse_command(text):
    return {
        "action": extract_action(text),
        "target": extract_target(text),
        "value": extract_value(text),
        "axis": extract_axis(text),
    }

def extract_action(text):
    actions = ['translate', 'move', 'rotate', 'scale']
    for action in actions:
        if action in text.lower():
            return action if action != 'move' else 'translate'
    return None

def extract_target(text):
    # Look for common Blender object names
    objects = ['cube', 'sphere', 'plane', 'camera', 'light']
    for obj in objects:
        if obj in text.lower():
            return obj
    return "object"  # default fallback

def extract_value(text):
    match = re.search(r'(\d+(\.\d+)?)', text)
    return float(match.group()) if match else None

def extract_axis(text):
    for axis in ['x', 'y', 'z']:
        if f"{axis}-axis" in text.lower() or f"on {axis}" in text.lower():
            return axis.upper()
    return None