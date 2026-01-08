#!/bin/bash
# Quick setup script for Antigravity integration

echo "🤖 Setting up Antigravity integration..."
echo ""

# Check if agent/ directory exists (checking for 'agent' or legacy 'ai')
SOURCE_DIR=""
if [ -d "agent" ]; then
    SOURCE_DIR="agent"
    echo "Found agent/ directory (Standard) ✓"
elif [ -d "ai" ]; then
    SOURCE_DIR="ai"
    echo "Found ai/ directory (Legacy) ✓"
else
    echo "❌ Error: agent/ or ai/ directory not found"
    echo "   Please run this script from your project root with the AI pack folder"
    exit 1
fi

echo ""

# Ask user preference
echo "Choose integration method:"
if [ "$SOURCE_DIR" == "agent" ]; then
    echo "1) Integration already standard (agent/ detected). Verify only."
else
    echo "1) Rename $SOURCE_DIR/ to agent/ (Recommended - Antigravity standard)"
fi
echo "2) Keep $SOURCE_DIR/ and create agent/ symlink"
echo "3) Keep $SOURCE_DIR/ and create agent/ pointer files"
echo ""
read -p "Enter choice (1-3): " choice

case $choice in
    1)
        echo ""
        if [ "$SOURCE_DIR" == "agent" ]; then
             echo "Already using standard 'agent' directory name. Nothing to rename."
        else
            echo "Renaming $SOURCE_DIR/ to agent/..."
            mv "$SOURCE_DIR" agent
            echo "✓ Done! Antigravity will auto-detect agent/ directory"
        fi
        ;;
    2)
        echo ""
        if [ "$SOURCE_DIR" == "agent" ]; then
            echo "Source is already 'agent'. No need to symlink to itself."
        else
            echo "Creating agent/ symlink to $SOURCE_DIR/..."
            ln -s "$SOURCE_DIR" agent
            echo "✓ Done! Antigravity will follow symlink to agent/"
        fi
        ;;
    3)
        echo ""
        echo "Creating agent/ pointer directory..."
        # If source is agent, we can't create agent dir. Assume this option is mainly for legacy naming.
        if [ "$SOURCE_DIR" == "agent" ]; then
             echo "Source is already 'agent'. This option is redundant."
             exit 0
        fi
        
        mkdir -p agent
        
        # Create pointer README
        cat > agent/README.md << EOF
# Agent Configuration

This project uses AI Agent MD Pack located in \`$SOURCE_DIR/\` directory.

**Start here:** [$SOURCE_DIR/00_INDEX.md](../$SOURCE_DIR/00_INDEX.md)

All agent instructions, workflows, and policies are in the \`$SOURCE_DIR/\` folder.
EOF
        
        # Create symlinks to key files
        ln -s ../$SOURCE_DIR/00_SYSTEM.md agent/00_SYSTEM.md
        ln -s ../$SOURCE_DIR/00_INDEX.md agent/00_INDEX.md
        ln -s ../$SOURCE_DIR/01_PROJECT_CONTEXT.md agent/01_PROJECT_CONTEXT.md
        
        echo "✓ Done! Created agent/ with pointers to $SOURCE_DIR/"
        ;;
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac

echo ""
echo "🎉 Integration complete!"
echo ""
echo "Verification:"

# Verify setup
if [ -f "agent/00_INDEX.md" ]; then
    echo "✓ agent/00_INDEX.md found"
else
    echo "✗ agent/00_INDEX.md not found"
fi

if [ -f "agent/00_SYSTEM.md" ]; then
    echo "✓ agent/00_SYSTEM.md found"
else
    echo "✗ agent/00_SYSTEM.md not found"
fi

if [ -f "agent/01_PROJECT_CONTEXT.md" ]; then
    echo "✓ agent/01_PROJECT_CONTEXT.md found"
else
    echo "✗ agent/01_PROJECT_CONTEXT.md not found"
fi

echo ""
echo "Next steps:"
echo "1. Fill agent/01_PROJECT_CONTEXT.md (2 required fields)"
echo "2. Test with Antigravity: 'What agent configuration do you see?'"
echo "3. Start using: 'Read agent/00_INDEX.md and [your task]'"
echo ""
echo "For more info: See ANTIGRAVITY_INTEGRATION.md"
