"""流式响应打印工具，支持工具调用的格式化输出"""

import json
from typing import Any, List, Dict, Optional, AsyncGenerator, Tuple


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
                        if isinstance(value, str):
                            # 如果包含换行符，使用多行格式显示
                            if "\n" in value:
                                # 多行字符串，使用缩进格式
                                indented_value = "\n".join(f"    {line}" for line in value.split("\n"))
                                args_lines.append(f"  {key}:\n{indented_value}")
                            else:
                                # 单行字符串，使用 JSON 格式（会转义特殊字符）
                                args_lines.append(f"  {key}: {json.dumps(value, ensure_ascii=False)}")
                        else:
                            # 非字符串类型，使用 JSON 格式
                            args_lines.append(f"  {key}: {json.dumps(value, ensure_ascii=False)}")
                    
                    args_display = "\n".join(args_lines)
                    print(f"{i}. {name}(\n{args_display}\n)")
                else:
                    print(f"{i}. {name}()")
                    
            except json.JSONDecodeError:
                # 如果 JSON 解析失败，显示原始字符串（可能是不完整的）
                if args_str:
                    print(f"{i}. {name}(...) — 参数解析中: {repr(args_str)}")
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


async def builtin_cli_print(
    generator: AsyncGenerator[Tuple[Any, List[Dict[str, Any]]], None]
) -> List[Dict[str, Any]]:
    """
    CLI 专用的流式打印函数，简化开发者体验
    
    自动处理工具调用累积、文本打印和状态管理，返回最终的对话历史。
    使用闭包封装 accumulator 和相关函数，确保状态隔离。
    
    Args:
        generator: 异步生成器，产生 (raw_response, updated_history) 元组
    
    Returns:
        List[Dict[str, Any]]: 最终的对话历史
    
    Example:
        ```python
        history = await builtin_cli_print(data_analyst_agent(user_input))
        ```
    """
    # 创建 accumulator 实例（闭包变量）
    accumulator = ToolCallAccumulator()
    accumulator.reset()
    
    # 跟踪已打印的 tool call（避免重复打印）
    printed_tool_call_indices: set[int] = set()
    tool_call_count = 0
    
    def _print_tool_call_name(index: int, name: str) -> None:
        """打印工具调用名称（首次检测到时）"""
        if index not in printed_tool_call_indices:
            printed_tool_call_indices.add(index)
            nonlocal tool_call_count
            tool_call_count += 1
            print(f"\n🔧 工具调用 {tool_call_count}: {name}()")
    
    def _update_tool_call_args(index: int, name: str, args_str: str) -> None:
        """更新工具调用的参数显示（实时显示参数生成进度）"""
        if index not in printed_tool_call_indices:
            return
        
        if not args_str:
            # 还没有参数
            return
        
        try:
            # 尝试解析 JSON 参数
            args = json.loads(args_str)
            
            # 参数已完整，显示完整参数
            args_lines = []
            for key, value in args.items():
                if isinstance(value, str):
                    # 如果包含换行符，使用多行格式显示
                    if "\n" in value:
                        # 多行字符串，使用缩进格式
                        indented_value = "\n".join(f"    {line}" for line in value.split("\n"))
                        args_lines.append(f"  {key}:\n{indented_value}")
                    else:
                        # 单行字符串，使用 JSON 格式（会转义特殊字符）
                        args_lines.append(f"  {key}: {json.dumps(value, ensure_ascii=False)}")
                else:
                    # 非字符串类型，使用 JSON 格式
                    args_lines.append(f"  {key}: {json.dumps(value, ensure_ascii=False)}")
            
            args_display = "\n".join(args_lines)
            # 使用 \r 清除当前行并重新打印
            print(f"\r🔧 工具调用 {tool_call_count}: {name}(\n{args_display}\n)", end="", flush=True)
        except json.JSONDecodeError:
            # JSON 解析失败，参数还在生成中，显示进度提示
            print(f"\r🔧 工具调用 {tool_call_count}: {name}(...) — 参数生成中", end="", flush=True)
    
    def _print_chunk(chunk: Any) -> None:
        """打印流式 chunk（使用闭包中的 accumulator）"""
        if hasattr(chunk, "choices") and chunk.choices:
            choice = chunk.choices[0]
            
            if hasattr(choice, "delta") and choice.delta:
                delta = choice.delta
                
                # 先累积工具调用数据
                is_complete = accumulator.process_chunk(chunk)
                
                # 处理工具调用（优先级高于文本内容）
                delta_tool_calls = getattr(delta, "tool_calls", None)
                if delta_tool_calls:
                    # 实时显示工具调用
                    for delta_tc in delta_tool_calls:
                        index = delta_tc.index
                        
                        if index < len(accumulator.tool_calls_buffer):
                            tc = accumulator.tool_calls_buffer[index]
                            name = tc["function"]["name"]
                            args_str = tc["function"]["arguments"]
                            
                            # 如果检测到新的 tool call name，立即打印
                            if name and index not in printed_tool_call_indices:
                                _print_tool_call_name(index, name)
                            
                            # 更新参数显示（如果已经打印过 name）
                            if name and index in printed_tool_call_indices:
                                _update_tool_call_args(index, name, args_str)
                    
                    # 如果所有工具调用已完成，换行并重置
                    if is_complete:
                        print()  # 换行
                        accumulator.reset()
                        printed_tool_call_indices.clear()
                        tool_call_count = 0
                    return
                
                # 处理文本内容（只有在没有 tool call 时）
                if getattr(delta, "content", None):
                    print(delta.content, end="", flush=True)
                    return
            
            # 处理 finish_reason（当没有 delta 但可能有 finish_reason 时）
            if hasattr(choice, "finish_reason") and choice.finish_reason:
                is_complete = accumulator.process_chunk(chunk)
                if is_complete:
                    print()  # 换行
                    accumulator.reset()
                    printed_tool_call_indices.clear()
                    tool_call_count = 0
    
    def _finish() -> None:
        """完成并打印累积的工具调用（使用闭包中的 accumulator）"""
        if accumulator.is_accumulating:
            # 确保所有 tool call 都已打印
            final_tool_calls = accumulator.get_final_tool_calls()
            for i, tc in enumerate(final_tool_calls):
                if i not in printed_tool_call_indices:
                    name = tc["function"]["name"]
                    if name:
                        _print_tool_call_name(i, name)
                        args_str = tc["function"]["arguments"]
                        _update_tool_call_args(i, name, args_str)
            print()  # 换行
            accumulator.reset()
            printed_tool_call_indices.clear()
            tool_call_count = 0
    
    # 处理流式响应
    history: List[Dict[str, Any]] = []
    last_history_length = 0
    printed_tool_results: set[str] = set()  # 跟踪已打印的工具结果（使用 tool_call_id）
    tool_call_id_to_name: Dict[str, str] = {}  # 映射 tool_call_id 到工具名称
    
    def _print_tool_result(tool_call_id: str, tool_name: str, result: Any) -> None:
        """打印工具执行结果"""
        if tool_call_id in printed_tool_results:
            return
        
        printed_tool_results.add(tool_call_id)
        
        # 格式化结果
        if isinstance(result, dict):
            # 如果是字典，尝试格式化
            result_lines = []
            for key, value in result.items():
                if isinstance(value, str):
                    if "\n" in value:
                        # 多行字符串
                        indented_value = "\n".join(f"    {line}" for line in value.split("\n"))
                        result_lines.append(f"  {key}:\n{indented_value}")
                    else:
                        result_lines.append(f"  {key}: {json.dumps(value, ensure_ascii=False)}")
                else:
                    result_lines.append(f"  {key}: {json.dumps(value, ensure_ascii=False)}")
            
            result_display = "\n".join(result_lines) if result_lines else "  (空结果)"
            print(f"\n✅ 工具执行结果 ({tool_name}):\n{result_display}")
        elif isinstance(result, str):
            # 如果是字符串
            if "\n" in result:
                indented_result = "\n".join(f"  {line}" for line in result.split("\n"))
                print(f"\n✅ 工具执行结果 ({tool_name}):\n{indented_result}")
            else:
                print(f"\n✅ 工具执行结果 ({tool_name}): {result}")
        else:
            # 其他类型，使用 JSON 格式化
            result_str = json.dumps(result, ensure_ascii=False, indent=2)
            print(f"\n✅ 工具执行结果 ({tool_name}):\n{result_str}")
    
    async for raw_response, updated_history in generator:
        # 在循环开始时检查是否有新的工具执行结果（tool 结果是在 llm_chat 内部添加的）
        if len(updated_history) > last_history_length:
            new_messages = updated_history[last_history_length:]
            
            # 检查新增的消息
            for msg in new_messages:
                if isinstance(msg, dict):
                    role = msg.get("role")
                    
                    # 如果是 assistant 消息，提取 tool_calls 信息，建立 tool_call_id 到工具名称的映射
                    if role == "assistant":
                        tool_calls = msg.get("tool_calls")
                        if tool_calls:
                            for tc in tool_calls:
                                if isinstance(tc, dict):
                                    tc_id = tc.get("id")
                                    tc_function = tc.get("function", {})
                                    if isinstance(tc_function, dict):
                                        tc_name = tc_function.get("name", "unknown")
                                        if tc_id and isinstance(tc_id, str):
                                            tool_call_id_to_name[tc_id] = tc_name
                    
                    # 检查是否是 tool 消息（包含工具执行结果）
                    if role == "tool":
                        # 这是工具执行结果消息
                        tool_call_id = msg.get("tool_call_id") or msg.get("id")
                        # 优先使用消息中的 name，否则从映射中查找
                        if tool_call_id and isinstance(tool_call_id, str):
                            name = msg.get("name") or tool_call_id_to_name.get(tool_call_id, "unknown")
                            content = msg.get("content", "")
                            
                            # 尝试解析 content（可能是 JSON 字符串）
                            try:
                                if isinstance(content, str):
                                    result = json.loads(content)
                                else:
                                    result = content
                                _print_tool_result(tool_call_id, name, result)
                            except (json.JSONDecodeError, TypeError):
                                # 如果不是 JSON，直接显示字符串
                                _print_tool_result(tool_call_id, name, content)
        
        # 打印当前的流式响应 chunk
        _print_chunk(raw_response)
        
        history = updated_history
        last_history_length = len(updated_history)
    
    # 流结束后，再次检查整个 history，确保没有遗漏的工具执行结果
    # 因为工具执行结果可能在流结束后才添加到 history
    
    # 遍历整个 history，查找所有 tool 消息
    for msg in history:
        if isinstance(msg, dict):
            role = msg.get("role")
            
            # 如果是 assistant 消息，提取 tool_calls 信息（补充映射）
            if role == "assistant":
                tool_calls = msg.get("tool_calls")
                if tool_calls:
                    for tc in tool_calls:
                        if isinstance(tc, dict):
                            tc_id = tc.get("id")
                            tc_function = tc.get("function", {})
                            if isinstance(tc_function, dict):
                                tc_name = tc_function.get("name", "unknown")
                                if tc_id and isinstance(tc_id, str):
                                    tool_call_id_to_name[tc_id] = tc_name
            
            # 检查是否是 tool 消息（包含工具执行结果）
            if role == "tool":
                tool_call_id = msg.get("tool_call_id") or msg.get("id")
                if tool_call_id and isinstance(tool_call_id, str):
                    # 如果还没有打印过，则打印
                    if tool_call_id not in printed_tool_results:
                        name = msg.get("name") or tool_call_id_to_name.get(tool_call_id, "unknown")
                        content = msg.get("content", "")
                        
                        try:
                            if isinstance(content, str):
                                result = json.loads(content)
                            else:
                                result = content
                            _print_tool_result(tool_call_id, name, result)
                        except (json.JSONDecodeError, TypeError):
                            _print_tool_result(tool_call_id, name, content)
    
    _finish()
    
    return history

