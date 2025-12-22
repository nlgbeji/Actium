"""Skills 开发辅助工具"""

from actium.skills.decorator import skill
from actium.skills.parser import discover_skills, read_properties, find_skill_md, SkillProperties
from actium.skills.prompt import to_prompt

__all__ = [
    "skill",
    "discover_skills",
    "read_properties",
    "find_skill_md",
    "SkillProperties",
    "to_prompt",
]

# CLI 入口（可选导入，避免在运行时依赖 click）
try:
    from actium.skills.cli import skills_cli
    __all__.append("skills_cli")
except ImportError:
    pass

