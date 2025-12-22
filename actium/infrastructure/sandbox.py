"""Sandbox management for Actium"""

from pathlib import Path
from typing import Optional
import shutil


class Sandbox:
    """文件系统沙箱"""
    
    def __init__(self, sandbox_dir: str | Path, skills_dir: str | Path) -> None:
        """
        初始化文件系统沙箱
        
        Args:
            sandbox_dir: Sandbox 根目录路径
            skills_dir: Skills 目录路径
        """
        self.sandbox_dir = Path(sandbox_dir).resolve()
        self.skills_dir = Path(skills_dir).resolve()
        
        # 创建 sandbox 目录
        self.sandbox_dir.mkdir(parents=True, exist_ok=True)
        
        # Skills 目录（只读，通过符号链接或复制）- 放在 sandbox_dir 下以便访问
        self.skills_link = self.sandbox_dir / "skills"
        # 清理旧的符号链接或目录
        if self.skills_link.is_symlink():
            self.skills_link.unlink()
        elif self.skills_link.exists():
            shutil.rmtree(self.skills_link)
        
        # 创建符号链接（或复制）
        if self.skills_dir.exists():
            try:
                self.skills_link.symlink_to(self.skills_dir)
            except OSError:
                # 如果不支持符号链接，则复制
                shutil.copytree(self.skills_dir, self.skills_link)
    
    def list_skills(self) -> str:
        """
        列出可用 Skills（返回格式化字符串）
        
        Returns:
            格式化的 skills 信息
        """
        if not self.skills_dir.exists():
            return ""
        
        skills_info = []
        for skill_dir in sorted(self.skills_dir.iterdir()):
            if not skill_dir.is_dir():
                continue
            
            skill_name = skill_dir.name
            readme_path = skill_dir / "README.md"
            
            # 读取 README（前 400 字符）
            description = ""
            if readme_path.exists():
                try:
                    with open(readme_path, 'r', encoding='utf-8') as f:
                        description = f.read(400).strip()
                except Exception:
                    pass
            
            # 列出 Python 模块
            py_files = list(skill_dir.glob("*.py"))
            modules = [f.stem for f in py_files]
            
            skills_info.append(
                f"  {skill_name}:\n"
                f"    Description: {description}\n"
                f"    Modules: {', '.join(modules) if modules else 'None'}"
            )
        
        if skills_info:
            return "Skills 目录:\n" + "\n".join(skills_info)
        return ""
    
    def cleanup(self) -> None:
        """清理 sandbox（可选）"""
        if self.sandbox_dir.exists():
            shutil.rmtree(self.sandbox_dir)

