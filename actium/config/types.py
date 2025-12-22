"""Type definitions for config module"""

from dataclasses import dataclass, field
from typing import Optional, Union
from pathlib import Path
from pydantic import BaseModel, ConfigDict
from SimpleLLMFunc.interface.llm_interface import LLM_Interface


class GlobalConfig(BaseModel):
    """全局配置（目前为空，保留用于未来扩展）"""
    
    model_config = ConfigDict(
        frozen=True,  # 不可变配置
        validate_assignment=True,  # 赋值时验证
    )


@dataclass
class RuntimeConfig:
    """Runtime 配置（简化版）"""
    model: Union[str, LLM_Interface]
    sandbox_dir: str
    skills_dir: str
    max_steps: int = 20
    timeout: int = 300
    system_prompt: str = "You are a CodeAct agent."
    provider_config_path: str = "provider.json"
    llm_interface: Optional[LLM_Interface] = field(default_factory=lambda: None)
    
    def __post_init__(self) -> None:
        """初始化后处理"""
        import os
        from actium.config import _create_llm_interface
        
        # 解析路径为绝对路径
        self.sandbox_dir = str(Path(self.sandbox_dir).resolve())
        self.skills_dir = str(Path(self.skills_dir).resolve())
        
        # 3. 其他运行参数的环境变量覆盖（仅在使用默认值时生效）
        max_steps_env = os.getenv("ACTIUM_MAX_STEPS")
        if max_steps_env is not None and self.max_steps == 20:
            try:
                self.max_steps = int(max_steps_env)
            except ValueError:
                pass  # 保持原值
        
        timeout_env = os.getenv("ACTIUM_TIMEOUT")
        if timeout_env is not None and self.timeout == 300:
            try:
                self.timeout = int(timeout_env)
            except ValueError:
                pass
        
        # 4. 获取 provider.json 路径（环境变量优先，然后使用参数，最后使用默认值）
        # 这里将 None 或空字符串视为"未指定"
        if not self.provider_config_path:
            provider_env = os.getenv("SIMPLELLMFUNC_PROVIDER_CONFIG")
            self.provider_config_path = provider_env or "provider.json"
        
        # 创建 LLM_Interface（如果传入的是字符串）
        if isinstance(self.model, str):
            self.llm_interface = _create_llm_interface(
                self.model,
                provider_config_path=self.provider_config_path
            )
        else:
            self.llm_interface = self.model
