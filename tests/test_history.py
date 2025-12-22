"""Tests for ExecutionHistory"""

import pytest
from actium.infrastructure.history import ExecutionHistory, ExecutionRecord


def test_add_record():
    """测试添加执行记录"""
    history = ExecutionHistory()
    
    history.add_record({
        "type": "python",
        "code": "print('hello')",
        "status": "success",
        "stdout": "hello"
    })
    
    assert len(history.records) == 1
    assert history.records[0].type == "python"
    assert history.records[0].code == "print('hello')"
    assert history.records[0].status == "success"


def test_get_recent_summary():
    """测试获取最近摘要"""
    history = ExecutionHistory()
    
    # 添加多条记录
    for i in range(5):
        history.add_record({
            "type": "python",
            "code": f"code_{i}",
            "status": "success"
        })
    
    summary = history.get_recent_summary(3)
    assert "code_2" in summary or "code_3" in summary or "code_4" in summary


def test_to_dict():
    """测试转换为字典"""
    history = ExecutionHistory()
    history.add_record({
        "type": "python",
        "code": "test",
        "status": "success"
    })
    
    data = history.to_dict()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["type"] == "python"


def test_save_and_load(tmp_path):
    """测试保存和加载"""
    history = ExecutionHistory()
    history.add_record({
        "type": "python",
        "code": "test",
        "status": "success"
    })
    
    filepath = tmp_path / "history.json"
    history.save_to_file(str(filepath))
    
    loaded = ExecutionHistory.load_from_file(str(filepath))
    assert len(loaded.records) == 1
    assert loaded.records[0].code == "test"

