# Skills Module

The `skills` module provides a file system-based skills discovery and management system.

## Overview

Skills are organized as directories containing Python modules and documentation. Agents can discover and use skills through the file system, enabling a modular and extensible architecture.

## Skills Structure

A skill is a directory with the following structure:

```
skills/
├── web/
│   ├── SKILL.md          # Skill metadata (YAML frontmatter + description)
│   ├── http.py           # Python modules
│   └── scraping.py
└── data/
    ├── SKILL.md
    └── processing.py
```

### SKILL.md Format

Each skill must have a `SKILL.md` file with YAML frontmatter:

```markdown
---
name: web
description: Web scraping and HTTP utilities
license: MIT
compatibility: python>=3.8
metadata:
  author: "Actium Team"
  version: "1.0.0"
allowed-tools: execute_python, execute_shell
---

# Web Skill

This skill provides utilities for web scraping and HTTP requests.

## Functions

- `fetch(url)`: Fetch content from a URL
- `scrape(html)`: Parse HTML content
```

#### Frontmatter Fields

- **`name`** (required): Skill name, must match directory name
- **`description`** (required): Brief description of the skill
- **`license`** (optional): License information
- **`compatibility`** (optional): Compatibility requirements
- **`metadata`** (optional): Additional metadata dictionary
- **`allowed-tools`** (optional): List of allowed tools

## Components

### Parser (`parser.py`)

The parser module discovers and validates skills from the file system.

#### Functions

##### `discover_skills(skills_dir: Path) -> list[Path]`

Discovers all valid skill directories in the skills root directory.

```python
from actium.skills.parser import discover_skills
from pathlib import Path

skill_dirs = discover_skills(Path("./skills"))
# Returns: [Path("./skills/web"), Path("./skills/data")]
```

**Validation Rules**:
- Directory must exist
- Must contain `SKILL.md` file
- YAML frontmatter must be valid
- `name` field must match directory name

##### `read_properties(skill_dir: Path) -> SkillProperties`

Reads and parses skill properties from `SKILL.md` frontmatter.

```python
from actium.skills.parser import read_properties

props = read_properties(Path("./skills/web"))
# props.name: "web"
# props.description: "Web scraping and HTTP utilities"
```

**Raises**:
- `FileNotFoundError`: If `SKILL.md` doesn't exist
- `ValueError`: If YAML parsing fails or required fields are missing

##### `find_skill_md(skill_dir: Path) -> Optional[Path]`

Finds the `SKILL.md` file in a skill directory.

```python
from actium.skills.parser import find_skill_md

skill_md = find_skill_md(Path("./skills/web"))
# Returns: Path("./skills/web/SKILL.md") or None
```

#### Data Structures

```python
@dataclass
class SkillProperties:
    """Skill properties extracted from SKILL.md frontmatter"""
    name: str
    description: str
    license: Optional[str] = None
    compatibility: Optional[str] = None
    metadata: Optional[dict[str, str]] = None
    allowed_tools: Optional[str] = None
```

### Prompt Generator (`prompt.py`)

The prompt generator formats skill information for inclusion in agent system prompts.

#### Functions

##### `to_prompt(skill_dirs: list[Path]) -> str`

Generates an XML-formatted prompt block listing available skills.

```python
from actium.skills.prompt import to_prompt
from actium.skills.parser import discover_skills

skill_dirs = discover_skills(Path("./skills"))
prompt = to_prompt(skill_dirs)
```

**Output Format**:

```xml
<available_skills>
<skill>
<name>web</name>
<description>Web scraping and HTTP utilities</description>
<location>/path/to/skills/web/SKILL.md</location>
</skill>
<skill>
<name>data</name>
<description>Data processing utilities</description>
<location>/path/to/skills/data/SKILL.md</location>
</skill>
</available_skills>
```

**Features**:
- XML format (Anthropic-recommended for Claude models)
- HTML-escaped content for safety
- Includes name, description, and location
- Skips invalid skills automatically

## Integration with Agents

### Automatic Discovery

The agent decorator automatically discovers skills when building the system prompt:

```python
# In agent.py
def _build_system_prompt(user_prompt: str, skills_dir: Optional[Path] = None) -> str:
    if skills_dir is not None:
        skill_dirs = discover_skills(skills_dir)
        skills_prompt = to_prompt(skill_dirs) if skill_dirs else ""
        # skills_prompt is added to system prompt
```

### Skills in System Prompt

Skills are included in the system prompt under "Available Skills" section:

```
## Available Skills

The following skills are available for use. Each skill provides specialized 
functionality that you can leverage by importing and using the provided functions.

<available_skills>
...
</available_skills>

To use a skill, first explore its location using shell commands to read the 
SKILL.md file, then import and use the functions as needed.
```

### File System Access

Agents access skills through the file system:

1. **Discovery**: Agent reads system prompt to see available skills
2. **Exploration**: Agent uses `execute_shell` to explore skill directories
3. **Import**: Agent uses `execute_python` to import and use skill modules

```python
# Agent can do:
# 1. Read SKILL.md
result = await execute_shell("cat skills/web/SKILL.md")

# 2. Import and use
result = await execute_python("from web.http import fetch")
result = await execute_python("content = fetch('https://example.com')")
```

## Best Practices

### Skill Development

1. **Clear Documentation**: Write comprehensive `SKILL.md` with examples
2. **Modular Design**: Split functionality into logical modules
3. **Type Hints**: Use type hints in Python modules for better IDE support
4. **Error Handling**: Implement robust error handling in skill functions

### Skill Organization

1. **One Skill Per Directory**: Each skill should be self-contained
2. **Descriptive Names**: Use clear, descriptive skill names
3. **Version Control**: Track skills in version control
4. **Dependencies**: Document dependencies in `SKILL.md`

### Agent Usage

1. **Explore First**: Agents should read `SKILL.md` before using skills
2. **Import Correctly**: Use proper import paths relative to skills directory
3. **Handle Errors**: Check for import and execution errors
4. **Reuse Skills**: Leverage existing skills instead of reimplementing

## Example Skill

### Directory Structure

```
skills/
└── calculator/
    ├── SKILL.md
    └── operations.py
```

### SKILL.md

```markdown
---
name: calculator
description: Basic calculator operations
license: MIT
---

# Calculator Skill

Provides basic mathematical operations.

## Functions

- `add(a, b)`: Add two numbers
- `multiply(a, b)`: Multiply two numbers
```

### operations.py

```python
"""Calculator operations"""

def add(a: float, b: float) -> float:
    """Add two numbers"""
    return a + b

def multiply(a: float, b: float) -> float:
    """Multiply two numbers"""
    return a * b
```

### Agent Usage

```python
# Agent discovers skill from system prompt
# Agent explores:
result = await execute_shell("cat skills/calculator/SKILL.md")

# Agent uses:
result = await execute_python("from calculator.operations import add, multiply")
result = await execute_python("result = add(10, 20)\nprint(result)")
```

## See Also

- [Agent Module](./agent.md): How skills are integrated into agents
- [Infrastructure Module](./infrastructure.md): How skills are linked in sandbox
- [Runtime Module](./runtime.md): Tools agents use to access skills

