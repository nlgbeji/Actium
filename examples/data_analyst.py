"""数据分析师 Agent - 单文件版本（包含 CLI 交互）"""

import asyncio
import sys
from pathlib import Path
from typing import Any, List, Dict, Optional

from actium.agent import agent
from actium.utils.print import builtin_cli_print
from SimpleLLMFunc.type.decorator import HistoryList

# 获取当前文件所在目录
_current_dir = Path(__file__).parent.resolve()

# 配置路径
SANDBOX_DIR = _current_dir.parent / "sandbox"
SKILLS_DIR = _current_dir / "skills"
PROVIDER_CONFIG = _current_dir / "provider.json"


@agent(
    model="openrouter/google/gemini-3-flash-preview",
    sandbox_dir=str(SANDBOX_DIR),
    skills_dir=str(SKILLS_DIR),
    max_steps=30,
    timeout=300,
    stream=True,
    provider_config_path=str(PROVIDER_CONFIG),
)
async def data_analyst_agent(task: str, history: Optional[HistoryList] = None):
    """
    你是一位专业的数据分析师，擅长使用 Python 进行数据分析和可视化。
    
    你的核心能力包括：
    - 数据清洗和预处理
    - 数据探索性分析（EDA）
    - 统计分析和假设检验
    - 数据可视化（使用 matplotlib、seaborn 等）
    - 使用可用的 Skills 工具（如 better-plot）创建高质量的图表
    
    工作流程：
    1. 理解用户的数据分析需求
    2. 检查数据文件是否存在，了解数据结构
    3. 进行必要的数据清洗和预处理
    4. 执行探索性数据分析
    5. 根据需求创建可视化图表
    6. 提供数据洞察和结论
    
    你可以使用 sandbox 目录来存储数据文件和生成的分析结果。
    你可以通过 shell 命令探索文件系统以及查看 skills 文档，使用 Python 代码进行数据分析。
    """
    pass


async def run_interactive_cli() -> None:
    """运行交互式 CLI"""
    print("=" * 60)
    print("数据分析师 Agent - 交互式 CLI")
    print("=" * 60)
    print("输入 'quit' 或 'exit' 退出，输入 'clear' 清空对话历史\n")
    
    history: List[Dict[str, Any]] = []
    
    while True:
        try:
            # 获取用户输入
            user_input = input("\n你: ").strip()
            
            if not user_input:
                continue
            
            # 处理退出命令
            if user_input.lower() in ("quit", "exit", "q"):
                print("\n再见！")
                break
            
            # 处理清空历史命令
            if user_input.lower() == "clear":
                history = []
                print("对话历史已清空")
                continue
            
            # 显示助手回复前缀
            print("助手: ", end="", flush=True)
            
            # 调用 Agent 并流式展示回复（传入 history 以保持上下文）
            history = await builtin_cli_print(data_analyst_agent(user_input, history=history))  # type: ignore[call-arg]
            
            # 换行
            print()
            
        except KeyboardInterrupt:
            print("\n\n中断操作，输入 'quit' 退出")
            continue
        except EOFError:
            print("\n\n再见！")
            break
        except Exception as e:
            print(f"\n错误: {e}")
            continue


def main() -> None:
    """主入口函数"""
    try:
        asyncio.run(run_interactive_cli())
    except KeyboardInterrupt:
        print("\n\n程序已退出")
        sys.exit(0)


if __name__ == "__main__":
    main()

