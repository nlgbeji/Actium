# create_histogram

创建高质量的直方图

## 函数签名

```python
def create_histogram(data: Union[List[float], numpy.ndarray], title: Optional[str] = None, xlabel: Optional[str] = None, bins: int = 30, kde: bool = False, color: str = 'steelblue', alpha: float = 0.7, figsize: Tuple[float, float] = (8, 6)) -> Tuple[matplotlib.figure.Figure, matplotlib.axes._axes.Axes]
```

## 参数

- `data`: 要绘制直方图的数据
- `title`: 图表标题
- `xlabel`: X 轴标签
- `bins`: 直方图的箱数
- `kde`: 是否添加核密度估计曲线
- `color`: 直方图颜色
- `alpha`: 透明度
- `figsize`: 图表尺寸 (width, height)

## 返回值

包含 (Figure, Axes) 的元组

## 示例

```python
fig, ax = create_histogram(data, title='数据分布直方图')
```

```python
fig, ax = create_histogram(data, bins=30, kde=True, title='带密度曲线的直方图')
```
