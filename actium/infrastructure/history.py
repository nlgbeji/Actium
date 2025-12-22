"""Execution history management for Actium"""

from typing import List, Optional, Any
from dataclasses import asdict
from datetime import datetime
import json

from actium.infrastructure.types import SerializedExecutionRecord, ExecutionRecord


class ExecutionHistory:
    """执行历史管理器"""
    
    def __init__(self) -> None:
        self.records: List[ExecutionRecord] = []
    
    def add_record(self, record_data: dict[str, Any]) -> None:
        """添加执行记录"""
        record = ExecutionRecord(
            timestamp=datetime.now().isoformat(),
            type=record_data.get("type", "unknown"),
            code=record_data.get("code") or record_data.get("command", ""),
            status=record_data.get("status", "unknown"),
            stdout=record_data.get("stdout", ""),
            stderr=record_data.get("stderr", ""),
            error=record_data.get("error", ""),
            traceback=record_data.get("traceback", ""),
            metadata=record_data.get("metadata", {})
        )
        self.records.append(record)
    
    def get_recent_summary(self, n: int = 5) -> str:
        """
        获取最近 N 条记录的摘要
        
        Args:
            n: 要获取的记录数量
        
        Returns:
            格式化的摘要文本
        """
        recent = self.records[-n:] if len(self.records) > n else self.records
        
        if not recent:
            return ""
        
        summary_parts = []
        for i, record in enumerate(recent, 1):
            summary_parts.append(
                f"  {i}. [{record.type}] {record.status}: "
                f"{record.code[:50]}..."
            )
            if record.status == "error":
                summary_parts.append(f"     Error: {record.error[:100]}")
        
        return "\n".join(summary_parts)
    
    def to_dict(self) -> List[SerializedExecutionRecord]:
        """转换为字典列表（用于序列化）"""
        return [asdict(record) for record in self.records]  # type: ignore[return-value]
    
    def save_to_file(self, filepath: str) -> None:
        """保存到文件"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
    
    @classmethod
    def load_from_file(cls, filepath: str) -> 'ExecutionHistory':
        """从文件加载"""
        history = cls()
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for record_data in data:
                history.records.append(ExecutionRecord(**record_data))
        return history

