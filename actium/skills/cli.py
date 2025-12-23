"""CLI 命令实现"""

import click
from pathlib import Path
from typing import Optional
import yaml
from actium.skills.generator import SkillDocGenerator
from actium.skills.validator import SkillValidator
from actium.skills.templates import SKILL_MD_TEMPLATE, INIT_PY_TEMPLATE


@click.group()
def skills_cli():
    """Skills 开发辅助工具"""
    pass


@skills_cli.command()
@click.argument("name")
@click.option("--skills-dir", "-s", required=True, help="Skills 根目录路径")
@click.option("--description", "-d", help="Skill 描述")
@click.option("--license", "-l", help="许可证信息")
@click.option("--compatibility", "-c", help="兼容性要求")
def init(
    name: str,
    skills_dir: str,
    description: Optional[str],
    license: Optional[str],
    compatibility: Optional[str],
):
    """
    初始化一个新的 skill 目录

    创建符合 Skills spec 的基础结构：
    - SKILL.md (包含 YAML frontmatter)
    - __init__.py
    - docs/ 目录
    """
    # 验证名称
    validator = SkillValidator()
    if not validator.validate_name(name):
        click.echo(f"错误: skill 名称 '{name}' 不符合规范", err=True)
        click.echo("名称要求: 1-64字符，可包含大小写字母、数字、连字符、下划线，不能包含连续连字符")
        return

    # 解析 skills 目录
    skills_dir_path = Path(skills_dir).resolve()

    skill_path = skills_dir_path / name

    if skill_path.exists():
        click.echo(f"错误: skill '{name}' 已存在", err=True)
        return

    # 创建目录结构
    skill_path.mkdir(parents=True, exist_ok=True)
    (skill_path / "docs").mkdir(exist_ok=True)
    (skill_path / "scripts").mkdir(exist_ok=True)
    (skill_path / "references").mkdir(exist_ok=True)
    (skill_path / "assets").mkdir(exist_ok=True)

    # 创建 SKILL.md
    frontmatter = {
        "name": name,
        "description": description
        or f"Skill: {name}, detailed docs or reference could be found in references/ folder under ./skills/{name}",
    }
    if license:
        frontmatter["license"] = license
    if compatibility:
        frontmatter["compatibility"] = compatibility

    skill_md_content = SKILL_MD_TEMPLATE.format(
        frontmatter=yaml.dump(
            frontmatter, allow_unicode=True, default_flow_style=False
        ).strip(),
        body=f"# {name}\n\n在此添加 skill 的使用说明。\n",
    )
    (skill_path / "SKILL.md").write_text(skill_md_content, encoding="utf-8")

    # 创建 __init__.py
    init_py_content = INIT_PY_TEMPLATE.format(skill_name=name)
    (skill_path / "__init__.py").write_text(init_py_content, encoding="utf-8")

    click.echo(f"✓ 已创建 skill: {skill_path}")
    click.echo(f"  编辑 {skill_path / 'SKILL.md'} 添加详细说明")


@skills_cli.command()
@click.argument("skill_name")
@click.option("--skills-dir", "-s", required=True, help="Skills 根目录路径")
@click.option("--output", "-o", help="输出目录（默认: skill/<skill_name>/references）")
@click.option(
    "--format", "-f", type=click.Choice(["md", "json"]), default="md", help="文档格式"
)
def build_doc(skill_name: str, skills_dir: str, output: Optional[str], format: str):
    """
    为 skill 生成文档

    扫描 skill 目录下所有被 @skill 装饰的函数，生成独立文档文件。
    文档存放在 skill/docs/ 目录下。
    """
    skills_dir_path = Path(skills_dir).resolve()
    skill_path = skills_dir_path / skill_name
    if not skill_path.exists():
        click.echo(f"错误: skill '{skill_name}' 不存在", err=True)
        return

    # 生成文档
    generator = SkillDocGenerator()
    output_dir = Path(output) if output else skill_path / "references"

    try:
        generated_files = generator.generate(skill_path, output_dir, format=format)
        click.echo(f"✓ 已生成 {len(generated_files)} 个文档文件:")
        for file in generated_files:
            click.echo(f"  - {file}")
    except Exception as e:
        click.echo(f"错误: {e}", err=True)


@skills_cli.command()
@click.argument("skill_name")
@click.option("--skills-dir", "-s", required=True, help="Skills 目录路径")
def validate(skill_name: str, skills_dir: str):
    """验证 skill 是否符合 Skills spec"""
    skills_dir_path = Path(skills_dir).resolve()
    skill_path = skills_dir_path / skill_name
    if not skill_path.exists():
        click.echo(f"错误: skill '{skill_name}' 不存在", err=True)
        return

    validator = SkillValidator()
    result = validator.validate_skill(skill_path)

    if result.is_valid:
        click.echo(f"✓ Skill '{skill_name}' 验证通过")
    else:
        click.echo(f"✗ Skill '{skill_name}' 验证失败:", err=True)
        for error in result.errors:
            click.echo(f"  - {error}", err=True)
