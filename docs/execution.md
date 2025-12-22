# Execution Module

The `execution` module provides persistent execution environments for Python and Shell code.

## Overview

The execution layer manages two types of execution sessions:
- **IPythonSession**: Persistent Python execution environment (like Jupyter notebook cells)
- **ShellSession**: Shell command execution in a fixed working directory

## Components

### IPythonSession

A persistent Python execution environment that maintains state across multiple code executions.

#### Features

- **Persistent State**: Variables, imports, and defined objects persist across executions
- **IPython Magic Commands**: Supports IPython magic commands (e.g., `%timeit`, `%%time`)
- **Working Directory**: Fixed working directory for file operations
- **Timeout Protection**: Configurable timeout for code execution
- **Error Handling**: Comprehensive error capture and reporting

#### Usage

```python
from actium.execution.ipython_session import IPythonSession

session = IPythonSession(working_dir="./sandbox", timeout=300)

# Execute code
result = await session.execute("x = 10\ny = 20\nprint(x + y)")
# result.success: True
# result.stdout: "30\n"
# Variables x and y are now available in subsequent executions

result = await session.execute("print(x * y)")
# result.stdout: "200\n"
```

#### Methods

- **`execute(code: str) -> PythonExecutionResult`**: Execute Python code asynchronously
- **`close() -> None`**: Clean up resources

#### Result Structure

```python
@dataclass
class PythonExecutionResult:
    success: bool
    stdout: str
    stderr: str
    error: Optional[str]
    traceback: Optional[str]
```

### ShellSession

A shell command execution environment with a fixed working directory.

#### Features

- **Fixed Working Directory**: All commands execute in the specified directory
- **Safe Command Parsing**: Uses `shlex.split` for safe command parsing
- **Timeout Protection**: Configurable timeout for command execution
- **Error Handling**: Captures stdout, stderr, and return codes

#### Usage

```python
from actium.execution.shell_session import ShellSession

session = ShellSession(working_dir="./sandbox", timeout=300)

# Execute shell command
result = await session.execute("ls -la")
# result.success: True
# result.stdout: "file listing..."
# result.returncode: 0
```

#### Methods

- **`execute(command: str) -> ShellExecutionResult`**: Execute shell command asynchronously
- **`close() -> None`**: Clean up resources

#### Result Structure

```python
@dataclass
class ShellExecutionResult:
    success: bool
    stdout: str
    stderr: str
    returncode: int
    error: Optional[str]
```

## Type Definitions

### PythonExecutionResult

```python
@dataclass
class PythonExecutionResult:
    """Python code execution result"""
    success: bool
    stdout: str
    stderr: str
    error: Optional[str]
    traceback: Optional[str]
```

### ShellExecutionResult

```python
@dataclass
class ShellExecutionResult:
    """Shell command execution result"""
    success: bool
    stdout: str
    stderr: str
    returncode: int
    error: Optional[str]
```

### Execution Records

For history tracking, the module defines execution record types:

```python
@dataclass
class PythonExecutionRecord:
    type: Literal["python"]
    code: str
    status: ExecutionStatus
    stdout: str
    stderr: str
    error: Optional[str]
    traceback: Optional[str]

@dataclass
class ShellExecutionRecord:
    type: Literal["shell"]
    command: str
    status: ExecutionStatus
    stdout: str
    stderr: str
    returncode: int
    error: Optional[str]
```

## Implementation Details

### IPythonSession Implementation

- Uses `IPython.core.interactiveshell.InteractiveShell` for code execution
- Captures stdout/stderr using `redirect_stdout` and `redirect_stderr`
- Executes code in a separate thread with timeout protection using `asyncio.wait_for`
- Maintains working directory in `sys.path` for module imports

### ShellSession Implementation

- Uses `asyncio.create_subprocess_exec` for command execution
- Parses commands with `shlex.split` for safe execution
- Sets `cwd` to the working directory
- Captures stdout/stderr asynchronously with timeout protection

### Timeout Handling

Both sessions implement timeout protection:
- IPythonSession: Uses `asyncio.wait_for` with configurable timeout
- ShellSession: Uses `asyncio.wait_for` on `process.communicate()`, kills process on timeout

### Error Handling

- Exceptions are caught and converted to result objects
- Tracebacks are captured for Python execution errors
- Return codes are captured for shell command execution

## Best Practices

1. **Always Close Sessions**: Use `async with` or explicitly call `close()` to clean up resources
2. **Handle Timeouts**: Set appropriate timeout values based on expected execution time
3. **Check Results**: Always check `result.success` before using execution results
4. **Persistent State**: Leverage persistent state in IPythonSession for incremental workflows

## See Also

- [Agent Module](./agent.md): How execution sessions are used in agents
- [Runtime Module](./runtime.md): Built-in tools that use execution sessions
- [Infrastructure Module](./infrastructure.md): Sandbox and resource management

