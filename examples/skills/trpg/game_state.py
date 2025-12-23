"""TRPG 游戏状态管理函数"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from actium.skills import skill


@skill(category="state")
def save_game_state(state: Dict[str, Any], file_path: str = "game_state.json") -> None:
    """
    保存游戏状态到文件
    
    将游戏状态字典保存为 JSON 文件。
    
    Args:
        state: 游戏状态字典
        file_path: 保存路径（默认 "game_state.json"）
    
    Returns:
        None
    
    Example:
        >>> state = {"scene": "森林", "turn": 1}
        >>> save_game_state(state)
    """
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


@skill(category="state")
def load_game_state(file_path: str = "game_state.json") -> Dict[str, Any]:
    """
    从文件加载游戏状态
    
    从 JSON 文件加载游戏状态。
    
    Args:
        file_path: 文件路径（默认 "game_state.json"）
    
    Returns:
        游戏状态字典，如果文件不存在则返回空字典
    
    Example:
        >>> state = load_game_state()
        >>> print(state.get("scene"))
    """
    path = Path(file_path)
    
    if not path.exists():
        return {}
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


@skill(category="state")
def update_character_hp(character_name: str, new_hp: int, file_path: str = "game_state.json") -> None:
    """
    更新角色生命值
    
    更新指定角色的生命值，并保存到游戏状态文件。
    
    Args:
        character_name: 角色名称（如 "warrior"）
        new_hp: 新的生命值
        file_path: 游戏状态文件路径（默认 "game_state.json"）
    
    Returns:
        None
    
    Example:
        >>> update_character_hp("warrior", 15)
    """
    state = load_game_state(file_path)
    
    if "characters" not in state:
        state["characters"] = {}
    
    if character_name not in state["characters"]:
        state["characters"][character_name] = {}
    
    state["characters"][character_name]["hp"] = max(0, new_hp)
    
    save_game_state(state, file_path)


@skill(category="state")
def get_character_info(character_name: str, file_path: str = "game_state.json") -> Dict[str, Any]:
    """
    获取角色信息
    
    从游戏状态文件中获取指定角色的信息。
    
    Args:
        character_name: 角色名称（如 "warrior"）
        file_path: 游戏状态文件路径（默认 "game_state.json"）
    
    Returns:
        角色信息字典，如果角色不存在则返回空字典
    
    Example:
        >>> info = get_character_info("warrior")
        >>> print(info.get("hp"))
    """
    state = load_game_state(file_path)
    
    if "characters" not in state:
        return {}
    
    return state["characters"].get(character_name, {})

