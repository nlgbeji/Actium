"""文档生成器"""

from pathlib import Path
from typing import List, Optional, TYPE_CHECKING
import importlib.util
import inspect

if TYPE_CHECKING:
    from actium.skills.decorator import SkillMetadata


class SkillDocGenerator:
    """生成 skill 函数的文档"""
    
    def generate(
        self, 
        skill_path: Path, 
        output_dir: Path, 
        format: str = "md"
    ) -> List[Path]:
        """
        扫描 skill 目录，生成所有 @skill 装饰函数的文档
        
        Args:
            skill_path: skill 目录路径
            output_dir: 输出目录
            format: 文档格式 ('md' 或 'json')
            
        Returns:
            生成的文件路径列表
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        generated_files = []
        
        # 扫描所有 Python 文件
        for py_file in skill_path.glob("*.py"):
            if py_file.name == "__init__.py":
                continue
            
            # 动态导入模块
            module_name = py_file.stem
            spec = importlib.util.spec_from_file_location(module_name, py_file)
            if spec is None or spec.loader is None:
                continue
            
            try:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # 查找所有被 @skill 装饰的函数
                for name, obj in inspect.getmembers(module, inspect.isfunction):
                    if hasattr(obj, '_skill_metadata'):
                        metadata = obj._skill_metadata
                        doc_file = self._generate_function_doc(
                            metadata, output_dir, format
                        )
                        if doc_file:
                            generated_files.append(doc_file)
            except Exception:
                # 跳过无法导入的模块
                continue
        
        return generated_files
    
    def _generate_function_doc(
        self, 
        metadata: "SkillMetadata",
        output_dir: Path, 
        format: str
    ) -> Optional[Path]:
        """为单个函数生成文档"""
        if format == "md":
            content = self._generate_markdown(metadata)
            filename = f"{metadata.name}.md"
        else:  # json
            import json
            content = json.dumps({
                "name": metadata.name,
                "description": metadata.description,
                "category": metadata.category,
                "params": metadata.params,
                "returns": metadata.returns,
                "examples": metadata.examples,
            }, indent=2, ensure_ascii=False)
            filename = f"{metadata.name}.json"
        
        output_file = output_dir / filename
        output_file.write_text(content, encoding='utf-8')
        return output_file
    
    def _generate_markdown(self, metadata: "SkillMetadata") -> str:
        """生成 Markdown 格式的文档"""
        lines = [
            f"# {metadata.name}",
            "",
            metadata.description,
            "",
        ]
        
        # 函数签名
        if metadata.func:
            sig = inspect.signature(metadata.func)
            lines.append("## 函数签名")
            lines.append("")
            lines.append("```python")
            lines.append(f"def {metadata.name}{sig}")
            lines.append("```")
            lines.append("")
        
        # 参数说明
        if metadata.params:
            lines.append("## 参数")
            lines.append("")
            for param, desc in metadata.params.items():
                lines.append(f"- `{param}`: {desc}")
            lines.append("")
        
        # 返回值
        if metadata.returns:
            lines.append("## 返回值")
            lines.append("")
            lines.append(metadata.returns)
            lines.append("")
        
        # 示例
        if metadata.examples:
            lines.append("## 示例")
            lines.append("")
            for example in metadata.examples:
                lines.append("```python")
                lines.append(example)
                lines.append("```")
                lines.append("")
        
        return "\n".join(lines)

