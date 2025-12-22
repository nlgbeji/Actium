# setup_plot_style

设置高质量绘图样式

## 函数签名

```python
def setup_plot_style(style: str = 'seaborn-v0_8', palette: str = 'husl', font_scale: float = 1.0, dpi: int = 100, figsize: Optional[Tuple[float, float]] = None) -> None
```

## 参数

- `style`: Seaborn 样式名称，可选值包括 'darkgrid', 'whitegrid', 'dark', 'white', 'ticks', 'seaborn-v0_8' 等
- `palette`: 调色板名称，如 'husl', 'Set2', 'viridis', 'muted' 等
- `font_scale`: 字体缩放比例，用于调整标签和标题的大小
- `dpi`: 图表分辨率（每英寸点数），默认 100，高质量输出建议 300
- `figsize`: 默认图表尺寸 (width, height)，单位为英寸

## 返回值

None

## 示例

```python
setup_plot_style()
```

```python
setup_plot_style(style='seaborn-v0_8', palette='husl', font_scale=1.2)
```
