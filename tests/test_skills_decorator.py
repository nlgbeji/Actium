"""Tests for @skill decorator"""

import pytest
from actium.skills.decorator import skill, SkillMetadata
from typing import AsyncGenerator


def test_skill_decorator_sync_function():
    """测试 @skill 装饰器装饰同步函数"""
    
    @skill(name="test_sync", description="Test sync function")
    def sync_func(x: int, y: int) -> int:
        """Add two numbers"""
        return x + y
    
    # 验证函数可以正常调用
    assert sync_func(1, 2) == 3
    
    # 验证元数据被附加
    assert hasattr(sync_func, '_skill_metadata')
    metadata = sync_func._skill_metadata
    assert isinstance(metadata, SkillMetadata)
    assert metadata.name == "test_sync"
    assert metadata.description == "Test sync function"


@pytest.mark.asyncio
async def test_skill_decorator_async_function():
    """测试 @skill 装饰器装饰异步函数"""
    
    @skill(name="test_async", description="Test async function")
    async def async_func(x: int, y: int) -> int:
        """Add two numbers asynchronously"""
        return x + y
    
    # 验证函数可以正常调用
    result = await async_func(1, 2)
    assert result == 3
    
    # 验证元数据被附加
    assert hasattr(async_func, '_skill_metadata')
    metadata = async_func._skill_metadata
    assert isinstance(metadata, SkillMetadata)
    assert metadata.name == "test_async"
    assert metadata.description == "Test async function"


@pytest.mark.asyncio
async def test_skill_decorator_async_generator():
    """测试 @skill 装饰器装饰异步生成器函数"""
    
    @skill(name="test_async_gen", description="Test async generator")
    async def async_gen_func(n: int) -> AsyncGenerator[int, None]:
        """Generate numbers from 0 to n"""
        for i in range(n):
            yield i
    
    # 验证函数可以正常调用
    results = []
    async for item in async_gen_func(3):
        results.append(item)
    assert results == [0, 1, 2]
    
    # 验证元数据被附加
    assert hasattr(async_gen_func, '_skill_metadata')
    metadata = async_gen_func._skill_metadata
    assert isinstance(metadata, SkillMetadata)
    assert metadata.name == "test_async_gen"
    assert metadata.description == "Test async generator"


@pytest.mark.asyncio
async def test_skill_with_agent_decorator(sandbox_dir, skills_dir):
    """测试 @skill 装饰器与 @agent 装饰器组合使用"""
    from unittest.mock import MagicMock, patch
    from actium import agent
    
    with patch('actium.agent._create_llm_interface') as mock_create:
        mock_llm = MagicMock()
        mock_create.return_value = mock_llm
        
        @skill(
            name="my_agent",
            description="A test agent",
            category="agent"
        )
        @agent(
            model="openai/gpt-3.5-turbo",
            sandbox_dir=sandbox_dir,
            skills_dir=skills_dir,
            stream=False
        )
        async def my_agent(task: str):
            """Test agent description"""
            pass
        
        # 验证函数是异步生成器
        import inspect
        assert inspect.isasyncgenfunction(my_agent)
        
        # 验证元数据被保留
        assert hasattr(my_agent, '_skill_metadata')
        metadata = my_agent._skill_metadata
        assert isinstance(metadata, SkillMetadata)
        assert metadata.name == "my_agent"
        assert metadata.description == "A test agent"
        assert metadata.category == "agent"


def test_skill_decorator_preserves_docstring():
    """测试 @skill 装饰器保留 docstring"""
    
    @skill()
    def func_with_doc():
        """This is a docstring"""
        pass
    
    assert func_with_doc.__doc__ == "This is a docstring"


def test_skill_decorator_extracts_params_from_docstring():
    """测试 @skill 装饰器从 docstring 提取参数信息"""
    
    @skill()
    def func_with_params(x: int, y: str) -> int:
        """Add x and y
        
        Args:
            x: First number
            y: Second string
        
        Returns:
            Sum of x and y
        """
        return x + int(y)
    
    metadata = func_with_params._skill_metadata
    assert "x" in metadata.params
    assert metadata.params["x"] == "First number"
    assert "y" in metadata.params
    assert metadata.params["y"] == "Second string"
    assert "Sum of x and y" in metadata.returns


@pytest.mark.asyncio
async def test_skill_decorator_with_examples():
    """测试 @skill 装饰器支持 examples 参数"""
    
    @skill(
        examples=[
            "result = my_func(1, 2)",
            "result = my_func(x=1, y=2)"
        ]
    )
    async def my_func(x: int, y: int) -> int:
        """Add two numbers"""
        return x + y
    
    metadata = my_func._skill_metadata
    assert len(metadata.examples) == 2
    assert "result = my_func(1, 2)" in metadata.examples
    assert "result = my_func(x=1, y=2)" in metadata.examples

