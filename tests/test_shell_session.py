"""Tests for ShellSession"""

import pytest
from actium.execution.shell_session import ShellSession


@pytest.mark.asyncio
async def test_execute_simple_command(temp_dir):
    """测试执行简单命令"""
    session = ShellSession(str(temp_dir))
    
    result = await session.execute("echo hello")
    
    assert result.success is True
    assert "hello" in result.stdout


@pytest.mark.asyncio
async def test_error_handling(temp_dir):
    """测试错误处理"""
    session = ShellSession(str(temp_dir))
    
    result = await session.execute("false")  # 返回非零退出码
    
    assert result.success is False
    assert result.returncode != 0


@pytest.mark.asyncio
async def test_working_directory(temp_dir):
    """测试工作目录"""
    session = ShellSession(str(temp_dir))
    
    result = await session.execute("pwd")
    
    assert result.success is True
    assert str(temp_dir) in result.stdout

