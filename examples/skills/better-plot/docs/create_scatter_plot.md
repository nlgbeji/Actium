# create_scatter_plot

创建高质量的散点图

## 函数签名

```python
def create_scatter_plot(x: Union[List[float], numpy.ndarray], y: Union[List[float], numpy.ndarray], title: Optional[str] = None, xlabel: Optional[str] = None, ylabel: Optional[str] = None, hue: Union[List, numpy.ndarray, NoneType] = None, size: Union[List[float], numpy.ndarray, NoneType] = None, alpha: float = 0.7, figsize: Tuple[float, float] = (8, 6)) -> Tuple[matplotlib.figure.Figure, matplotlib.axes._axes.Axes]
```

## 参数

- `x`: X 轴数据
- `y`: Y 轴数据
- `title`: 图表标题
- `xlabel`: X 轴标签
- `ylabel`: Y 轴标签
- `hue`: 用于颜色映射的分类变量
- `size`: 用于大小映射的数值变量
- `alpha`: 透明度，范围 0-1
- `figsize`: 图表尺寸 (width, height)

## 返回值

包含 (Figure, Axes) 的元组

## 示例

```python
fig, ax = create_scatter_plot(x, y, title='数据分布')
```

```python
fig, ax = create_scatter_plot(x, y, hue=labels, size=values, alpha=0.6)
```
