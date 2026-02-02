# Agent OS Prompts - Quick Start

## 30-Second Guide: How to Pick the Right Prompt

### **Starting a New Project?**

→ Use `prompts/by_entrypoint/new_project.txt`

### **Working on Existing Code?**

→ Use `prompts/by_entrypoint/existing_project.txt`

### **Specific Task?**

→ Check `prompts/cheatsheets/prompt_selector.md` for the decision tree

### **Emergency/Production Issue?**

→ Use `prompts/by_scenario/emergency_hotfix.txt`

## What Are These Prompts?

These are **copy-paste instructions** for AI assistants (ChatGPT, Claude, Gemini, etc.) that make them follow the Agent OS framework. Each prompt:

- Forces the AI to use the structured workflows in `agent/`
- Ensures consistent output locations (`plans/`)
- Mandates quality gates and state tracking
- Prevents the AI from "freelancing" or making assumptions

## How to Use

1. **Copy** the entire content of the appropriate `.txt` file
2. **Paste** it into your AI chat as the first message
3. **Provide** any additional context (project description, bug details, etc.)
4. **Let the AI execute** following the Agent OS structure

## Universal Wrapper

ALL prompts include the content from `00_master_prompt.txt`. This ensures:

- Consistent behavior across all scenarios
- Proper state management
- Mandatory gate enforcement
- Standardized response format

## Directory Structure

```
prompts/
├── 00_master_prompt.txt          # Universal wrapper (included in all prompts)
├── README.md                      # This file
├── PROMPTS_GUIDE.md              # Detailed guide for each situation
├── by_entrypoint/                # Main workflow prompts
│   ├── new_project.txt
│   ├── existing_project.txt
│   ├── srs_only.txt
│   └── ...
├── by_scenario/                  # Specific problem prompts
│   ├── bug_fix.txt
│   ├── emergency_hotfix.txt
│   ├── performance_investigation.txt
│   └── ...
├── hard_cases/                   # Tech-specific hard case prompts (Docker, GitHub, C++, etc.)
└── cheatsheets/
    ├── prompt_selector.md        # Decision tree
    └── quick_copy_blocks.md      # Mobile-friendly versions
```

## Quick Links

- **Full Guide**: See `PROMPTS_GUIDE.md` for detailed explanations
- **Decision Tree**: See `cheatsheets/prompt_selector.md` to choose quickly
- **Agent OS Docs**: See `../AGENT_MANIFEST.md` for system overview
- **Hard Cases**: `hard_cases/` prompts map diagnostics to recovery playbooks per tech (Docker, GitHub, C++, CMake, Java, Python, Flask, Flutter, Static Web)

## Model Compatibility

These prompts work with:

- ✅ GPT-4, GPT-4 Turbo, GPT-4o
- ✅ Claude 3 (Opus, Sonnet, Haiku)
- ✅ Gemini 1.5 Pro, Gemini 2.0
- ✅ Open-source models (Llama 3, Mixtral, etc.)

The prompts are model-agnostic and use standard markdown/text format.
