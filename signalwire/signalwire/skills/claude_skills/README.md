# Claude Skills Loader

Load Claude Code-style SKILL.md files as SignalWire agent tools.

## Overview

This skill bridges Claude Code skills into SignalWire AI agents. It parses Claude skill directories (each containing a `SKILL.md` file) and makes them available as SWAIG tools that the AI can invoke.

## Claude Skill Format

Claude skills use a simple markdown format with YAML frontmatter:

```yaml
---
name: explain-code
description: Use when explaining how code works or when user asks "how does this work?"
---

When explaining code, always include:
1. Start with an analogy
2. Draw a diagram
3. Walk through step-by-step

Use $ARGUMENTS for context passed to this skill.
```

## Usage

```python
from signalwire_agents import AgentBase

agent = AgentBase(name="my-agent")

# Load Claude skills from a directory
agent.add_skill("claude_skills", {
    "skills_path": "~/.claude/skills",  # Path to Claude skills directory
})
```

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `skills_path` | string | Yes | - | Path to directory containing Claude skill folders |
| `include` | array | No | `["*"]` | Glob patterns for skills to include |
| `exclude` | array | No | `[]` | Glob patterns for skills to exclude |
| `tool_prefix` | string | No | `"claude_"` | Prefix for generated tool names (use `""` for no prefix) |
| `prompt_title` | string | No | `"Claude Skills"` | Title for the prompt section |
| `prompt_intro` | string | No | See below | Intro text for prompt section |
| `skill_descriptions` | object | No | `{}` | Override descriptions for specific skills |
| `response_prefix` | string | No | `""` | Text to prepend to skill results |
| `response_postfix` | string | No | `""` | Text to append to skill results |
| `swaig_fields` | object | No | `{}` | Extra SWAIG fields (fillers, wait_file, etc.) |

## Safety Parameters

These parameters control advanced features that are disabled by default for security:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `allow_shell_injection` | boolean | `False` | Enable `` !`command` `` preprocessing. **DANGEROUS**: allows arbitrary shell execution in skill bodies |
| `allow_script_execution` | boolean | `False` | Discover and list `scripts/`, `assets/` files in prompt sections |
| `ignore_invocation_control` | boolean | `False` | Override `disable-model-invocation` and `user-invocable` flags, register everything |
| `shell_timeout` | integer | `30` | Timeout in seconds for shell injection commands |

> **Security Warning**: Enabling `allow_shell_injection` permits skill bodies to execute arbitrary shell commands on the host system. Only enable this for trusted skills in controlled environments.

## How It Works

1. **Discovery**: Scans `skills_path` for directories containing `SKILL.md` files
2. **Parsing**: Extracts YAML frontmatter (name, description) and markdown body
3. **Prompt Injection**: Adds a prompt section telling the AI when to use each skill
4. **Tool Registration**: Creates a SWAIG tool for each skill (e.g., `claude_explain_code`)
5. **Execution**: When called, returns the skill's instructions with arguments substituted

## Invocation Control

Skills can control whether they are registered as tools and/or appear in prompt sections using frontmatter fields:

| Frontmatter | Tool Registered? | Prompt Section? | Use Case |
|---|---|---|---|
| *(defaults)* | Yes | Yes | Normal skill |
| `disable-model-invocation: true` | No | No | Completely hidden from AI |
| `user-invocable: false` | No | Yes | Knowledge-only (appears in prompt but not callable) |

Example knowledge-only skill:
```yaml
---
name: coding-standards
description: Team coding standards
user-invocable: false
---

Always follow these coding standards:
- Use 4-space indentation
- Write docstrings for all public methods
```

Set `ignore_invocation_control=True` to override these flags and register everything.

### Breaking Change

`disable-model-invocation` and `user-invocable` flags were previously parsed but ignored. They are now respected by default. Set `ignore_invocation_control=True` to restore the old behavior where all skills are registered regardless of these flags.

## Argument Substitution

Claude skills support argument placeholders:

- `$ARGUMENTS` - Full arguments string
- `$0`, `$1`, `$2`... - Positional arguments (space-separated)
- `$ARGUMENTS[0]`, `$ARGUMENTS[1]`... - Same as above

Example skill:
```yaml
---
name: migrate-component
description: Migrate a component between frameworks
---

Migrate the $0 component from $1 to $2.
Preserve all existing behavior.
```

When called with arguments `"Button React Vue"`, expands to:
```
Migrate the Button component from React to Vue.
Preserve all existing behavior.
```

### Fallback Argument Appending

If a skill body does **not** contain a bare `$ARGUMENTS` placeholder (the indexed form `$ARGUMENTS[N]` does not count) and arguments are non-empty, the arguments are automatically appended:

```
[skill body content]

ARGUMENTS: [the arguments value]
```

This matches Claude Code behavior where arguments are always visible to the AI. Skills that explicitly use `$ARGUMENTS` control their own placement and do not get the fallback.

## Variable Substitution

Skill bodies support variable placeholders that are replaced at invocation time:

| Variable | Description |
|----------|-------------|
| `${CLAUDE_SKILL_DIR}` | Absolute path to the skill's directory |
| `${CLAUDE_SESSION_ID}` | Session/call ID from the current request |

Example:
```yaml
---
name: file-helper
description: Help with file operations
---

The skill files are located at: ${CLAUDE_SKILL_DIR}
Current session: ${CLAUDE_SESSION_ID}
```

## Shell Injection

> **Security Warning**: Shell injection allows arbitrary command execution. Only enable for trusted skills.

When `allow_shell_injection=True`, patterns like `` !`command` `` in skill bodies are replaced with the command's stdout:

```yaml
---
name: git-status
description: Show current git status
---

Current branch: !`git branch --show-current`
Last commit: !`git log -1 --oneline`
```

When called, `!`git branch --show-current`` is replaced with the actual output of the command, executed in the skill's directory.

Configuration:
```python
agent.add_skill("claude_skills", {
    "skills_path": "~/.claude/skills",
    "allow_shell_injection": True,
    "shell_timeout": 10,  # seconds
})
```

When shell injection is **disabled** (default) but patterns are detected in skill bodies, a WARNING is logged for each pattern to alert operators.

## File Discovery

When `allow_script_execution=True`, non-markdown files in skill directories are discovered and listed in prompt sections:

```
my-skill/
├── SKILL.md
├── scripts/
│   ├── build.sh
│   └── test.py
├── assets/
│   └── template.json
└── config.yaml
```

Files are categorized as:
- **Scripts**: Files under `scripts/` directory
- **Assets**: Files under `assets/` directory
- **Other files**: Any other non-`.md` files at top level or other directories

Hidden files (starting with `.`) and `__pycache__` directories are skipped.

## Customizing Descriptions

Override skill descriptions when loading:

```python
agent.add_skill("claude_skills", {
    "skills_path": "~/.claude/skills",
    "skill_descriptions": {
        "explain-code": "Use when user asks how something works",
        "commit": "Use when user wants to create a git commit",
    }
})
```

Priority: `skill_descriptions` override > SKILL.md `description` > skill name

## Filtering Skills

Include or exclude specific skills:

```python
agent.add_skill("claude_skills", {
    "skills_path": "~/.claude/skills",
    "include": ["explain-*", "code-*"],  # Only these patterns
    "exclude": ["*-internal"],            # Skip these
})
```

## Tool Prefix

By default, tools are prefixed with `claude_`. You can change or remove this:

```python
# Custom prefix
agent.add_skill("claude_skills", {
    "skills_path": "~/.claude/skills",
    "tool_prefix": "skill_",  # Results in skill_explain_code
})

# No prefix
agent.add_skill("claude_skills", {
    "skills_path": "~/.claude/skills",
    "tool_prefix": "",  # Results in explain_code
})
```

## SWAIG Fields

Add fillers, wait files, or other SWAIG fields to all generated tools:

```python
agent.add_skill("claude_skills", {
    "skills_path": "~/.claude/skills",
    "swaig_fields": {
        "fillers": {"en": ["Just a moment...", "Let me check..."]},
        "wait_file": "https://example.com/hold.mp3",
        "wait_file_loops": 3
    }
})
```

## Response Wrapping

Wrap skill results with prefix and postfix text to provide context or instructions to the AI:

```python
agent.add_skill("claude_skills", {
    "skills_path": "~/.claude/skills",
    "response_prefix": "Use the following skill instructions to help the user:",
    "response_postfix": "Remember to be concise and helpful in your response."
})
```

This wraps all skill results:
```
Use the following skill instructions to help the user:

[SKILL.md content or section content here]

Remember to be concise and helpful in your response.
```

## Generated Tools

Each Claude skill becomes a SWAIG tool named `{prefix}{skill_name}` (default prefix: `claude_`):

| Claude Skill | Default Tool Name | With `tool_prefix=""` |
|--------------|-------------------|----------------------|
| `explain-code` | `claude_explain_code` | `explain_code` |
| `review-pr` | `claude_review_pr` | `review_pr` |
| `commit` | `claude_commit` | `commit` |

## Prompt Section

The skill automatically adds a prompt section like:

```
## Claude Skills

You have access to specialized skills. Call the appropriate tool when the user's question matches:

- claude_explain_code: Use when explaining how code works
- claude_review_pr: Use when reviewing pull requests
- claude_commit: Use when creating git commits
```

## Supporting Files (Progressive Disclosure)

Skills can include additional markdown files that are loaded on-demand. This enables progressive disclosure - the SKILL.md content goes into the prompt as a table of contents, while supporting files are loaded only when the AI calls the tool with a specific section.

### Directory Structure

```
my-skill/
├── SKILL.md              # TOC - goes in prompt
├── reference.md          # Supporting file
├── examples.md           # Supporting file
├── references/
│   ├── api.md            # Nested supporting file
│   └── errors.md
└── templates/
    └── template.md
```

### How It Works

1. **Discovery**: All `.md` files in the skill directory (recursively) are discovered
2. **Prompt Section**: SKILL.md body becomes a TOC in the agent's prompt
3. **Tool Registration**: ONE tool per skill with optional `section` enum parameter
4. **Enum Values**: All discovered .md files (e.g., `["reference", "examples", "references/api", "references/errors", "templates/template"]`)
5. **Execution**: When called with a section, return that file's content

### Example SKILL.md with Sections

```yaml
---
name: explain-code
description: Explains code with diagrams and analogies
---

When explaining code, always include:
1. Start with an analogy
2. Draw a diagram
3. Walk through step-by-step

Use the reference sections for detailed guidance.
```

### Generated Tool

When sections exist, the tool has a `section` enum parameter:

```json
{
  "function": "claude_explain_code",
  "parameters": {
    "type": "object",
    "properties": {
      "section": {
        "type": "string",
        "description": "Which reference section to load",
        "enum": ["examples", "reference", "references/api", "references/errors"]
      },
      "arguments": {
        "type": "string",
        "description": "Arguments or context to pass to the skill"
      }
    }
  }
}
```

### Prompt Section

The agent's prompt includes the SKILL.md body plus available sections:

```
## explain-code

When explaining code, always include:
1. Start with an analogy
2. Draw a diagram
3. Walk through step-by-step

Use the reference sections for detailed guidance.

Available reference sections: examples, reference, references/api, references/errors
Call claude_explain_code(section="<name>") to load a section.
```

### Benefits

- **Reduced prompt size**: Only SKILL.md goes in the prompt; supporting files load on-demand
- **Better organization**: Split large skill documentation into logical sections
- **Nested structure**: Organize files in subdirectories for complex skills

## Unsupported Claude Code Features

All frontmatter fields from the Claude Code skills spec are **parsed** from SKILL.md files. When an unsupported field is detected, a `WARNING` is logged at skill discovery time identifying the specific skill and field.

| Feature | Status | Notes |
|---------|--------|-------|
| `context: fork` | Not supported | Subagent execution is a Claude Code concept; logged as WARNING if set |
| `agent` | Not supported | Subagent type selection; logged as WARNING if set |
| `allowed-tools` | Not supported | Tool restrictions per skill; logged as WARNING if set |
| `model` | Not supported | Model switching; logged as WARNING if set |
| `hooks` | Not supported | Lifecycle hooks; logged as WARNING if set |
| `` !`command` `` | Opt-in | Requires `allow_shell_injection=True`; logged as WARNING if patterns detected but disabled |
| `license` | Informational | Parsed and logged at DEBUG level |
| `compatibility` | Informational | Parsed and logged at DEBUG level |

## Example

Directory structure:
```
~/.claude/skills/
├── explain-code/
│   ├── SKILL.md
│   ├── examples.md
│   └── references/
│       └── patterns.md
├── review-pr/
│   └── SKILL.md
└── commit/
    └── SKILL.md
```

Agent code:
```python
from signalwire_agents import AgentBase

agent = AgentBase(name="code-assistant")

agent.add_skill("claude_skills", {
    "skills_path": "~/.claude/skills",
    "prompt_intro": "You have coding assistance tools available:",
})

if __name__ == "__main__":
    agent.serve()
```

The AI will now have access to `claude_explain_code`, `claude_review_pr`, and `claude_commit` tools, and will know when to use them based on user questions.
