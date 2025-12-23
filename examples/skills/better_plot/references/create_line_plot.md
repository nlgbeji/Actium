# create_line_plot

创建高质量的线图

## 函数签名

```python
def create_line_plot(x: Union[List[float], numpy.ndarray], y: Union[List[float], numpy.ndarray], title: Optional[str] = None, xlabel: Optional[str] = None, ylabel: Optional[str] = None, multiple_series: Optional[List[Union[List[float], numpy.ndarray]]] = None, labels: Optional[List[str]] = None, linewidth: float = 2.0, figsize: Tuple[float, float] = (10, 6)) -> Tuple[matplotlib.figure.Figure, matplotlib.axes._axes.Axes]
```

## 参数

- `x`: X 轴数据
- `y`: Y 轴数据（单条线时使用）
- `title`: 图表标题
- `xlabel`: X 轴标签
- `ylabel`: Y 轴标签
- `multiple_series`: 多条线的 Y 数据列表
- `labels`: 图例标签列表
- `linewidth`: 线宽
- `figsize`: 图表尺寸 (width, height)

## 返回值

包含 (Figure, Axes) 的元组

## 示例

```python
fig, ax = create_line_plot(x, y, title='趋势分析')
```

```python
fig, ax = create_line_plot(x, y, multiple_series=[y1, y2], labels=['系列1', '系列2'])
```
