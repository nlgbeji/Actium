"""trpg skill module"""

from .dice import (
    roll_dice,
    roll_d20,
    roll_with_advantage,
    roll_with_disadvantage,
    roll_ability_check,
    roll_attack,
    roll_damage,
    parse_dice_formula,
)
from .rules import (
    calculate_modifier,
    check_dc,
    calculate_ac,
    determine_hit,
    apply_damage,
)
from .game_state import (
    save_game_state,
    load_game_state,
    update_character_hp,
    get_character_info,
)
from .agents import (
    gm_agent,
    warrior_player_agent,
    wizard_player_agent,
    rogue_player_agent,
)

__all__ = [
    # Dice functions
    "roll_dice",
    "roll_d20",
    "roll_with_advantage",
    "roll_with_disadvantage",
    "roll_ability_check",
    "roll_attack",
    "roll_damage",
    "parse_dice_formula",
    # Rules functions
    "calculate_modifier",
    "check_dc",
    "calculate_ac",
    "determine_hit",
    "apply_damage",
    # Game state functions
    "save_game_state",
    "load_game_state",
    "update_character_hp",
    "get_character_info",
    # Agents
    "gm_agent",
    "warrior_player_agent",
    "wizard_player_agent",
    "rogue_player_agent",
]
