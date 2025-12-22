"""Agent decorator for Actium"""

from typing import Callable, Any, Optional, AsyncGenerator, Tuple, List, Union, Awaitable, cast
from functools import wraps
from SimpleLLMFunc.llm_decorator import llm_chat
from SimpleLLMFunc.interface.llm_interface import LLM_Interface
from SimpleLLMFunc.type.decorator import HistoryList
from SimpleLLMFunc.tool import Tool
from actium.config import _create_llm_interface
from actium.runtime.builtin_tools import (
    execute_python,
    execute_shell,
    search_variables,
    set_sessions,
)
from actium.execution.ipython_session import IPythonSession
from actium.execution.shell_session import ShellSession
from actium.infrastructure.sandbox import Sandbox
from actium.skills.parser import discover_skills
from actium.skills.prompt import to_prompt
from pathlib import Path


def _build_system_prompt(user_prompt: str, skills_dir: Optional[Path] = None) -> str:
    """
    构建完整的 system prompt，合并用户自定义 prompt 和基础 prompt
    
    Args:
        user_prompt: 用户自定义的 prompt（来自函数 docstring）
        skills_dir: Skills 目录路径，如果为 None 则不包含 skills 信息
        
    Returns:
        完整的 system prompt
    """
    # 获取 skills 信息
    try:
        if skills_dir is not None:
            skills_dir_path = Path(skills_dir).resolve()
            skill_dirs = discover_skills(skills_dir_path)
            skills_prompt = to_prompt(skill_dirs) if skill_dirs else ""
        else:
            skills_prompt = ""
    except Exception:
        # 如果获取 skills 失败，继续执行但不包含 skills 信息
        skills_prompt = ""
    
    # 基础 prompt：环境描述、工具使用说明
    base_prompt = """## Working Environment

You are working in a **Jupyter notebook-like persistent execution environment**:
- **Python Execution Environment**: Variables, imported modules, and defined objects persist across multiple executions, just like cells in a Jupyter notebook
- **Shell Execution Environment**: Working directory is fixed to the sandbox directory
- **File System**: You have an independent sandbox directory for reading/writing files, and a skills directory containing available tools and functions

This means you can:
- Define functions, classes, and variables in one execution and reuse them in subsequent executions
- Import modules once and use them throughout the session
- Build up complex workflows incrementally, just like running multiple cells in a notebook

## Available Tools

You have access to the following builtin tools:

### execute_python(code: str)
Execute Python code in the persistent execution environment. The code runs in an IPython shell, so you can use IPython magic commands (e.g., `%timeit`, `%%time`). Variables and objects persist across calls.

### execute_shell(command: str)
Execute shell commands in the sandbox working directory. Use this for file operations, directory listings, and system commands.

### search_variables(pattern: str)
Search for variable names in the Python execution environment using a regular expression pattern. Useful for discovering what variables are available.

## Workflow

1. **Think**: Analyze the task and plan your steps
2. **Act**: Use tools to execute code or commands
3. **Observe**: Review execution results (stdout, stderr, error messages)
4. **Reflect**: Continue thinking or provide the final answer based on results

## Best Practices

- **Prefer Python**: For complex logic, data processing, and file operations, prioritize Python code
- **Shell for Simple Operations**: Use Shell for file listings, simple commands, etc.
- **Leverage Persistent Environment**: Define functions, classes, and variables that can be reused in subsequent steps
- **Check Execution Results**: Always review outputs and errors after each execution, adjust strategy accordingly
- **Execute Step by Step**: Break down complex tasks into multiple steps and complete them incrementally
- **Use Skills**: First explore available Skills using shell commands to view the file system, then utilize existing tools and functions

## Common Shell Commands

### File Browsing
- `ls -la` - List directory contents (including hidden files)
- `tree -L 2` - Display directory structure as a tree (2 levels deep)
- `find . -name "*.py"` - Search files by name

### File Content Viewing
- `cat file.txt` - View complete file
- `head -n 20 file.txt` - View first 20 lines
- `tail -n 20 file.txt` - View last 20 lines
- `head -n 50 file.txt | tail -n 20` - View lines 31-50
- `wc -l file.txt` - Count file lines

### Content Search
- `grep "pattern" file.txt` - Search in file
- `grep -r "pattern" dir/` - Recursively search directory
- `grep -n "pattern" file.txt` - Show matching line numbers
- `grep -C 3 "pattern" file.txt` - Show matches with 3 lines of context

## Additional Notes

- Variables and objects in Python code remain available in subsequent executions (like Jupyter cells)
- File operations use the sandbox directory as the working directory
- If execution fails, check error messages and correct your code
- You can call multiple tools in parallel if they are independent
"""
    
    # 添加 skills 信息
    if skills_prompt:
        base_prompt += f"\n\n## Available Skills\n\nThe following skills are available for use. Each skill provides specialized functionality that you can leverage by importing and using the provided functions.\n\n{skills_prompt}\n\nTo use a skill, first explore its location using shell commands to read the SKILL.md file, then import and use the functions as needed.\n"
    
    # 合并用户 prompt 和基础 prompt
    if user_prompt.strip():
        # 如果用户提供了自定义 prompt，将其放在前面，基础 prompt 作为补充
        return f"{user_prompt.strip()}\n\n{base_prompt}"
    else:
        # 如果用户没有提供，只使用基础 prompt
        return base_prompt


def agent(
    model: str,
    sandbox_dir: str,
    skills_dir: str,
    max_steps: int = 20,
    timeout: int = 300,
    stream: bool = True,
    provider_config_path: Optional[str] = None,
    **llm_kwargs: Any,
) -> Callable[
    [Callable[[str], Any]],
    Callable[[str], AsyncGenerator[Tuple[Any, HistoryList], None]]
]:
    """
    Agent 装饰器，基于 llm_chat 实现。
    
    Args:
        model: 模型标识符（如 "openai/gpt-4"）
        sandbox_dir: Sandbox 根目录路径（必需）
        skills_dir: Skills 目录路径（必需）
        max_steps: 最大执行步数（映射到 max_tool_calls）
        timeout: 单次执行超时时间（秒）
        stream: 是否启用流式输出
        provider_config_path: provider.json 配置文件路径
        **llm_kwargs: 透传给 llm_chat 的额外参数
        
    Returns:
        装饰后的异步生成器函数
    """
    
    # 创建 LLM_Interface
    provider_path = provider_config_path or "provider.json"
    llm_interface = _create_llm_interface(model, provider_path)
    
    # 解析路径
    agent_sandbox_dir = Path(sandbox_dir).resolve()
    agent_skills_dir = Path(skills_dir).resolve()
    
    # 构建 builtin tools（类型注解为 ToolkitList）
    builtin_tools: List[Union[Tool, Callable[..., Awaitable[Any]]]] = [
        execute_python,
        execute_shell,
        search_variables,
    ]
    
    def decorator(func: Callable[[str], Any]) -> Callable[[str], AsyncGenerator[Tuple[Any, HistoryList], None]]:
        # 获取函数 docstring 作为用户自定义 system prompt
        user_prompt = func.__doc__ or ""
        
        # 构建完整的 system prompt（合并基础 prompt 和用户自定义 prompt）
        # 使用 agent 特定的 skills_dir
        system_prompt = _build_system_prompt(user_prompt, skills_dir=agent_skills_dir)
        
        # 创建内部函数，用于 llm_chat
        # 注意：必须在装饰器应用之前设置 docstring，因为 llm_chat 装饰器会读取 docstring
        async def _agent_internal(task: str, history: Optional[HistoryList] = None):
            pass
        
        # 设置 docstring（作为 system prompt）- 必须在装饰器应用之前设置
        _agent_internal.__doc__ = system_prompt
        
        # 应用 llm_chat 装饰器
        _agent_internal_decorated = llm_chat(
            llm_interface=llm_interface,
            toolkit=builtin_tools,  # type: ignore[arg-type]
            max_tool_calls=max_steps,
            stream=stream,
            return_mode="raw",
            **llm_kwargs,
        )(_agent_internal)
        
        # 类型转换：确保类型检查器知道这是异步生成器函数
        # llm_chat 装饰器返回的是 AsyncGenerator，但类型推断可能有问题
        _agent_internal_typed = cast(
            Callable[[str, Optional[HistoryList]], AsyncGenerator[Tuple[Any, HistoryList], None]],
            _agent_internal_decorated
        )
        
        @wraps(func)
        async def wrapper(task: str) -> AsyncGenerator[Tuple[Any, HistoryList], None]:
            # 创建 Sandbox 实例（会自动创建目录和 symlink）
            sandbox = Sandbox(
                sandbox_dir=agent_sandbox_dir,
                skills_dir=agent_skills_dir
            )
            
            # 创建 sessions（使用 sandbox 目录作为工作目录）
            python_session = IPythonSession(
                working_dir=str(sandbox.sandbox_dir),
                timeout=timeout
            )
            shell_session = ShellSession(
                working_dir=str(sandbox.sandbox_dir),
                timeout=timeout
            )
            
            # 设置全局 sessions（供 builtin tools 使用）
            set_sessions(python_session, shell_session)
            
            try:
                # 调用 llm_chat 装饰的函数
                # llm_chat 会自动处理 history 参数
                history: HistoryList = []
                # llm_chat 装饰器会处理 history 参数，但类型检查器可能无法正确推断 ParamSpec
                async for response, updated_history in _agent_internal_typed(task, history=history):  # type: ignore[call-arg]
                    history = updated_history
                    yield response, updated_history
            finally:
                # 清理资源
                await python_session.close()
                await shell_session.close()
        
        return wrapper
    
    return decorator
