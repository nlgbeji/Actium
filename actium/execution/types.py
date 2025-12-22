"""Type definitions for execution module"""

from dataclasses import dataclass, asdict
from typing import Optional, Literal


@dataclass
class PythonExecutionResult:
    """Python 代码执行结果"""
    success: bool
    stdout: str
    stderr: str
    error: Optional[str]
    traceback: Optional[str]


@dataclass
class ShellExecutionResult:
    """Shell 命令执行结果"""
    success: bool
    stdout: str
    stderr: str
    returncode: int
    error: Optional[str]


ActionType = Literal["python", "shell"]
ExecutionStatus = Literal["success", "error"]


@dataclass
class PythonExecutionRecord:
    """Python 执行记录"""
    type: Literal["python"]
    code: str
    status: ExecutionStatus
    stdout: str
    stderr: str
    error: Optional[str]
    traceback: Optional[str]
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ShellExecutionRecord:
    """Shell 执行记录"""
    type: Literal["shell"]
    command: str
    status: ExecutionStatus
    stdout: str
    stderr: str
    returncode: int
    error: Optional[str]
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ErrorExecutionRecord:
    """错误执行记录"""
    type: str
    status: Literal["error"]
    error: str
    
    def to_dict(self) -> dict:
        return asdict(self)


ExecutionRecord = PythonExecutionRecord | ShellExecutionRecord | ErrorExecutionRecord
