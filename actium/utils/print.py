"""流式响应打印工具，支持工具调用的格式化输出"""

import json
from typing import Any, List, Dict, Optional


class ToolCallAccumulator:
    """累积流式工具调用的状态管理器"""
    
    def __init__(self):
        self.tool_calls_buffer: List[Dict[str, Any]] = []
        self.is_accumulating = False
        self.finish_reason: Optional[str] = None
    
    def process_chunk(self, chunk: Any) -> bool:
        """
        处理流式 chunk，累积工具调用
        
        Args:
            chunk: 流式响应 chunk
            
        Returns:
            bool: 如果所有工具调用已完成，返回 True
        """
        if not (hasattr(chunk, "choices") and chunk.choices):
            return False
        
        choice = chunk.choices[0]
        
        # 检查 finish_reason
        if hasattr(choice, "finish_reason") and choice.finish_reason:
            self.finish_reason = choice.finish_reason
        
        if not (hasattr(choice, "delta") and choice.delta):
            return False
        
        delta = choice.delta
        
        # 处理文本内容
        if getattr(delta, "content", None):
            return False
        
        # 处理工具调用
        delta_tool_calls = getattr(delta, "tool_calls", None)
        if delta_tool_calls:
            self.is_accumulating = True
            for delta_tc in delta_tool_calls:
                index = delta_tc.index
                
                # 确保 buffer 长度足够
                while len(self.tool_calls_buffer) <= index:
                    self.tool_calls_buffer.append({
                        "id": None,
                        "type": "function",
                        "function": {"name": "", "arguments": ""}
                    })
                
                tc = self.tool_calls_buffer[index]
                
                # 更新 id（通常只在第一个 chunk 出现）
                if hasattr(delta_tc, "id") and delta_tc.id is not None:
                    tc["id"] = delta_tc.id
                
                # 更新 type（通常为 "function"）
                if hasattr(delta_tc, "type") and delta_tc.type is not None:
                    tc["type"] = delta_tc.type
                
                # 拼接 function.name（通常一次性出现，但为安全起见做拼接）
                if hasattr(delta_tc, "function") and hasattr(delta_tc.function, "name") and delta_tc.function.name:
                    tc["function"]["name"] += delta_tc.function.name
                
                # 拼接 function.arguments（JSON 字符串，可能分多次）
                if hasattr(delta_tc, "function") and hasattr(delta_tc.function, "arguments") and delta_tc.function.arguments:
                    tc["function"]["arguments"] += delta_tc.function.arguments
        
        # 检查是否完成（finish_reason 为 tool_calls 表示工具调用完成）
        if self.finish_reason == "tool_calls" or (self.finish_reason == "stop" and self.is_accumulating):
            return True
        
        return False
    
    def get_final_tool_calls(self) -> List[Dict[str, Any]]:
        """获取最终完整的工具调用列表"""
        return [
            {
                "id": tc["id"],
                "type": tc["type"],
                "function": {
                    "name": tc["function"]["name"],
                    "arguments": tc["function"]["arguments"],
                }
            }
            for tc in self.tool_calls_buffer if tc["function"]["name"]
        ]
    
    def print_tool_calls(self) -> None:
        """以人类可读的方式打印工具调用"""
        final_tool_calls = self.get_final_tool_calls()
        
        if not final_tool_calls:
            return
        
        print("\n🔧 工具调用:")
        for i, tc in enumerate(final_tool_calls, 1):
            name = tc["function"]["name"]
            args_str = tc["function"]["arguments"]
            
            try:
                # 尝试解析 JSON 参数
                args = json.loads(args_str) if args_str else {}
                
                # 格式化参数为人类可读格式
                if args:
                    # 将参数格式化为键值对
                    args_lines = []
                    for key, value in args.items():
                        # 处理长字符串（如代码）
                        if isinstance(value, str) and len(value) > 100:
                            value_display = value[:100] + "..."
                        else:
                            value_display = value
                        args_lines.append(f"  {key}: {json.dumps(value_display, ensure_ascii=False)}")
                    
                    args_display = "\n".join(args_lines)
                    print(f"{i}. {name}(\n{args_display}\n)")
                else:
                    print(f"{i}. {name}()")
                    
            except json.JSONDecodeError:
                # 如果 JSON 解析失败，显示原始字符串（可能是不完整的）
                if args_str:
                    print(f"{i}. {name}(...) — 参数解析中: {repr(args_str[:100])}...")
                else:
                    print(f"{i}. {name}()")
    
    def reset(self) -> None:
        """重置状态，准备处理新的工具调用"""
        self.tool_calls_buffer = []
        self.is_accumulating = False
        self.finish_reason = None


# 全局工具调用累积器实例（用于默认的 print_chunk 函数）
_default_accumulator = ToolCallAccumulator()


def print_chunk(chunk: Any, accumulator: Optional[ToolCallAccumulator] = None) -> None:
    """
    打印流式 chunk，自动处理文本内容和工具调用
    
    这个函数会自动累积工具调用，并在所有工具调用完成后以人类可读的格式打印。
    支持在 async for 循环中直接调用。
    
    Args:
        chunk: 流式响应 chunk
        accumulator: 可选的工具调用累积器实例。如果为 None，使用默认的全局实例。
                    如果需要独立的状态管理（例如多个并发流），可以传入自定义实例。
    
    Example:
        ```python
        async for raw_response, updated_history in agent("task"):
            print_chunk(raw_response)
            history = updated_history
        ```
    """
    acc = accumulator if accumulator is not None else _default_accumulator
    
    if hasattr(chunk, "choices") and chunk.choices:
        choice = chunk.choices[0]
        
        # 处理工具调用（需要检查整个 choice，而不仅仅是 delta）
        is_complete = acc.process_chunk(chunk)
        
        if hasattr(choice, "delta") and choice.delta:
            delta = choice.delta
            
            # 处理文本内容
            if getattr(delta, "content", None):
                print(delta.content, end="", flush=True)
                return
            
            # 如果所有工具调用已完成，打印它们
            if is_complete:
                acc.print_tool_calls()
                acc.reset()


def reset_accumulator(accumulator: Optional[ToolCallAccumulator] = None) -> None:
    """
    重置工具调用累积器状态
    
    在开始新的对话或响应时调用，确保状态干净。
    
    Args:
        accumulator: 可选的工具调用累积器实例。如果为 None，重置默认的全局实例。
    
    Example:
        ```python
        reset_accumulator()  # 重置默认累积器
        async for raw_response, updated_history in agent("new task"):
            print_chunk(raw_response)
        ```
    """
    acc = accumulator if accumulator is not None else _default_accumulator
    acc.reset()


def finish_accumulator(accumulator: Optional[ToolCallAccumulator] = None) -> None:
    """
    完成并打印累积的工具调用（如果还有未完成的）
    
    在流结束时调用，确保所有工具调用都被打印。
    
    Args:
        accumulator: 可选的工具调用累积器实例。如果为 None，使用默认的全局实例。
    
    Example:
        ```python
        async for raw_response, updated_history in agent("task"):
            print_chunk(raw_response)
        finish_accumulator()  # 确保所有工具调用都被打印
        ```
    """
    acc = accumulator if accumulator is not None else _default_accumulator
    if acc.is_accumulating:
        acc.print_tool_calls()
        acc.reset()

