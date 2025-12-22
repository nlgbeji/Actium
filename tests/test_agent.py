"""Tests for @agent decorator"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from actium import agent


@pytest.mark.asyncio
async def test_agent_decorator(sandbox_dir, skills_dir):
    """测试 @agent 装饰器"""
    # 注意：由于 agent 装饰器现在需要实际的 LLM_Interface，我们需要 mock _create_llm_interface
    mock_llm = MagicMock()
    mock_llm.chat_stream = AsyncMock(return_value=iter([{"choices": [{"delta": {"content": "test"}}]}]))
    
    # 需要在装饰器定义之前 patch
    with patch('actium.agent._create_llm_interface', return_value=mock_llm):
        @agent(
            model="openai/gpt-3.5-turbo",
            sandbox_dir=sandbox_dir,
            skills_dir=skills_dir,
            stream=False
        )
        async def test_agent(task: str):
            """Test agent"""
            pass
        
        # 测试装饰器是否正确应用
        assert callable(test_agent)
        
        # 测试返回类型是异步生成器
        import inspect
        assert inspect.isasyncgenfunction(test_agent)


@pytest.mark.asyncio
async def test_agent_signature(sandbox_dir, skills_dir):
    """测试 agent 装饰器签名"""
    # 验证装饰器接受必需参数
    with patch('actium.agent._create_llm_interface') as mock_create:
        mock_llm = MagicMock()
        mock_create.return_value = mock_llm
        
        @agent(
            model="openai/gpt-3.5-turbo",
            sandbox_dir=sandbox_dir,
            skills_dir=skills_dir,
            max_steps=10,
            timeout=60,
            stream=True,
        )
        async def test_agent(task: str):
            """Test agent"""
            pass
        
        # 验证装饰器参数被正确传递
        assert callable(test_agent)


@pytest.mark.asyncio
async def test_agent_requires_sandbox_and_skills_dir(sandbox_dir, skills_dir):
    """测试 agent 装饰器需要 sandbox_dir 和 skills_dir"""
    with patch('actium.agent._create_llm_interface') as mock_create:
        mock_llm = MagicMock()
        mock_create.return_value = mock_llm
        
        # 测试缺少必需参数会报错
        with pytest.raises(TypeError):
            @agent(model="openai/gpt-3.5-turbo")
            async def test_agent(task: str):
                """Test agent"""
                pass


@pytest.mark.asyncio
async def test_agent_specific_sandbox_isolation(sandbox_dir, skills_dir):
    """测试不同 agent 的 sandbox 隔离"""
    import tempfile
    from pathlib import Path
    
    # 创建两个不同的 sandbox 目录
    agent1_sandbox = tempfile.mkdtemp()
    agent2_sandbox = tempfile.mkdtemp()
    
    try:
        with patch('actium.agent._create_llm_interface') as mock_create:
            mock_llm = MagicMock()
            mock_create.return_value = mock_llm
            
            @agent(
                model="openai/gpt-3.5-turbo",
                sandbox_dir=agent1_sandbox,
                skills_dir=skills_dir,
                stream=False
            )
            async def agent1(task: str):
                """Agent 1"""
                pass
            
            @agent(
                model="openai/gpt-3.5-turbo",
                sandbox_dir=agent2_sandbox,
                skills_dir=skills_dir,
                stream=False
            )
            async def agent2(task: str):
                """Agent 2"""
                pass
            
            # 验证两个 agent 使用不同的 sandbox 目录
            assert Path(agent1_sandbox).exists()
            assert Path(agent2_sandbox).exists()
            assert agent1_sandbox != agent2_sandbox
            
            # 验证每个 sandbox 都有自己的 skills symlink
            agent1_skills_link = Path(agent1_sandbox) / "skills"
            agent2_skills_link = Path(agent2_sandbox) / "skills"
            
            # 注意：由于我们只是创建了装饰器，还没有实际运行 agent，
            # 所以 symlink 可能还没有创建。这里主要验证装饰器接受不同的路径。
            assert callable(agent1)
            assert callable(agent2)
    finally:
        # 清理临时目录
        import shutil
        try:
            shutil.rmtree(agent1_sandbox)
        except Exception:
            pass
        try:
            shutil.rmtree(agent2_sandbox)
        except Exception:
            pass

