---
description: TRPG游戏工具集，包含骰子系统、规则判定和Agent定义
name: trpg
---

# trpg

TRPG（桌面角色扮演游戏）工具集，提供完整的骰子系统、D20 规则判定、游戏状态管理和多 Agent 协作支持。

## 功能特性

### 骰子系统
- **基础投骰**: 支持任意面数和数量的骰子
- **D20 系统**: 专门的 D20 投骰和优势/劣势机制
- **属性检定**: 支持属性调整值和熟练加值
- **攻击检定**: 支持优势、劣势和暴击判定
- **伤害投骰**: 支持复杂公式（如 "2d6+3"）

### 规则判定
- **属性调整值计算**: 根据属性值计算调整值
- **DC 判定**: 难度等级判定
- **护甲等级计算**: AC 计算
- **命中判定**: 攻击是否命中
- **伤害应用**: 生命值计算和死亡判定

### 游戏状态管理
- **状态持久化**: 通过 JSON 文件保存和加载游戏状态
- **角色管理**: 更新和查询角色信息
- **状态同步**: 多 Agent 共享游戏状态

### Agent 定义
- **GM Agent**: 游戏主持人，负责剧情生成和判定
- **Warrior Player Agent**: 战士角色 Agent
- **Wizard Player Agent**: 法师角色 Agent
- **Rogue Player Agent**: 盗贼角色 Agent

## 依赖

- Python >= 3.13
- actium >= 0.1.0

## 主要函数

### 骰子工具 (dice.py)

- `roll_dice(sides, count=1)`: 基础投骰
- `roll_d20()`: 投掷 D20
- `roll_with_advantage()`: 优势投骰
- `roll_with_disadvantage()`: 劣势投骰
- `roll_ability_check(ability_modifier, proficiency_bonus=0)`: 属性检定
- `roll_attack(attack_bonus, advantage=False, disadvantage=False)`: 攻击检定
- `roll_damage(dice_formula)`: 伤害投骰
- `parse_dice_formula(formula)`: 解析骰子公式

### 规则判定 (rules.py)

- `calculate_modifier(ability_score)`: 计算属性调整值
- `check_dc(roll_result, difficulty_class)`: DC 判定
- `calculate_ac(base_ac, dex_modifier, armor_bonus=0)`: 计算护甲等级
- `determine_hit(attack_roll, target_ac)`: 判定是否命中
- `apply_damage(current_hp, damage)`: 应用伤害

### 游戏状态 (game_state.py)

- `save_game_state(state, file_path="game_state.json")`: 保存游戏状态
- `load_game_state(file_path="game_state.json")`: 加载游戏状态
- `update_character_hp(character_name, new_hp, file_path="game_state.json")`: 更新角色生命值
- `get_character_info(character_name, file_path="game_state.json")`: 获取角色信息

### Agent (agents.py)

- `gm_agent(task, history=None)`: 游戏主持人 Agent
- `warrior_player_agent(task, history=None)`: 战士玩家 Agent
- `wizard_player_agent(task, history=None)`: 法师玩家 Agent
- `rogue_player_agent(task, history=None)`: 盗贼玩家 Agent

## 使用示例

### 基础骰子使用

```python
import sys
sys.path.append('skills/')
from trpg import roll_d20, roll_damage, roll_attack

# 投掷 D20
result = roll_d20()
print(f"D20 结果: {result}")

# 投掷伤害
damage = roll_damage("2d6+3")
print(f"伤害: {damage['total_damage']}")

# 攻击检定
attack = roll_attack(5, advantage=True)
print(f"攻击结果: {attack['total']}")
```

### 规则判定

```python
from trpg import calculate_modifier, check_dc, determine_hit

# 计算属性调整值
modifier = calculate_modifier(16)  # 返回 3

# DC 判定
result = check_dc(17, 15)  # 成功

# 命中判定
hit = determine_hit(18, 16)  # True
```

### 游戏状态管理

```python
from trpg import save_game_state, load_game_state, update_character_hp

# 保存游戏状态
state = {
    "scene": "黑暗森林",
    "turn": 1,
    "characters": {
        "warrior": {"hp": 20, "max_hp": 20}
    }
}
save_game_state(state)

# 加载游戏状态
state = load_game_state()

# 更新角色生命值
update_character_hp("warrior", 15)
```

### Agent 调用

```python
import sys
sys.path.append('skills/')
from trpg.agents import gm_agent, warrior_player_agent

# 调用 GM Agent（维护独立的 history）
gm_history = []
async for response, updated_history in gm_agent(
    "生成一个冒险场景",
    history=gm_history
):
    gm_history = updated_history
    # 处理响应...

# 调用 Player Agent（维护独立的 history）
warrior_history = []
async for response, updated_history in warrior_player_agent(
    "战士，你的行动是什么？",
    history=warrior_history
):
    warrior_history = updated_history
    # 处理响应...
```

## History 管理策略

本 skill 中的 Agent 使用**独立历史模式**：

- **每个 Agent 维护独立的 history**: 每个 Agent 有自己的对话历史，不与其他 Agent 共享
- **上下文摘要传递**: 通过显式的上下文摘要（而非完整 history）在 Agent 间传递信息
- **文件系统持久化**: 游戏状态通过 JSON 文件持久化，所有 Agent 可以读取

这种设计的好处：
- 避免 history 过长
- 每个 Agent 专注于自己的上下文
- 灵活控制信息传递
- 易于调试和追踪

## 详细文档

每个函数的详细文档和使用示例请查看 `references/` 目录下自动生成的文档文件。

