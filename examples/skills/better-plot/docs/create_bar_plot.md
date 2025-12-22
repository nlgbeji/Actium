# create_bar_plot

创建高质量的柱状图

## 函数签名

```python
def create_bar_plot(categories: Union[List[str], numpy.ndarray], values: Union[List[float], numpy.ndarray], title: Optional[str] = None, xlabel: Optional[str] = None, ylabel: Optional[str] = None, horizontal: bool = False, color: Union[str, List[str], NoneType] = None, figsize: Tuple[float, float] = (8, 6)) -> Tuple[matplotlib.figure.Figure, matplotlib.axes._axes.Axes]
```

## 参数

- `categories`: 分类标签列表
- `values`: 对应的数值列表
- `title`: 图表标题
- `xlabel`: X 轴标签
- `ylabel`: Y 轴标签
- `horizontal`: 是否创建水平柱状图
- `color`: 柱状图颜色，可以是单个颜色字符串或颜色列表
- `figsize`: 图表尺寸 (width, height)

## 返回值

包含 (Figure, Axes) 的元组

## 示例

```python
fig, ax = create_bar_plot(categories, values, title='分类统计')
```

```python
fig, ax = create_bar_plot(categories, values, horizontal=True, color='steelblue')
```
