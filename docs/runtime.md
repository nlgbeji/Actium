# Runtime Module

The `runtime` module provides built-in tools that agents can use to execute code and interact with the execution environment.

## Overview

The runtime layer provides three built-in tools that are automatically available to all agents:
- **`execute_python`**: Execute Python code in a persistent IPython environment
- **`execute_shell`**: Execute shell commands in the sandbox directory
- **`search_variables`**: Search for variables in the Python execution environment

## Built-in Tools

### execute_python

Executes Python code in a persistent IPython execution environment.

#### Signature

```python
@tool(name="execute_python", description="执行 Python 代码")
async def execute_python(code: str) -> Dict[str, Any]
```

#### Parameters

- **`code`** (str): Python code string to execute

#### Returns

```python
{
    "success": bool,
    "stdout": str,
    "stderr": str,
    "error": Optional[str],
    "traceback": Optional[str]
}
```

#### Features

- **Persistent State**: Variables, imports, and defined objects persist across calls
- **IPython Magic Commands**: Supports IPython magic commands (e.g., `%timeit`, `%%time`)
- **Error Handling**: Captures exceptions, tracebacks, and error messages
- **Output Capture**: Captures stdout and stderr separately

#### Example Usage

```python
# Agent can call:
result = await execute_python("x = 10\ny = 20\nprint(x + y)")
# result: {"success": True, "stdout": "30\n", ...}

# Variables persist:
result = await execute_python("print(x * y)")
# result: {"success": True, "stdout": "200\n", ...}
```

### execute_shell

Executes shell commands in the sandbox working directory.

#### Signature

```python
@tool(name="execute_shell", description="执行 Shell 命令")
async def execute_shell(command: str) -> Dict[str, Any]
```

#### Parameters

- **`command`** (str): Shell command string to execute

#### Returns

```python
{
    "success": bool,
    "stdout": str,
    "stderr": str,
    "returncode": int,
    "error": Optional[str]
}
```

#### Features

- **Fixed Working Directory**: Commands execute in the sandbox directory
- **Safe Parsing**: Uses `shlex.split` for safe command parsing
- **Return Code**: Captures command return code
- **Error Handling**: Captures stderr and error messages

#### Example Usage

```python
# Agent can call:
result = await execute_shell("ls -la")
# result: {"success": True, "stdout": "file listing...", "returncode": 0, ...}

result = await execute_shell("cat file.txt")
# result: {"success": True, "stdout": "file contents...", ...}
```

### search_variables

Searches for variable names in the Python execution environment using regular expressions.

#### Signature

```python
@tool(name="search_variables", description="搜索 Python 执行环境中的变量")
async def search_variables(pattern: str) -> List[str]
```

#### Parameters

- **`pattern`** (str): Regular expression pattern to match variable names

#### Returns

- **`List[str]`**: Sorted list of matching variable names

#### Features

- **Regex Matching**: Uses regular expressions for flexible searching
- **Namespace Access**: Searches in IPython session's user namespace
- **Sorted Results**: Returns sorted list of matches
- **Error Handling**: Returns empty list on errors

#### Example Usage

```python
# Agent can call:
vars = await search_variables("^data_")
# vars: ["data_1", "data_2", "data_result"]

vars = await search_variables(".*result")
# vars: ["final_result", "intermediate_result"]
```

## Session Management

### Global Session State

The runtime module maintains global session instances:

```python
_python_session: Optional[IPythonSession] = None
_shell_session: Optional[ShellSession] = None
```

### Session Initialization

Sessions are initialized by the agent decorator:

```python
def set_sessions(python_session: IPythonSession, shell_session: ShellSession) -> None:
    """Set global session instances (called by agent decorator)"""
    global _python_session, _shell_session
    _python_session = python_session
    _shell_session = shell_session
```

### Session Usage

Tools check for session initialization:

```python
if _python_session is None:
    return {"success": False, "error": "Python session not initialized", ...}
```

## Tool Registration

Tools are registered with the LLM interface in the agent decorator:

```python
builtin_tools: List[Union[Tool, Callable[..., Awaitable[Any]]]] = [
    execute_python,
    execute_shell,
    search_variables,
]

@llm_chat(
    toolkit=builtin_tools,
    ...
)
```

## Implementation Details

### Tool Decorator

Tools use SimpleLLMFunc's `@tool` decorator:

```python
from SimpleLLMFunc.tool import tool

@tool(name="execute_python", description="执行 Python 代码")
async def execute_python(code: str) -> Dict[str, Any]:
    ...
```

### Error Handling

All tools implement comprehensive error handling:

- **Session Check**: Verify session is initialized
- **Exception Capture**: Catch and return errors in result format
- **Graceful Degradation**: Return error results instead of raising exceptions

### Type Safety

Tools use type hints for better IDE support and type checking:

```python
from typing import Dict, Any, List

async def execute_python(code: str) -> Dict[str, Any]:
    ...
```

## Best Practices

1. **Always Check Results**: Agents should check `success` field before using results
2. **Handle Errors**: Agents should handle error messages and tracebacks
3. **Use Appropriate Tool**: Choose Python for complex logic, Shell for simple operations
4. **Leverage Persistence**: Use persistent state in Python execution for incremental workflows

## See Also

- [Agent Module](./agent.md): How tools are registered and used
- [Execution Module](./execution.md): Execution sessions that tools use
- [Infrastructure Module](./infrastructure.md): Sandbox that provides working directory

