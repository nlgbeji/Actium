"""TRPG 骰子工具函数"""

import random
import re
from typing import List, Dict, Any, Tuple
from actium.skills import skill


@skill(category="dice")
def roll_dice(sides: int, count: int = 1) -> List[int]:
    """
    基础投骰函数
    
    投掷指定面数和数量的骰子。
    
    Args:
        sides: 骰子面数（如 6 表示 D6）
        count: 投掷次数（默认 1）
    
    Returns:
        每次投掷的结果列表
    
    Example:
        >>> roll_dice(6, 3)  # 投掷 3 次 D6
        [4, 2, 6]
    """
    if sides < 2:
        raise ValueError(f"骰子面数必须 >= 2，当前为 {sides}")
    if count < 1:
        raise ValueError(f"投掷次数必须 >= 1，当前为 {count}")
    
    return [random.randint(1, sides) for _ in range(count)]


@skill(category="dice")
def roll_d20() -> int:
    """
    投掷 D20 骰子
    
    Returns:
        D20 投掷结果（1-20）
    
    Example:
        >>> roll_d20()
        15
    """
    return random.randint(1, 20)


@skill(category="dice")
def roll_with_advantage() -> Dict[str, Any]:
    """
    优势投骰（投两次 D20，取较高值）
    
    Returns:
        包含两次投掷结果和最终结果的字典
    
    Example:
        >>> roll_with_advantage()
        {'rolls': [12, 18], 'result': 18, 'advantage': True}
    """
    roll1 = roll_d20()
    roll2 = roll_d20()
    result = max(roll1, roll2)
    
    return {
        "rolls": [roll1, roll2],
        "result": result,
        "advantage": True,
        "used_roll": "higher"
    }


@skill(category="dice")
def roll_with_disadvantage() -> Dict[str, Any]:
    """
    劣势投骰（投两次 D20，取较低值）
    
    Returns:
        包含两次投掷结果和最终结果的字典
    
    Example:
        >>> roll_with_disadvantage()
        {'rolls': [15, 8], 'result': 8, 'disadvantage': True}
    """
    roll1 = roll_d20()
    roll2 = roll_d20()
    result = min(roll1, roll2)
    
    return {
        "rolls": [roll1, roll2],
        "result": result,
        "disadvantage": True,
        "used_roll": "lower"
    }


@skill(category="dice")
def roll_ability_check(ability_modifier: int, proficiency_bonus: int = 0) -> Dict[str, Any]:
    """
    属性检定
    
    投掷 D20 并加上属性调整值和熟练加值。
    
    Args:
        ability_modifier: 属性调整值（如力量 +3）
        proficiency_bonus: 熟练加值（默认 0）
    
    Returns:
        包含投掷结果、调整值和总和的字典
    
    Example:
        >>> roll_ability_check(3, 2)  # 力量 +3，熟练 +2
        {'d20_roll': 12, 'ability_modifier': 3, 'proficiency_bonus': 2, 'total': 17}
    """
    d20_roll = roll_d20()
    total = d20_roll + ability_modifier + proficiency_bonus
    
    return {
        "d20_roll": d20_roll,
        "ability_modifier": ability_modifier,
        "proficiency_bonus": proficiency_bonus,
        "total": total,
        "is_critical": d20_roll == 20,
        "is_critical_failure": d20_roll == 1
    }


@skill(category="dice")
def roll_attack(attack_bonus: int, advantage: bool = False, disadvantage: bool = False) -> Dict[str, Any]:
    """
    攻击检定
    
    投掷攻击骰，支持优势和劣势。
    
    Args:
        attack_bonus: 攻击加值
        advantage: 是否使用优势（默认 False）
        disadvantage: 是否使用劣势（默认 False）
    
    Returns:
        包含投掷结果、加值和总和的字典
    
    Example:
        >>> roll_attack(5, advantage=True)
        {'d20_rolls': [12, 18], 'd20_result': 18, 'attack_bonus': 5, 'total': 23, 'advantage': True}
    """
    if advantage and disadvantage:
        # 优势和劣势同时存在时抵消
        advantage = False
        disadvantage = False
    
    if advantage:
        advantage_result = roll_with_advantage()
        d20_result = advantage_result["result"]
        d20_rolls = advantage_result["rolls"]
    elif disadvantage:
        disadvantage_result = roll_with_disadvantage()
        d20_result = disadvantage_result["result"]
        d20_rolls = disadvantage_result["rolls"]
    else:
        d20_result = roll_d20()
        d20_rolls = [d20_result]
    
    total = d20_result + attack_bonus
    
    result: Dict[str, Any] = {
        "d20_result": d20_result,
        "attack_bonus": attack_bonus,
        "total": total,
        "is_critical": d20_result == 20,
        "is_critical_failure": d20_result == 1
    }
    
    if advantage:
        result["d20_rolls"] = d20_rolls
        result["advantage"] = True
    elif disadvantage:
        result["d20_rolls"] = d20_rolls
        result["disadvantage"] = True
    
    return result


@skill(category="dice")
def parse_dice_formula(formula: str) -> Tuple[int, int, int]:
    """
    解析骰子公式
    
    解析 "XdY+Z" 格式的骰子公式。
    
    Args:
        formula: 骰子公式（如 "2d6+3" 或 "1d8-1"）
    
    Returns:
        (骰子数量, 骰子面数, 调整值) 的元组
    
    Example:
        >>> parse_dice_formula("2d6+3")
        (2, 6, 3)
        >>> parse_dice_formula("1d8-1")
        (1, 8, -1)
    """
    # 匹配 XdY+Z 或 XdY-Z 格式
    pattern = r'(\d+)d(\d+)([+-]?\d+)?'
    match = re.match(pattern, formula.lower().replace(' ', ''))
    
    if not match:
        raise ValueError(f"无效的骰子公式: {formula}。格式应为 XdY+Z 或 XdY-Z")
    
    count = int(match.group(1))
    sides = int(match.group(2))
    modifier_str = match.group(3) if match.group(3) else '0'
    modifier = int(modifier_str)
    
    if count < 1:
        raise ValueError(f"骰子数量必须 >= 1，当前为 {count}")
    if sides < 2:
        raise ValueError(f"骰子面数必须 >= 2，当前为 {sides}")
    
    return (count, sides, modifier)


@skill(category="dice")
def roll_damage(dice_formula: str) -> Dict[str, Any]:
    """
    伤害投骰
    
    根据骰子公式投掷伤害。
    
    Args:
        dice_formula: 骰子公式（如 "2d6+3" 表示 2 个 D6 + 3）
    
    Returns:
        包含每次投掷结果、总和和总伤害的字典
    
    Example:
        >>> roll_damage("2d6+3")
        {'rolls': [4, 5], 'dice_total': 9, 'modifier': 3, 'total_damage': 12}
    """
    count, sides, modifier = parse_dice_formula(dice_formula)
    
    rolls = roll_dice(sides, count)
    dice_total = sum(rolls)
    total_damage = dice_total + modifier
    
    return {
        "formula": dice_formula,
        "rolls": rolls,
        "dice_total": dice_total,
        "modifier": modifier,
        "total_damage": total_damage
    }

