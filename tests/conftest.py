"""Pytest configuration for Actium tests"""

import pytest
import tempfile
import shutil
from pathlib import Path

# 配置 pytest-asyncio
pytest_plugins = ('pytest_asyncio',)


@pytest.fixture
def temp_dir():
    """创建临时目录"""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def sandbox_dir(temp_dir):
    """创建测试用的 sandbox 目录路径"""
    return str(Path(temp_dir).resolve() / "sandbox")


@pytest.fixture
def skills_dir(temp_dir):
    """创建测试用的 skills 目录"""
    skills_path = Path(temp_dir) / "skills"
    skills_path.mkdir()
    
    # 创建一个示例 skill
    web_skill = skills_path / "web"
    web_skill.mkdir()
    
    # 创建 README
    (web_skill / "README.md").write_text("Web utilities for HTTP requests")
    
    # 创建 Python 模块
    (web_skill / "http.py").write_text("def fetch(url): pass")
    
    return str(skills_path.resolve())

