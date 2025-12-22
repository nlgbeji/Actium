"""Actium - A Product-Ready CodeAct Agent Framework"""

__version__ = "0.1.0"
__all__ = ["agent"]


def __getattr__(name: str):
    """延迟导入，避免在导入 skills CLI 时触发 SimpleLLMFunc 的初始化"""
    if name == "agent":
        from actium.agent import agent
        return agent
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

