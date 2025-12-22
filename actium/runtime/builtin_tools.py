"""Builtin tools for Actium agent"""

from typing import List, Dict, Any, Optional
import re
from SimpleLLMFunc.tool import tool
from actium.execution.ipython_session import IPythonSession
from actium.execution.shell_session import ShellSession

# 全局 session 实例（在 AgentSession 中初始化）
_python_session: Optional[IPythonSession] = None
_shell_session: Optional[ShellSession] = None


def set_sessions(python_session: IPythonSession, shell_session: ShellSession) -> None:
    """设置全局 session 实例（由 AgentSession 调用）"""
    global _python_session, _shell_session
    _python_session = python_session
    _shell_session = shell_session


@tool(name="execute_python", description="执行 Python 代码")
async def execute_python(code: str) -> Dict[str, Any]:
    """
    在持久化 Python 执行环境中执行代码。
    
    Args:
        code: 要执行的 Python 代码字符串
        
    Returns:
        包含执行结果的字典：
        {
            "success": bool,
            "stdout": str,
            "stderr": str,
            "error": Optional[str],
            "traceback": Optional[str]
        }
    """
    if _python_session is None:
        return {
            "success": False,
            "error": "Python session not initialized",
            "stdout": "",
            "stderr": "",
            "traceback": None,
        }
    
    result = await _python_session.execute(code)
    return {
        "success": result.success,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "error": result.error,
        "traceback": result.traceback,
    }


@tool(name="execute_shell", description="执行 Shell 命令")
async def execute_shell(command: str) -> Dict[str, Any]:
    """
    在 sandbox 工作目录中执行 Shell 命令。
    
    Args:
        command: 要执行的 Shell 命令字符串
        
    Returns:
        包含执行结果的字典：
        {
            "success": bool,
            "stdout": str,
            "stderr": str,
            "returncode": int,
            "error": Optional[str]
        }
    """
    if _shell_session is None:
        return {
            "success": False,
            "error": "Shell session not initialized",
            "stdout": "",
            "stderr": "",
            "returncode": -1,
        }
    
    result = await _shell_session.execute(command)
    return {
        "success": result.success,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode,
        "error": result.error,
    }


@tool(name="search_variables", description="搜索 Python 执行环境中的变量")
async def search_variables(pattern: str) -> List[str]:
    """
    使用正则表达式搜索 Python 执行环境中的变量名。
    
    Args:
        pattern: 正则表达式模式，用于匹配变量名
        
    Returns:
        匹配的变量名列表
    """
    if _python_session is None:
        return []
    
    try:
        # 从 IPython session 的命名空间中获取所有变量
        namespace = _python_session.shell.user_ns
        
        # 使用正则表达式匹配
        regex = re.compile(pattern)
        matched_vars = [name for name in namespace.keys() if regex.search(name)]
        
        return sorted(matched_vars)
    except Exception:
        return []

