"""IPython execution session for Actium"""

import sys
import io
import traceback
import asyncio
import os
from contextlib import redirect_stdout, redirect_stderr
from typing import Optional
from pathlib import Path

try:
    from IPython.core.interactiveshell import InteractiveShell
except ImportError:
    raise ImportError(
        "IPython is required but not installed. "
        "Please install it with: pip install ipython"
    )

from actium.execution.types import PythonExecutionResult


class IPythonSession:
    """持久化 IPython 执行环境"""
    
    def __init__(self, working_dir: str, timeout: int = 300) -> None:
        """
        初始化 IPython 执行环境
        
        Args:
            working_dir: 工作目录路径
            timeout: 执行超时时间（秒）
        """
        self.working_dir = Path(working_dir).resolve()
        self.timeout = timeout
        
        # 创建独立的 IPython shell 实例
        self.shell = InteractiveShell.instance()
        # 或者创建独立实例（如果需要隔离）
        # self.shell = InteractiveShell()
        
        # 设置工作目录
        os.chdir(str(self.working_dir))
        
        # 添加工作目录到 sys.path
        working_dir_str = str(self.working_dir)
        if working_dir_str not in sys.path:
            sys.path.insert(0, working_dir_str)
    
    async def execute(self, code: str) -> PythonExecutionResult:
        """
        执行 Python 代码，支持优雅中断
        
        Args:
            code: 要执行的 Python 代码
            
        Returns:
            PythonExecutionResult: 执行结果
        """
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        
        try:
            # 捕获 stdout/stderr
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                # 在独立线程中执行（带超时）
                await asyncio.wait_for(
                    asyncio.to_thread(self._execute_sync, code),
                    timeout=self.timeout
                )
            
            return PythonExecutionResult(
                success=True,
                stdout=stdout_capture.getvalue(),
                stderr=stderr_capture.getvalue(),
                error=None,
                traceback=None
            )
            
        except asyncio.TimeoutError:
            return PythonExecutionResult(
                success=False,
                stdout=stdout_capture.getvalue(),
                stderr=stderr_capture.getvalue(),
                error=f"Execution timeout after {self.timeout} seconds",
                traceback=None
            )
        except Exception as e:
            tb = traceback.format_exc()
            return PythonExecutionResult(
                success=False,
                stdout=stdout_capture.getvalue(),
                stderr=stderr_capture.getvalue(),
                error=str(e),
                traceback=tb
            )
    
    def _execute_sync(self, code: str) -> None:
        """同步执行代码（在独立线程中运行）"""
        # 确保工作目录正确
        old_cwd = os.getcwd()
        try:
            os.chdir(str(self.working_dir))
            # 使用 IPython 的 run_cell 方法
            # store_history=True 保持历史记录
            result = self.shell.run_cell(code, store_history=True)
            # IPython 的 run_cell 返回 ExecutionResult，检查是否有错误
            if result.error_in_exec:
                # 如果有执行错误，抛出异常以便上层捕获
                raise result.error_in_exec
        finally:
            os.chdir(old_cwd)
    
    async def close(self) -> None:
        """清理资源，支持优雅中断"""
        # 移除工作目录
        working_dir_str = str(self.working_dir)
        if working_dir_str in sys.path:
            sys.path.remove(working_dir_str)
        # IPython shell 实例可以保留，不需要特殊清理

