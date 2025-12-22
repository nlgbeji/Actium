"""SKILL.md 解析器"""

from pathlib import Path
from typing import Optional
import yaml
from dataclasses import dataclass


@dataclass
class SkillProperties:
    """Skill 属性（从 SKILL.md frontmatter 提取）"""
    name: str
    description: str
    license: Optional[str] = None
    compatibility: Optional[str] = None
    metadata: Optional[dict[str, str]] = None
    allowed_tools: Optional[str] = None


def find_skill_md(skill_dir: Path) -> Optional[Path]:
    """查找 skill 目录中的 SKILL.md 文件
    
    Args:
        skill_dir: Skill 目录路径
        
    Returns:
        SKILL.md 文件路径，如果不存在则返回 None
    """
    skill_md = skill_dir / "SKILL.md"
    return skill_md if skill_md.exists() else None


def read_properties(skill_dir: Path) -> SkillProperties:
    """读取 skill 的 frontmatter 属性
    
    Args:
        skill_dir: Skill 目录路径
        
    Returns:
        SkillProperties 对象
        
    Raises:
        FileNotFoundError: SKILL.md 不存在
        ValueError: YAML 解析失败或缺少必需字段
    """
    skill_md = find_skill_md(skill_dir)
    if skill_md is None:
        raise FileNotFoundError(f"SKILL.md not found in {skill_dir}")
    
    content = skill_md.read_text(encoding='utf-8')
    
    # 解析 YAML frontmatter
    if not content.startswith('---'):
        raise ValueError(f"SKILL.md must start with YAML frontmatter (---)")
    
    parts = content.split('---', 2)
    if len(parts) < 3:
        raise ValueError(f"Invalid YAML frontmatter format in SKILL.md")
    
    try:
        frontmatter = yaml.safe_load(parts[1])
    except yaml.YAMLError as e:
        raise ValueError(f"Failed to parse YAML frontmatter: {e}")
    
    if not frontmatter:
        raise ValueError("YAML frontmatter is empty")
    
    # 验证必需字段
    if 'name' not in frontmatter:
        raise ValueError("Missing required field: name")
    if 'description' not in frontmatter:
        raise ValueError("Missing required field: description")
    
    return SkillProperties(
        name=frontmatter['name'],
        description=frontmatter['description'],
        license=frontmatter.get('license'),
        compatibility=frontmatter.get('compatibility'),
        metadata=frontmatter.get('metadata'),
        allowed_tools=frontmatter.get('allowed-tools'),
    )


def discover_skills(skills_dir: Path) -> list[Path]:
    """发现所有符合规范的 skill 目录
    
    Args:
        skills_dir: Skills 根目录路径
        
    Returns:
        符合规范的 skill 目录路径列表
    """
    if not skills_dir.exists():
        return []
    
    skill_dirs = []
    for item in skills_dir.iterdir():
        if not item.is_dir():
            continue
        
        # 检查是否有 SKILL.md
        skill_md = find_skill_md(item)
        if skill_md is None:
            continue
        
        # 尝试读取属性，验证是否符合规范
        try:
            props = read_properties(item)
            # 验证 name 与目录名匹配
            if props.name != item.name:
                continue
            skill_dirs.append(item)
        except (ValueError, FileNotFoundError):
            # 不符合规范，跳过
            continue
    
    return sorted(skill_dirs)

