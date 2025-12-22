"""Type definitions for infrastructure module"""

from typing import Literal, Optional
from typing_extensions import TypedDict
from dataclasses import dataclass, field


ExecutionType = Literal["python", "shell", "unknown"]
ExecutionStatus = Literal["success", "error", "unknown"]


class ExecutionRecordData(TypedDict, total=False):
    """执行记录输入数据"""
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


class SerializedExecutionRecord(TypedDict):
    """序列化的执行记录"""
    timestamp: str
    type: str
    code: str
    status: str
    stdout: str
    stderr: str
    error: str
    traceback: str
    metadata: dict[str, object]


@dataclass
class ExecutionRecord:
    """单条执行记录"""
    timestamp: str
    type: str  # "python" | "shell"
    code: str
    status: str  # "success" | "error"
    stdout: str = ""
    stderr: str = ""
    error: str = ""
    traceback: str = ""
    metadata: dict[str, object] = field(default_factory=dict)

