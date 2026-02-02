#!/usr/bin/env python3
import argparse
import os
import sys
from pathlib import Path

# Configuration
AGENT_ROOT = Path(__file__).parent.absolute()
PROMPTS_DIR = AGENT_ROOT / "prompts"
STATE_DIR = AGENT_ROOT / "agent" / "09_state"
MANIFEST_FILE = AGENT_ROOT / "agent" / "AGENT_MANIFEST.md"

def load_file(path):
    if not path.exists():
        return f"[ERROR] File not found: {path}"
    with open(path, "r") as f:
        return f.read()

def cmd_status(args):
    """Show current project state and manifest version."""
    print("════ AGENT OS STATUS ════")
    # Manifest
    if MANIFEST_FILE.exists():
        lines = load_file(MANIFEST_FILE).splitlines()
        for line in lines:
            if line.startswith("**Version**") or line.startswith("**Name**"):
                print(line)
    else:
        print("[WARN] AGENT_MANIFEST.md not found in root.")

    print("\n--- Project State ---")
    state_file = STATE_DIR / "PROJECT_STATE.md"
    if state_file.exists():
        content = load_file(state_file)
        # Print non-empty lines
        print(content.strip())
    else:
        print("No active project state.")

def cmd_prompts(args):
    """List available prompts."""
    print("════ AVAILABLE PROMPTS ════")
    if not PROMPTS_DIR.exists():
        print("[ERROR] prompts/ directory missing.")
        return

    for root, dirs, files in os.walk(PROMPTS_DIR):
        rel_root = Path(root).relative_to(PROMPTS_DIR)
        if str(rel_root) == ".":
            category = "Root"
        else:
            category = str(rel_root)
        
        print(f"\n[{category}]")
        for f in sorted(files):
            if f.endswith(".txt") or f.endswith(".md"):
                print(f"  - {f}")

def cmd_validate(args):
    """Simple validation of structure."""
    print("════ SYSTEM VALIDATION ════")
    required = [
        AGENT_ROOT / "agent",
        PROMPTS_DIR,
        AGENT_ROOT / "Dockerfile",
        AGENT_ROOT / ".github"
    ]
    all_ok = True
    for p in required:
        if p.exists():
            print(f"[PASS] {p.name}")
        else:
            print(f"[FAIL] {p.name} missing")
            all_ok = False
    
    if all_ok:
        print("\nSystem Integrity: GREEN")
    else:
        print("\nSystem Integrity: RED")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Agent OS Native CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Status
    parser_status = subparsers.add_parser("status", help="Show system status")
    
    # Prompts
    parser_prompts = subparsers.add_parser("prompts", help="List text prompts")

    # Validate
    parser_check = subparsers.add_parser("validate", help="Check integrity")

    args = parser.parse_args()

    if args.command == "status":
        cmd_status(args)
    elif args.command == "prompts":
        cmd_prompts(args)
    elif args.command == "validate":
        cmd_validate(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
