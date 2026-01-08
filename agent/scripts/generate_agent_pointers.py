#!/usr/bin/env python3
import os
import re

# Configuration
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
COMPONENTS_FILE = os.path.join(PROJECT_ROOT, 'agent', 'COMPONENT_GRAPH.md')

def parse_components_table(file_path):
    """
    Parses the markdown table in COMPONENT_GRAPH.md to extract component info.
    Expects table row format: | `id` | `path` | ...
    """
    components = []
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return []

    with open(file_path, 'r') as f:
        lines = f.readlines()

    # Regex to extract content between pipes
    # Example: | `root` | `.` | `markdown` ...
    # We want group 1 (id) and group 2 (path)
    
    for line in lines:
        line = line.strip()
        if not line.startswith('|') or '---' in line or 'Component ID' in line:
            continue
            
        parts = [p.strip() for p in line.split('|') if p.strip()]
        if len(parts) >= 2:
            # Strip backticks
            comp_id = parts[0].strip('`')
            comp_path = parts[1].strip('`')
            
            components.append({
                'id': comp_id,
                'path': comp_path
            })
            
    return components

def create_pointer_file(component):
    comp_id = component['id']
    rel_path = component['path']
    
    # Resolve absolute path for the target directory
    target_dir = os.path.join(PROJECT_ROOT, rel_path)
    
    if not os.path.exists(target_dir):
        print(f"Skipping {comp_id}: Directory {target_dir} does not exist.")
        return

    file_path = os.path.join(target_dir, 'AGENTS.md')
    
    content = f"""<!-- AGENT_POINTER_FILE -->
# Agent Context: {comp_id}

This directory is a **Component** within the larger project.
Follow the specific instructions below.

- **Active Scope**: `{comp_id}`
- **Path**: `{rel_path}`
- **Component Config**: `agent/components/{comp_id}.md` (See root)

> ⚠️ **Authoritative Source**: The root `agent/` directories contain the master instructions.
> Refer to `agent/ROUTING_RULES.md` for cross-component workflows.
"""
    
    try:
        with open(file_path, 'w') as f:
            f.write(content)
        print(f"Created/Updated: {file_path}")
    except Exception as e:
        print(f"Error writing to {file_path}: {e}")

def main():
    print(f"Scanning {COMPONENTS_FILE}...")
    components = parse_components_table(COMPONENTS_FILE)
    print(f"Found {len(components)} components.")
    
    for comp in components:
        create_pointer_file(comp)
    
    print("Done.")

if __name__ == "__main__":
    main()
