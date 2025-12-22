"""Tests for IPythonSession"""

import pytest
from actium.execution.ipython_session import IPythonSession


@pytest.mark.asyncio
async def test_execute_simple_code(temp_dir):
    """测试执行简单代码"""
    session = IPythonSession(str(temp_dir))
    
    result = await session.execute("print('hello')")
    
    assert result.success is True
    assert "hello" in result.stdout


@pytest.mark.asyncio
async def test_variable_persistence(temp_dir):
    """测试变量持久化"""
    session = IPythonSession(str(temp_dir))
    
    # 第一次执行：定义变量
    await session.execute("x = 42")
    
    # 第二次执行：使用变量
    result = await session.execute("print(x)")
    
    assert result.success is True
    assert "42" in result.stdout


@pytest.mark.asyncio
async def test_error_handling(temp_dir):
    """测试错误处理"""
    session = IPythonSession(str(temp_dir))
    
    result = await session.execute("1 / 0")
    
    assert result.success is False
    assert result.error is not None


@pytest.mark.asyncio
async def test_timeout(temp_dir):
    """测试超时"""
    session = IPythonSession(str(temp_dir), timeout=1)
    
    result = await session.execute("import time; time.sleep(2)")
    
    assert result.success is False
    assert "timeout" in result.error.lower()

