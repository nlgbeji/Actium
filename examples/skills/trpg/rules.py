"""TRPG D20 规则判定函数"""

from typing import Dict, Any
from actium.skills import skill


@skill(category="rules")
def calculate_modifier(ability_score: int) -> int:
    """
    计算属性调整值
    
    根据属性值计算调整值，公式为 (ability_score - 10) // 2
    
    Args:
        ability_score: 属性值（如力量 16）
    
    Returns:
        属性调整值（如力量 16 对应 +3）
    
    Example:
        >>> calculate_modifier(16)
        3
        >>> calculate_modifier(8)
        -1
    """
    return (ability_score - 10) // 2


@skill(category="rules")
def check_dc(roll_result: int, difficulty_class: int) -> Dict[str, Any]:
    """
    DC 判定
    
    判定投掷结果是否达到或超过难度等级（DC）。
    
    Args:
        roll_result: 投掷结果（已包含所有调整值）
        difficulty_class: 难度等级（DC）
    
    Returns:
        包含判定结果的字典
    
    Example:
        >>> check_dc(17, 15)
        {'roll_result': 17, 'dc': 15, 'success': True, 'margin': 2}
    """
    success = roll_result >= difficulty_class
    margin = roll_result - difficulty_class if success else difficulty_class - roll_result
    
    return {
        "roll_result": roll_result,
        "dc": difficulty_class,
        "success": success,
        "margin": margin,
        "description": "成功" if success else f"失败（差 {margin} 点）"
    }


@skill(category="rules")
def calculate_ac(base_ac: int, dex_modifier: int, armor_bonus: int = 0) -> int:
    """
    计算护甲等级（AC）
    
    计算角色的护甲等级，公式为 base_ac + dex_modifier + armor_bonus
    
    Args:
        base_ac: 基础 AC（通常为 10）
        dex_modifier: 敏捷调整值
        armor_bonus: 护甲加值（默认 0）
    
    Returns:
        最终护甲等级
    
    Example:
        >>> calculate_ac(10, 2, 4)  # 基础 10 + 敏捷 +2 + 护甲 +4
        16
    """
    return base_ac + dex_modifier + armor_bonus


@skill(category="rules")
def determine_hit(attack_roll: int, target_ac: int) -> bool:
    """
    判定是否命中
    
    判定攻击投掷是否命中目标。
    
    Args:
        attack_roll: 攻击投掷结果（已包含所有调整值）
        target_ac: 目标护甲等级
    
    Returns:
        是否命中
    
    Example:
        >>> determine_hit(18, 16)
        True
        >>> determine_hit(14, 16)
        False
    """
    return attack_roll >= target_ac


@skill(category="rules")
def apply_damage(current_hp: int, damage: int) -> Dict[str, Any]:
    """
    应用伤害
    
    计算受到伤害后的生命值。
    
    Args:
        current_hp: 当前生命值
        damage: 受到的伤害值
    
    Returns:
        包含新生命值和是否死亡的字典
    
    Example:
        >>> apply_damage(20, 5)
        {'old_hp': 20, 'damage': 5, 'new_hp': 15, 'is_dead': False}
    """
    new_hp = max(0, current_hp - damage)
    is_dead = new_hp == 0
    
    return {
        "old_hp": current_hp,
        "damage": damage,
        "new_hp": new_hp,
        "is_dead": is_dead,
        "description": "死亡" if is_dead else f"剩余 {new_hp} 点生命值"
    }

