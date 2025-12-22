"""Configuration for Actium"""

from typing import Optional

from actium.config.types import GlobalConfig, RuntimeConfig
from SimpleLLMFunc.interface.llm_interface import LLM_Interface

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
        # 创建空的全局配置（用于未来扩展）
        _global_config = GlobalConfig()
    
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


# 导出所有公共 API
__all__ = ["GlobalConfig", "RuntimeConfig", "set_global_config", "get_global_config", "_create_llm_interface"]

