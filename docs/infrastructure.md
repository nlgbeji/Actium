# Infrastructure Module

The `infrastructure` module provides core infrastructure components for file system management and execution history tracking.

## Overview

The infrastructure layer manages:
- **Sandbox**: File system isolation and skills linking
- **History**: Execution history tracking (if implemented)

## Components

### Sandbox

The `Sandbox` class manages file system isolation for agents, providing a dedicated working directory and access to skills.

#### Features

- **Directory Management**: Creates and manages sandbox directories
- **Skills Linking**: Creates symbolic links (or copies) to skills directory
- **Isolation**: Each agent gets its own sandbox directory
- **Skills Discovery**: Lists available skills with descriptions

#### Usage

```python
from actium.infrastructure.sandbox import Sandbox

sandbox = Sandbox(
    sandbox_dir="./sandbox/agent1",
    skills_dir="./skills"
)

# Sandbox directory is created automatically
# Skills are linked at sandbox_dir/skills
```

#### Methods

- **`list_skills() -> str`**: Returns formatted string listing available skills
- **`cleanup() -> None`**: Removes the sandbox directory (optional cleanup)

#### Implementation Details

- **Directory Creation**: Automatically creates sandbox directory if it doesn't exist
- **Symbolic Links**: Creates symbolic link to skills directory at `sandbox_dir/skills`
- **Fallback**: If symbolic links are not supported, copies the skills directory instead
- **Cleanup**: Removes old symbolic links or directories before creating new ones

### History (Future)

The history module is designed for tracking execution history, though it may not be fully implemented in the current version.

#### Type Definitions

```python
@dataclass
class ExecutionRecord:
    """Single execution record"""
    timestamp: str
    type: str  # "python" | "shell"
    code: str
    status: str  # "success" | "error"
    stdout: str = ""
    stderr: str = ""
    error: str = ""
    traceback: str = ""
    metadata: dict[str, object] = field(default_factory=dict)
```

## Type Definitions

### ExecutionRecord

Represents a single execution record with all relevant information:

```python
@dataclass
class ExecutionRecord:
    timestamp: str
    type: str
    code: str
    status: str
    stdout: str
    stderr: str
    error: str
    traceback: str
    metadata: dict[str, object]
```

### ExecutionRecordData

TypedDict for execution record input data:

```python
class ExecutionRecordData(TypedDict, total=False):
    type: str
    code: str
    command: str
    status: str
    stdout: str
    stderr: str
    error: str
    traceback: str
    returncode: int
    metadata: dict[str, object]
```

## Sandbox Architecture

### Directory Structure

```
sandbox/
├── agent1/
│   ├── skills/          # Symbolic link to skills directory
│   └── ...             # Agent's working files
└── agent2/
    ├── skills/          # Symbolic link to skills directory
    └── ...             # Agent's working files
```

### Skills Linking

The sandbox creates a symbolic link (or copy) to the skills directory:

- **Symbolic Link**: Preferred method, allows skills to be updated without recreating sandbox
- **Copy Fallback**: If symbolic links are not supported (e.g., on Windows without admin rights), copies the directory instead

### Isolation

Each agent gets its own sandbox directory:
- Complete file system isolation
- Independent working directory
- Shared skills (via symbolic link or copy)

## Usage Patterns

### Agent Initialization

```python
from actium.infrastructure.sandbox import Sandbox

# In agent decorator
sandbox = Sandbox(
    sandbox_dir=agent_sandbox_dir,
    skills_dir=agent_skills_dir
)

# Sandbox is ready to use
# Skills are accessible at sandbox.sandbox_dir / "skills"
```

### Skills Access

Agents can access skills through the file system:

```python
# Skills are linked at sandbox_dir/skills
# Agent can explore and import:
from skills.web.http import fetch
```

### Cleanup

```python
# Optional cleanup (removes entire sandbox)
sandbox.cleanup()
```

## Implementation Details

### Symbolic Link Creation

```python
# Try to create symbolic link
try:
    self.skills_link.symlink_to(self.skills_dir)
except OSError:
    # Fallback to copy if symlink fails
    shutil.copytree(self.skills_dir, self.skills_link)
```

### Directory Management

- Uses `pathlib.Path` for path operations
- Automatically creates parent directories with `mkdir(parents=True, exist_ok=True)`
- Resolves paths to absolute paths for consistency

## Best Practices

1. **Separate Sandboxes**: Use different sandbox directories for different agents
2. **Skills Sharing**: Skills are shared via symbolic links, so updates propagate
3. **Cleanup**: Consider cleanup for temporary agents, but preserve sandboxes for persistent agents
4. **Path Resolution**: Always use resolved absolute paths for consistency

## See Also

- [Agent Module](./agent.md): How sandbox is used in agents
- [Skills Module](./skills.md): Skills system that sandbox links to
- [Execution Module](./execution.md): Execution sessions that use sandbox working directory

