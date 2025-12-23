"""Shell execution session for Actium"""

import asyncio
import shlex
from pathlib import Path

from actium.execution.types import ShellExecutionResult


class ShellSession:
    """Shell 执行环境"""
    
    def __init__(self, working_dir: str, timeout: int = 300) -> None:
        """
        初始化 Shell 执行环境
        
        Args:
            working_dir: 工作目录路径
            timeout: 执行超时时间（秒）
        """
        self.working_dir = Path(working_dir).resolve()
        self.timeout = timeout
        
        # 确保工作目录存在
        self.working_dir.mkdir(parents=True, exist_ok=True)
    
    async def execute(self, command: str) -> ShellExecutionResult:
        """
        执行 Shell 命令
        
        Args:
            command: 要执行的 Shell 命令
        
        Returns:
            {
                "success": bool,
                "stdout": str,
                "stderr": str,
                "returncode": int,
                "error": Optional[str]
            }
        """
        try:
            # 检测是否包含 shell 操作符（&&, ||, |, >, <, ;, & 等）
            shell_operators = ['&&', '||', '|', '>', '<', ';', '&', '$', '`']
            needs_shell = any(op in command for op in shell_operators)
            
            if needs_shell:
                # 包含 shell 操作符，使用 shell=True 执行
                process = await asyncio.create_subprocess_shell(
                    command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=str(self.working_dir),
                    shell=True
                )
            else:
                # 不包含 shell 操作符，使用 shlex.split 安全地分割命令
                command_parts = shlex.split(command)
                if not command_parts:
                    return ShellExecutionResult(
                        success=False,
                        stdout="",
                        stderr="",
                        returncode=-1,
                        error="Empty command"
                    )
                
                # 异步执行 subprocess
                process = await asyncio.create_subprocess_exec(
                    *command_parts,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=str(self.working_dir),
                    shell=False  # 安全考虑
                )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=self.timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                return ShellExecutionResult(
                    success=False,
                    stdout="",
                    stderr="",
                    returncode=-1,
                    error=f"Command timeout after {self.timeout} seconds"
                )
            
            stdout_text = stdout.decode('utf-8', errors='replace')
            stderr_text = stderr.decode('utf-8', errors='replace')
            
            return ShellExecutionResult(
                success=process.returncode == 0,
                stdout=stdout_text,
                stderr=stderr_text,
                returncode=process.returncode or 0,
                error=None if process.returncode == 0 else f"Command failed with return code {process.returncode}"
            )
            
        except Exception as e:
            return ShellExecutionResult(
                success=False,
                stdout="",
                stderr="",
                returncode=-1,
                error=str(e)
            )
    
    async def close(self) -> None:
        """清理资源"""
        # Shell session 无需特殊清理
        pass

