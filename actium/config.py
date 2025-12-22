"""Configuration for Actium"""

import os
from typing import Optional

from actium.config.types import GlobalConfig, RuntimeConfig

# 全局 config 实例
_global_config: Optional[GlobalConfig] = None


def set_global_config(config: GlobalConfig) -> None:
    """设置全局配置"""
    global _global_config
    _global_config = config


def get_global_config() -> GlobalConfig:
    """获取全局配置"""
    global _global_config
    if _global_config is None:
        # 尝试从环境变量初始化（向后兼容）
        sandbox_dir = os.getenv("ACTIUM_SANDBOX_DIR")
        skills_dir = os.getenv("ACTIUM_SKILLS_DIR")
        
        if not sandbox_dir or not skills_dir:
            raise ValueError(
                "全局 config 未设置，且环境变量也未设置。"
                "请通过 set_global_config() 设置全局配置，"
                "或设置 ACTIUM_SANDBOX_DIR 和 ACTIUM_SKILLS_DIR 环境变量。"
            )
        
        # 使用 Pydantic 创建配置（会自动验证和转换）
        _global_config = GlobalConfig(
            sandbox_dir=sandbox_dir,
            skills_dir=skills_dir,
        )
    
    return _global_config


def _create_llm_interface(
    model: str,
    provider_config_path: str = "provider.json"
) -> LLM_Interface:
    """
    从模型标识符创建 LLM_Interface（仅从 provider.json 加载）
    
    Args:
        model: 模型标识符（如 "openai/gpt-3.5-turbo" 或 "gpt-3.5-turbo"）
        provider_config_path: provider.json 配置文件路径
    
    Returns:
        LLM_Interface 实例
    
    Raises:
        FileNotFoundError: 如果 provider.json 文件不存在
        ValueError: 如果无法从配置文件中找到指定的模型
    """
    from SimpleLLMFunc import OpenAICompatible
    
    # 解析模型标识符
    if "/" in model:
        provider, model_name = model.split("/", 1)
    else:
        provider = "openai"
        model_name = model
    
    # 从配置文件加载
    try:
        all_models = OpenAICompatible.load_from_json_file(provider_config_path)
        if provider in all_models and model_name in all_models[provider]:
            return all_models[provider][model_name]
        else:
            raise ValueError(
                f"无法在配置文件 '{provider_config_path}' 中找到模型 '{provider}/{model_name}'。"
                f"请确保配置文件中包含该模型的配置。"
            )
    except FileNotFoundError:
        raise FileNotFoundError(
            f"配置文件 '{provider_config_path}' 不存在。"
            "请创建 provider.json 配置文件，参考 provider.json.example。"
        )
    except (KeyError, AttributeError, TypeError) as e:
        raise ValueError(
            f"配置文件 '{provider_config_path}' 格式错误或无法解析: {e}"
        )


# 为了向后兼容，从 types 模块导出类型
__all__ = ["GlobalConfig", "RuntimeConfig", "set_global_config", "get_global_config", "_create_llm_interface"]

