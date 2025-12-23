"""Skills spec 验证器"""

from pathlib import Path
from dataclasses import dataclass
from typing import List
import re
import yaml
from yaml import YAMLError


@dataclass
class ValidationResult:
    """验证结果"""
    is_valid: bool
    errors: List[str]


class SkillValidator:
    """验证 skill 是否符合 Skills spec"""
    
    def validate_name(self, name: str) -> bool:
        """验证 skill 名称是否符合规范
        
        Args:
            name: 要验证的名称
            
        Returns:
            是否符合规范
        """
        if not (1 <= len(name) <= 64):
            return False
        # 允许大小写字母、数字、连字符、下划线
        if not re.match(r'^[a-zA-Z0-9_-]+$', name):
            return False
        # 不允许连续的两个连字符（避免混淆）
        if '--' in name:
            return False
        return True
    
    def validate_skill(self, skill_path: Path) -> ValidationResult:
        """验证整个 skill 目录
        
        Args:
            skill_path: Skill 目录路径
            
        Returns:
            ValidationResult 对象
        """
        errors: List[str] = []
        
        # 检查 SKILL.md 是否存在
        skill_md = skill_path / "SKILL.md"
        if not skill_md.exists():
            errors.append("缺少必需文件: SKILL.md")
            return ValidationResult(False, errors)
        
        # 验证 SKILL.md 格式
        try:
            content = skill_md.read_text(encoding='utf-8')
            if not content.startswith('---'):
                errors.append("SKILL.md 必须以 YAML frontmatter 开头")
                return ValidationResult(False, errors)
            
            # 解析 frontmatter
            parts = content.split('---', 2)
            if len(parts) < 3:
                errors.append("SKILL.md frontmatter 格式错误")
                return ValidationResult(False, errors)
            
            frontmatter = yaml.safe_load(parts[1])
            if not frontmatter:
                errors.append("SKILL.md frontmatter 为空")
                return ValidationResult(False, errors)
            
            # 验证必需字段
            if 'name' not in frontmatter:
                errors.append("SKILL.md 缺少必需字段: name")
            elif not self.validate_name(frontmatter['name']):
                errors.append(f"SKILL.md name 字段不符合规范: {frontmatter['name']}")
            elif frontmatter['name'] != skill_path.name:
                errors.append(
                    f"SKILL.md name 字段 '{frontmatter['name']}' "
                    f"与目录名 '{skill_path.name}' 不匹配"
                )
            
            if 'description' not in frontmatter:
                errors.append("SKILL.md 缺少必需字段: description")
            elif not (1 <= len(frontmatter['description']) <= 1024):
                errors.append(
                    "SKILL.md description 字段长度必须在 1-1024 字符之间"
                )
            
            # 验证可选字段
            if 'compatibility' in frontmatter:
                compat = frontmatter['compatibility']
                if isinstance(compat, str) and len(compat) > 500:
                    errors.append("SKILL.md compatibility 字段长度不能超过 500 字符")
        
        except YAMLError as e:
            errors.append(f"SKILL.md YAML 解析错误: {e}")
        except Exception as e:
            errors.append(f"SKILL.md 读取错误: {e}")
        
        return ValidationResult(len(errors) == 0, errors)

