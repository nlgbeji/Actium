"""TRPG 多 Agent 协作游戏演示"""

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
SANDBOX_DIR = _current_dir / "sandbox"
SKILLS_DIR = _current_dir / "skills"
# provider.json 在 skills 目录下，使用绝对路径
PROVIDER_CONFIG = str((SKILLS_DIR / "provider.json").resolve())


@agent(
    model="openrouter/google/gemini-3-flash-preview",
    sandbox_dir=str(SANDBOX_DIR),
    skills_dir=str(SKILLS_DIR),
    max_steps=60,  # 需要更多步数来协调多个 Agent
    timeout=600,
    stream=True,
    provider_config_path=str(PROVIDER_CONFIG),
)
async def game_coordinator_agent(task: str, history: Optional[HistoryList] = None):
    """你是TRPG游戏的协调者，负责管理整个游戏流程。
    
    核心职责：
    1. 游戏流程管理：
       - 管理回合顺序
       - 协调玩家和GM的行动
       - 维护游戏状态文件（game_state.json）
    
    2. Agent 协调：
       - 调用 GM Agent (gm_agent) 生成剧情和场景
       - 调用 Player Agent 获取玩家角色的行动
       - 整合所有 Agent 的响应
    
    3. 与人类玩家互动：
       - 接收人类玩家的指令和行动
       - 展示游戏状态和剧情
       - 处理人类玩家与其他 Agent 的互动
    
    工作流程：
    1. 初始化游戏：
       - 如果是第一次，调用 GM Agent 生成初始场景
       - 初始化游戏状态文件
       - 让各个 Player Agent 介绍自己
    
    2. 游戏循环：
       a. 展示当前场景（调用 GM Agent）
       b. 收集所有玩家行动（人类玩家 + Player Agent）
       c. 调用 GM Agent 判定结果
       d. 更新游戏状态
    
    3. 使用 trpg skill 中的工具进行骰子判定和状态管理
    
    Agent 调用方式：
    你需要通过 execute_python 来调用其他 Agent。每个 Agent 维护独立的 history。
    
    示例代码：
    ```python
    # 1. 导入 Agent
    import sys
    sys.path.append('skills/')
    from trpg.agents import gm_agent, warrior_player_agent, wizard_player_agent, rogue_player_agent
    
    # 2. 准备上下文摘要（从游戏状态中提取）
    from trpg.game_state import load_game_state
    state = load_game_state()
    context_summary = f"当前场景: {state.get('scene', '未知')}, 回合: {state.get('turn', 0)}"
    
    # 3. 调用 GM Agent（传递其独立的 history）
    # 注意：history 需要在 Python 环境中维护
    # 首次调用时 history 为空列表 []
    gm_history = []  # 在 Python 环境中维护 GM 的独立历史
    gm_response = ""
    async for response, updated_history in gm_agent(
        f"{context_summary}\\n\\n生成场景描述",
        history=gm_history
    ):
        gm_history = updated_history
        # 提取响应文本（简化处理）
        if hasattr(response, 'choices') and response.choices:
            # 处理流式响应...
            pass
    
    # 4. 调用 Player Agent（传递其独立的 history）
    warrior_history = []  # 战士的独立历史
    warrior_response = ""
    async for response, updated_history in warrior_player_agent(
        f"{context_summary}\\n\\n战士，你的行动是什么？",
        history=warrior_history
    ):
        warrior_history = updated_history
        # 处理响应...
    ```
    
    重要提示：
    - 每个 Agent 都有自己独立的 history，需要在 Python 环境中维护
    - 使用文件系统（game_state.json）来持久化游戏状态
    - 通过上下文摘要传递信息，而不是共享完整 history
    - 使用 trpg skill 中的工具函数进行骰子判定和状态管理
    
    输出格式：
    - 清晰展示场景描述（来自 GM Agent）
    - 展示各玩家的行动（来自 Player Agent）
    - 展示判定结果和游戏状态更新
    - 使用分隔线区分不同部分
    """
    pass


async def run_interactive_trpg_game() -> None:
    """运行交互式 TRPG 游戏"""
    print("=" * 60)
    print("TRPG 多 Agent 协作游戏")
    print("=" * 60)
    print("玩家: 你（人类）")
    print("队友: 战士（Agent）、法师（Agent）、盗贼（Agent）")
    print("游戏主持: GM（Agent）")
    print("\n输入 'quit' 或 'exit' 退出，输入 'clear' 清空对话历史\n")
    
    coordinator_history: List[Dict[str, Any]] = []
    
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
                coordinator_history = []
                print("对话历史已清空")
                continue
            
            # 显示助手回复前缀
            print("\n游戏协调者: ", end="", flush=True)
            
            # 调用协调 Agent 并流式展示回复（传入 history 以保持上下文）
            coordinator_history = await builtin_cli_print(
                game_coordinator_agent(user_input, history=coordinator_history)  # type: ignore[call-arg]
            )
            
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
        asyncio.run(run_interactive_trpg_game())
    except KeyboardInterrupt:
        print("\n\n程序已退出")
        sys.exit(0)


if __name__ == "__main__":
    main()

