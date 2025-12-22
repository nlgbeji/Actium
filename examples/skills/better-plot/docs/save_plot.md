# save_plot

保存图表到文件

## 函数签名

```python
def save_plot(fig: matplotlib.figure.Figure, filepath: Union[str, pathlib._local.Path], dpi: int = 300, format: Optional[str] = None, bbox_inches: str = 'tight') -> pathlib._local.Path
```

## 参数

- `fig`: matplotlib Figure 对象
- `filepath`: 保存路径
- `dpi`: 分辨率（每英寸点数），高质量输出建议 300
- `format`: 文件格式，如 'png', 'pdf', 'svg', 'jpg'。如果为 None，则从文件扩展名推断
- `bbox_inches`: 边界框设置，'tight' 表示自动裁剪空白边距

## 返回值

保存的文件路径

## 示例

```python
save_plot(fig, 'output.png')
```

```python
save_plot(fig, 'output.pdf', dpi=300, format='pdf')
```
