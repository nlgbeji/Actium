"""Tests for RuntimeConfig and GlobalConfig"""

import pytest
from actium.config import (
    RuntimeConfig,
    GlobalConfig,
    set_global_config,
    get_global_config,
    _create_llm_interface,
)


def test_global_config_creation():
    """测试全局配置创建"""
    config = GlobalConfig()
    assert config is not None


def test_set_and_get_global_config():
    """测试设置和获取全局配置"""
    config = GlobalConfig()
    set_global_config(config)
    
    retrieved_config = get_global_config()
    assert retrieved_config is not None


def test_config_creation_with_runtime_config(temp_dir, skills_dir):
    """测试 RuntimeConfig 直接接收路径参数"""
    from unittest.mock import MagicMock
    
    mock_llm = MagicMock()
    config = RuntimeConfig(
        model=mock_llm,
        sandbox_dir=temp_dir,
        skills_dir=skills_dir,
    )
    
    # RuntimeConfig 应该直接使用传入的路径
    from pathlib import Path
    assert Path(config.sandbox_dir).resolve() == Path(temp_dir).resolve()
    assert Path(config.skills_dir).resolve() == Path(skills_dir).resolve()
    assert config.max_steps == 20
    assert config.llm_interface == mock_llm


def test_create_llm_interface_from_provider_json(tmp_path):
    """测试从 provider.json 创建 LLM 接口"""
    import json
    from pathlib import Path
    
    # 创建测试用的 provider.json（使用 SimpleLLMFunc 要求的格式：列表）
    provider_config = {
        "openai": [
            {
                "model_name": "gpt-3.5-turbo",
                "api_keys": ["test-key"],
                "base_url": "https://api.openai.com/v1",
                "max_retries": 5,
                "retry_delay": 1.0,
                "rate_limit_capacity": 10,
                "rate_limit_refill_rate": 1.0
            }
        ]
    }
    
    provider_file = tmp_path / "provider.json"
    with open(provider_file, 'w') as f:
        json.dump(provider_config, f)
    
    # 测试加载
    llm = _create_llm_interface(
        "openai/gpt-3.5-turbo",
        provider_config_path=str(provider_file)
    )
    
    assert llm is not None


def test_create_llm_interface_file_not_found():
    """测试 provider.json 不存在的情况"""
    with pytest.raises(FileNotFoundError):
        _create_llm_interface(
            "openai/gpt-3.5-turbo",
            provider_config_path="nonexistent.json"
        )

