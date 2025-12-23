"""@skill 装饰器实现"""

from typing import Callable, Any, Optional, Awaitable, AsyncGenerator
from functools import wraps
import inspect


class SkillMetadata:
    """存储 skill 函数的元数据"""

    def __init__(
        self,
        name: str,
        description: str,
        category: Optional[str] = None,
        examples: Optional[list[str]] = None,
        params: Optional[dict[str, str]] = None,
        returns: Optional[str] = None,
    ):
        self.name = name
        self.description = description
        self.category = category
        self.examples = examples or []
        self.params = params or {}
        self.returns = returns
        self.func: Optional[Callable[..., Any]] = None
        self.module_path: Optional[str] = None


def skill(
    name: Optional[str] = None,
    description: Optional[str] = None,
    category: Optional[str] = None,
) -> Callable:
    """
    装饰器：标记一个函数为 skill，用于文档生成

    支持同步函数、异步函数和异步生成器函数。
    可以与其他装饰器（如 @agent）组合使用。

    Args:
        name: 函数名称（默认使用函数名）
        description: 函数描述（默认从 docstring 提取）
        category: 分类（如 'api', 'core', 'operations'）
        examples: 使用示例列表

    Returns:
        装饰器函数
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        # 从 docstring 提取信息
        doc = inspect.getdoc(func) or ""

        # 解析 docstring（支持 Google 风格）
        parsed_doc = _parse_docstring(doc)

        # 创建元数据
        metadata = SkillMetadata(
            name=name or func.__name__,
            description=description or parsed_doc.get("summary", ""),
            category=category,
            examples=parsed_doc.get("examples", []),
            params=parsed_doc.get("params", {}),
            returns=parsed_doc.get("returns", ""),
        )
        metadata.func = func
        metadata.module_path = func.__module__

        # 将元数据附加到原函数上
        func._skill_metadata = metadata  # type: ignore

        # 检测函数类型并创建相应的 wrapper
        if inspect.isasyncgenfunction(func):
            # 异步生成器函数（如 @agent 装饰后的函数）
            @wraps(func)
            async def async_gen_wrapper(
                *args: Any, **kwargs: Any
            ) -> AsyncGenerator[Any, None]:
                async for item in func(*args, **kwargs):
                    yield item

            async_gen_wrapper._skill_metadata = metadata  # type: ignore
            return async_gen_wrapper

        elif inspect.iscoroutinefunction(func):
            # 异步函数
            @wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Awaitable[Any]:
                return await func(*args, **kwargs)

            async_wrapper._skill_metadata = metadata  # type: ignore
            return async_wrapper

        else:
            # 同步函数
            @wraps(func)
            def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
                return func(*args, **kwargs)

            sync_wrapper._skill_metadata = metadata  # type: ignore
            return sync_wrapper

    return decorator


def _parse_docstring(doc: str) -> dict[str, Any]:
    """解析 docstring，提取参数、返回值、示例等信息

    Args:
        doc: docstring 内容

    Returns:
        解析后的字典，包含 summary, params, returns, examples
    """
    result = {
        "summary": "",
        "params": {},
        "returns": "",
        "examples": [],
    }

    if not doc:
        return result

    lines = doc.strip().split("\n")
    if lines:
        result["summary"] = lines[0].strip()

    # 简单的参数解析（支持 Google 风格）
    current_section = None
    current_example = []

    for line in lines[1:]:
        line = line.strip()
        if not line:
            if current_example:
                result["examples"].append("\n".join(current_example))
                current_example = []
            continue

        if line.startswith("Args:"):
            current_section = "args"
        elif line.startswith("Returns:"):
            current_section = "returns"
        elif line.startswith("Example:") or line.startswith("Examples:"):
            current_section = "examples"
        elif current_section == "args" and ":" in line:
            param_name = line.split(":")[0].strip()
            param_desc = ":".join(line.split(":")[1:]).strip()
            result["params"][param_name] = param_desc
        elif current_section == "returns":
            result["returns"] += line + " "
        elif current_section == "examples":
            current_example.append(line)

    if current_example:
        result["examples"].append("\n".join(current_example))

    result["returns"] = result["returns"].strip()
    return result
