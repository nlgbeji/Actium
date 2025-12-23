"""Agent decorator for Actium"""

from typing import Callable, Any, Optional, AsyncGenerator, Tuple, List, Union, Awaitable, cast
from functools import wraps
from SimpleLLMFunc.llm_decorator import llm_chat
from SimpleLLMFunc.interface.llm_interface import LLM_Interface
from SimpleLLMFunc.type.decorator import HistoryList
from SimpleLLMFunc.tool import Tool
from SimpleLLMFunc.observability.langfuse_client import langfuse_client
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
    
    # 基础 prompt：环境描述、工具使用说明（XML 风格）
    base_prompt = """<environment>
<description>
You are working in a Jupyter notebook-like persistent execution environment with the following characteristics:
</description>
<features>
<feature name="Python Execution Environment">
Variables, imported modules, and defined objects persist across multiple executions, just like cells in a Jupyter notebook.
</feature>
<feature name="Shell Execution Environment">
Working directory is fixed to the sandbox directory.
</feature>
<feature name="File System">
You have an independent sandbox directory for reading/writing files, and a skills directory containing available tools and functions.
</feature>
</features>
<capabilities>
- Define functions, classes, and variables in one execution and reuse them in subsequent executions
- Import modules once and use them throughout the session
- Build up complex workflows incrementally, just like running multiple cells in a notebook
</capabilities>
</environment>

<tools>
<description>
You have access to the following builtin tools:
</description>
<tool name="execute_python">
<signature>execute_python(code: str)</signature>
<description>
Execute Python code in the persistent execution environment. The code runs in an IPython shell, so you can use IPython magic commands (e.g., `%timeit`, `%%time`). Variables and objects persist across calls.
</description>
</tool>
<tool name="execute_shell">
<signature>execute_shell(command: str)</signature>
<description>
Execute shell commands in the sandbox working directory. Use this for file operations, directory listings, and system commands.
</description>
</tool>
<tool name="search_variables">
<signature>search_variables(pattern: str)</signature>
<description>
Search for variable names in the Python execution environment using a regular expression pattern. Useful for discovering what variables are available.
</description>
</tool>
</tools>

<workflow>
<step number="1" name="Think">
Analyze the task and plan your steps
</step>
<step number="2" name="Act">
Use tools to execute code or commands
</step>
<step number="3" name="Observe">
Review execution results (stdout, stderr, error messages)
</step>
<step number="4" name="Reflect">
Continue thinking or provide the final answer based on results
</step>
</workflow>

<best_practices>
<practice priority="critical" name="Check Skills First">
**IMPORTANT**: Before starting any task, always check if there are available Skills that can help you complete the task faster. Skills are pre-built, tested, and optimized solutions. Using Skills can save significant time and effort compared to writing code from scratch. First explore available Skills using shell commands to view the file system, then read SKILL.md files to understand what each skill offers.
</practice>
<practice name="Prefer Python">
For complex logic, data processing, and file operations, prioritize Python code.
</practice>
<practice name="Shell for Simple Operations">
Use Shell for file listings, simple commands, etc.
</practice>
<practice name="Leverage Persistent Environment">
Define functions, classes, and variables that can be reused in subsequent steps.
</practice>
<practice name="Check Execution Results">
Always review outputs and errors after each execution, adjust strategy accordingly.
</practice>
<practice name="Execute Step by Step">
Break down complex tasks into multiple steps and complete them incrementally.
</practice>
</best_practices>

<shell_commands>
<category name="File Browsing">
<command>ls -la</command> - List directory contents (including hidden files)
<command>tree -L 2</command> - Display directory structure as a tree (2 levels deep)
<command>find . -name "*.py"</command> - Search files by name
</category>
<category name="File Content Viewing">
<command>cat file.txt</command> - View complete file
<command>head -n 20 file.txt</command> - View first 20 lines
<command>tail -n 20 file.txt</command> - View last 20 lines
<command>head -n 50 file.txt | tail -n 20</command> - View lines 31-50
<command>wc -l file.txt</command> - Count file lines
</category>
<category name="Content Search">
<command>grep "pattern" file.txt</command> - Search in file
<command>grep -r "pattern" dir/</command> - Recursively search directory
<command>grep -n "pattern" file.txt</command> - Show matching line numbers
<command>grep -C 3 "pattern" file.txt</command> - Show matches with 3 lines of context
</category>
</shell_commands>

<additional_notes>
- Variables and objects in Python code remain available in subsequent executions (like Jupyter cells)
- File operations use the sandbox directory as the working directory
- If execution fails, check error messages and correct your code
- You can call multiple tools in parallel if they are independent
</additional_notes>

<output_format>
<requirement priority="critical">
**IMPORTANT**: When providing output or responses to users, you must NOT include any XML tags in your output. Use plain text, markdown, or code blocks as appropriate, but never include XML tags like &lt;tag&gt; or &lt;/tag&gt; in your responses. The XML format is only used in this system prompt for structure - your actual output should be clean, readable text without any XML markup.
</requirement>
</output_format>
"""
    
    # 添加 skills 信息（XML 风格）
    if skills_prompt:
        skills_section = f"""
<skills>
<description>
Skills are pre-built, tested, and optimized Python modules that provide specialized functionality. They are organized in a structured format and can significantly speed up your work by providing ready-to-use solutions.
</description>

<what_are_skills>
<definition>
A Skill is a self-contained Python module directory that contains:
- SKILL.md: A markdown file with YAML frontmatter describing the skill (name, description, license, compatibility)
- Python modules: Implementation files (e.g., __init__.py, *.py files) containing the actual functions
- references/: Optional directory with detailed documentation for each function
- assets/: Optional directory with resources like images, templates, etc.
- scripts/: Optional directory with utility scripts
</definition>
<benefits>
- Pre-tested and optimized code
- Consistent API and documentation
- Reusable across different tasks
- Saves time compared to writing code from scratch
</benefits>
</what_are_skills>

<skill_structure>
<directory_structure>
A typical skill directory looks like this:
skill-name/
├── SKILL.md          # Main documentation with YAML frontmatter
├── __init__.py       # Python module entry point, exports functions
├── *.py              # Implementation files
├── references/       # Detailed function documentation (optional)
│   └── function_name.md
├── assets/           # Resources like images, templates (optional)
└── scripts/          # Utility scripts (optional)
</directory_structure>
<skill_md_format>
SKILL.md contains:
1. YAML frontmatter (between --- markers):
   - name: Skill name (must match directory name)
   - description: Brief description
   - license: License information (optional)
   - compatibility: Python version requirements (optional)
2. Markdown content:
   - Overview and features
   - Dependencies
   - Main functions list
   - Usage examples
   - Reference to detailed docs
</skill_md_format>
</skill_structure>

<how_to_read_skills>
<step number="1" name="Discover Skills">
First, explore the skills directory to see what's available:
- Use shell command: `ls -la /path/to/skills/` to list all skills
- Each subdirectory is a skill
</step>
<step number="2" name="Read SKILL.md">
For each skill you're interested in:
- Read the SKILL.md file: `cat /path/to/skill-name/SKILL.md`
- This gives you an overview of what the skill does, its features, and main functions
</step>
<step number="2.5" name="Plan Required Functions" priority="critical">
**CRITICAL**: Before reading reference documentation, you MUST first plan which functions you need.

**Planning Process**:
1. Based on your task and the SKILL.md overview, identify which specific functions you will need
2. **Output your plan**: Clearly list the functions you plan to use and why
   - Example: "I need to use `load_dataframe` to load the CSV file, `explore_dataframe` to understand the data structure, and `clean_dataframe` to handle missing values."
3. This planning step helps you:
   - Focus on relevant documentation only
   - Avoid reading unnecessary reference files
   - Have a clear execution strategy

**IMPORTANT**: Always output your function usage plan before proceeding to read reference documentation. This makes your approach more efficient and systematic.
</step>
<step number="3" name="Read Reference Documentation" priority="critical">
**CRITICAL**: For detailed function documentation, you MUST read the actual content of reference files, not just list the directory.

**DO NOT** just list the references/ directory and assume you know what's inside. You MUST read the full content of each relevant reference document.

**Targeted Reading Process** (based on your plan from step 2.5):
1. First, list available reference files: `ls /path/to/skill-name/references/`
2. **MUST READ**: For each function you planned to use (from your plan), read its complete reference document: `cat /path/to/skill-name/references/function_name.md`
   - Read ONLY the reference documents for functions you actually need
   - This targeted approach is more efficient than reading all references
3. Read the entire content carefully - these documents contain:
   - Detailed parameter descriptions and types
   - Parameter requirements and constraints
   - Return value specifications
   - Usage examples and patterns
   - Edge cases and error handling
   - Best practices

**IMPORTANT**: Merely listing the references/ directory is NOT sufficient. You must read the actual content of the reference documents before using any skill functions. However, you should read them in a targeted manner based on your function usage plan.
</step>
<step number="4" name="Examine Code">
If needed, examine the implementation:
- Check __init__.py to see what functions are exported
- Look at the implementation files to understand function signatures
</step>
</how_to_read_skills>

<how_to_use_skills>
<step number="1" name="Import the Skill Module">
Skills are Python modules, so you import them like any Python package.
The import path is relative to the skills directory.

Example:
```python
# If skill is at skills/better-pandas/
# first add skills/ folder to sys.path
import sys
sys.path.append('skills/')
from better_pandas import load_dataframe, explore_dataframe

# Or import the entire module
import better_pandas as bp
```
</step>
<step number="2" name="Use the Functions">
Call the functions as you would any Python function:

Example:
```python
# Load data using the skill
from better_pandas import load_dataframe
df = load_dataframe('data.csv')

# Use other functions from the skill
from better_pandas import explore_dataframe, clean_dataframe
info = explore_dataframe(df)
df_clean = clean_dataframe(df)
```
</step>
<step number="3" name="Check Function Signatures" priority="critical">
**CRITICAL**: Before using any skill function, you MUST read its reference documentation first.

**Required Process**:
1. **MUST READ FIRST**: Read the complete reference document for the function: `cat /path/to/skill-name/references/function_name.md`
   - This is the PRIMARY and REQUIRED source of information
   - Reference documents contain the most detailed and accurate information
2. Only after reading the reference document, you may optionally:
   - Use Python's help(): `help(function_name)`
   - Or inspect in code: `import inspect; print(inspect.signature(function_name))`

**IMPORTANT**: Do NOT skip reading the reference documentation. Listing the references/ directory or guessing function parameters is NOT acceptable. Always read the actual content of reference documents.
</step>
</how_to_use_skills>

<reminder priority="critical">
**IMPORTANT**: Always check if Skills can help you complete the task faster before writing code from scratch. Skills are optimized solutions that can save significant time and effort.
**IMPORTANT**: Always add skills/ folder to sys.path before importing skills.
**CRITICAL WORKFLOW**: 
1. First, plan which functions you need and output your plan
2. Then, read the complete content of reference documentation files for those planned functions
3. Merely listing the references/ directory is NOT sufficient - you must read the actual documentation content using commands like `cat /path/to/skill-name/references/function_name.md`
4. This planning-then-reading approach is more efficient and systematic than randomly exploring documentation
</reminder>

<available_skills>
{skills_prompt}
</available_skills>

<workflow_for_using_skills>
<step number="1">Before starting a task, check available skills using shell commands</step>
<step number="2">Read SKILL.md files to understand what each skill offers</step>
<step number="2.5" priority="critical">**MUST**: Plan which functions you need - output a clear plan listing the specific functions you will use and why. This helps you focus on relevant documentation.</step>
<step number="3" priority="critical">**MUST**: Based on your plan, read the COMPLETE CONTENT of relevant reference documents in references/ folder. Do NOT just list the directory - you must read the actual documentation files (e.g., `cat /path/to/skill-name/references/function_name.md`) to understand function parameters, usage, and examples. Read only the documents for functions you planned to use.</step>
<step number="4">Import and use the skill functions in your Python code</step>
<step number="5">Only write custom code if no suitable skill exists</step>
</workflow_for_using_skills>
</skills>
"""
        base_prompt += skills_section
    
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
        [Callable[..., Any]],
        Callable[[str, Optional[HistoryList]], AsyncGenerator[Tuple[Any, HistoryList], None]]
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
    
    def decorator(func: Callable[..., Any]) -> Callable[[str, Optional[HistoryList]], AsyncGenerator[Tuple[Any, HistoryList], None]]:
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
        async def wrapper(task: str, history: Optional[HistoryList] = None) -> AsyncGenerator[Tuple[Any, HistoryList], None]:
            # 创建与被装饰函数同名的 langfuse span
            with langfuse_client.start_as_current_observation(
                as_type="span",
                name=func.__name__,
                input={"task": task, "history": history},
                metadata={
                    "model": model,
                    "sandbox_dir": str(agent_sandbox_dir),
                    "skills_dir": str(agent_skills_dir),
                    "max_steps": max_steps,
                    "timeout": timeout,
                    "stream": stream,
                },
            ) as agent_span:
                try:
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
                        # 如果未提供 history，使用空列表；否则使用传入的 history
                        current_history: HistoryList = history if history is not None else []
                        
                        # 收集响应用于更新 span
                        collected_responses = []
                        final_history = None
                        
                        # llm_chat 装饰器会处理 history 参数，但类型检查器可能无法正确推断 ParamSpec
                        async for response, updated_history in _agent_internal_typed(task, history=current_history):  # type: ignore[call-arg]
                            collected_responses.append(response)
                            final_history = updated_history
                            current_history = updated_history
                            yield response, updated_history
                        
                        # 更新 langfuse span
                        agent_span.update(
                            output={
                                "responses": collected_responses,
                                "final_history": final_history,
                                "total_responses": len(collected_responses),
                            },
                        )
                    finally:
                        # 清理资源
                        await python_session.close()
                        await shell_session.close()
                except Exception as exc:
                    # 更新 span 错误信息
                    agent_span.update(
                        output={"error": str(exc)},
                    )
                    raise
        
        return wrapper
    
    return decorator
