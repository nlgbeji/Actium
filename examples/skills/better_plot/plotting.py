"""高质量绘图工具函数"""

from typing import Optional, Union, List, Dict, Any, Tuple
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
from actium.skills import skill


@skill(
    category="style",
)
def setup_plot_style(
    style: str = "seaborn-v0_8",
    palette: str = "husl",
    font_scale: float = 1.0,
    dpi: int = 100,
    figsize: Optional[Tuple[float, float]] = None,
) -> None:
    """
    设置高质量绘图样式

    配置 matplotlib 和 seaborn 的默认样式，使图表更加美观和专业。

    Args:
        style: Seaborn 样式名称，可选值包括 'darkgrid', 'whitegrid', 'dark', 'white', 'ticks', 'seaborn-v0_8' 等
        palette: 调色板名称，如 'husl', 'Set2', 'viridis', 'muted' 等
        font_scale: 字体缩放比例，用于调整标签和标题的大小
        dpi: 图表分辨率（每英寸点数），默认 100，高质量输出建议 300
        figsize: 默认图表尺寸 (width, height)，单位为英寸

    Returns:
        None

    Example:
        >>> setup_plot_style(style='whitegrid', palette='Set2', font_scale=1.2)
        >>> # 后续的图表将使用这些样式设置
    """
    sns.set_style(style)
    sns.set_palette(palette)
    sns.set_context("paper", font_scale=font_scale)

    plt.rcParams["figure.dpi"] = dpi
    plt.rcParams["savefig.dpi"] = dpi
    plt.rcParams["savefig.bbox"] = "tight"
    plt.rcParams["savefig.pad_inches"] = 0.1

    if figsize:
        plt.rcParams["figure.figsize"] = figsize


@skill(
    category="plotting",
)
def create_scatter_plot(
    x: Union[List[float], np.ndarray],
    y: Union[List[float], np.ndarray],
    title: Optional[str] = None,
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None,
    hue: Optional[Union[List, np.ndarray]] = None,
    size: Optional[Union[List[float], np.ndarray]] = None,
    alpha: float = 0.7,
    figsize: Tuple[float, float] = (8, 6),
) -> Tuple[plt.Figure, plt.Axes]:
    """
    创建高质量的散点图

    生成美观的散点图，支持颜色和大小映射，自动添加标签和标题。

    Args:
        x: X 轴数据
        y: Y 轴数据
        title: 图表标题
        xlabel: X 轴标签
        ylabel: Y 轴标签
        hue: 用于颜色映射的分类变量
        size: 用于大小映射的数值变量
        alpha: 透明度，范围 0-1
        figsize: 图表尺寸 (width, height)

    Returns:
        包含 (Figure, Axes) 的元组

    Example:
        >>> import numpy as np
        >>> x = np.random.randn(100)
        >>> y = np.random.randn(100)
        >>> fig, ax = create_scatter_plot(x, y, title='随机数据散点图')
    """
    fig, ax = plt.subplots(figsize=figsize)

    scatter_kwargs: Dict[str, Any] = {"alpha": alpha, "s": 50 if size is None else size}

    if hue is not None:
        scatter = ax.scatter(x, y, c=hue, **scatter_kwargs, cmap="viridis")
        plt.colorbar(scatter, ax=ax, label="类别")
    else:
        ax.scatter(x, y, **scatter_kwargs)

    if title:
        ax.set_title(title, fontsize=14, fontweight="bold", pad=15)
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=12)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=12)

    ax.grid(True, alpha=0.3, linestyle="--")
    plt.tight_layout()

    return fig, ax


@skill(
    category="plotting",
)
def create_line_plot(
    x: Union[List[float], np.ndarray],
    y: Union[List[float], np.ndarray],
    title: Optional[str] = None,
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None,
    multiple_series: Optional[List[Union[List[float], np.ndarray]]] = None,
    labels: Optional[List[str]] = None,
    linewidth: float = 2.0,
    figsize: Tuple[float, float] = (10, 6),
) -> Tuple[plt.Figure, plt.Axes]:
    """
    创建高质量的线图

    生成美观的线图，支持多条线，自动添加图例和网格。

    Args:
        x: X 轴数据
        y: Y 轴数据（单条线时使用）
        title: 图表标题
        xlabel: X 轴标签
        ylabel: Y 轴标签
        multiple_series: 多条线的 Y 数据列表
        labels: 图例标签列表
        linewidth: 线宽
        figsize: 图表尺寸 (width, height)

    Returns:
        包含 (Figure, Axes) 的元组

    Example:
        >>> x = np.linspace(0, 10, 100)
        >>> y = np.sin(x)
        >>> fig, ax = create_line_plot(x, y, title='正弦波')
    """
    fig, ax = plt.subplots(figsize=figsize)

    if multiple_series is not None:
        for i, series in enumerate(multiple_series):
            label = labels[i] if labels and i < len(labels) else f"系列 {i+1}"
            ax.plot(
                x, series, linewidth=linewidth, label=label, marker="o", markersize=4
            )
        if labels:
            ax.legend(loc="best", frameon=True, fancybox=True, shadow=True)
    else:
        ax.plot(x, y, linewidth=linewidth, marker="o", markersize=4)

    if title:
        ax.set_title(title, fontsize=14, fontweight="bold", pad=15)
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=12)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=12)

    ax.grid(True, alpha=0.3, linestyle="--")
    plt.tight_layout()

    return fig, ax


@skill(
    category="plotting",
)
def create_bar_plot(
    categories: Union[List[str], np.ndarray],
    values: Union[List[float], np.ndarray],
    title: Optional[str] = None,
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None,
    horizontal: bool = False,
    color: Optional[Union[str, List[str]]] = None,
    figsize: Tuple[float, float] = (8, 6),
) -> Tuple[plt.Figure, plt.Axes]:
    """
    创建高质量的柱状图

    生成美观的柱状图，支持水平和垂直方向，自动添加数值标签。

    Args:
        categories: 分类标签列表
        values: 对应的数值列表
        title: 图表标题
        xlabel: X 轴标签
        ylabel: Y 轴标签
        horizontal: 是否创建水平柱状图
        color: 柱状图颜色，可以是单个颜色字符串或颜色列表
        figsize: 图表尺寸 (width, height)

    Returns:
        包含 (Figure, Axes) 的元组

    Example:
        >>> categories = ['A', 'B', 'C', 'D']
        >>> values = [10, 20, 15, 25]
        >>> fig, ax = create_bar_plot(categories, values, title='分类统计')
    """
    fig, ax = plt.subplots(figsize=figsize)

    if horizontal:
        bars = ax.barh(categories, values, color=color)
        ax.set_xlabel(ylabel or "数值", fontsize=12)
        ax.set_ylabel(xlabel or "分类", fontsize=12)
        # 在水平柱状图上添加数值标签
        for i, (cat, val) in enumerate(zip(categories, values)):
            ax.text(val, i, f" {val}", va="center", fontsize=10)
    else:
        bars = ax.bar(categories, values, color=color)
        ax.set_xlabel(xlabel or "分类", fontsize=12)
        ax.set_ylabel(ylabel or "数值", fontsize=12)
        # 在垂直柱状图上添加数值标签
        for cat, val in zip(categories, values):
            ax.text(cat, val, f"{val}", ha="center", va="bottom", fontsize=10)

    if title:
        ax.set_title(title, fontsize=14, fontweight="bold", pad=15)

    ax.grid(True, alpha=0.3, linestyle="--", axis="y" if not horizontal else "x")
    plt.tight_layout()

    return fig, ax


@skill(
    category="plotting",
)
def create_histogram(
    data: Union[List[float], np.ndarray],
    title: Optional[str] = None,
    xlabel: Optional[str] = None,
    bins: int = 30,
    kde: bool = False,
    color: str = "steelblue",
    alpha: float = 0.7,
    figsize: Tuple[float, float] = (8, 6),
) -> Tuple[plt.Figure, plt.Axes]:
    """
    创建高质量的直方图

    生成美观的直方图，可选添加核密度估计曲线。

    Args:
        data: 要绘制直方图的数据
        title: 图表标题
        xlabel: X 轴标签
        bins: 直方图的箱数
        kde: 是否添加核密度估计曲线
        color: 直方图颜色
        alpha: 透明度
        figsize: 图表尺寸 (width, height)

    Returns:
        包含 (Figure, Axes) 的元组

    Example:
        >>> data = np.random.normal(0, 1, 1000)
        >>> fig, ax = create_histogram(data, kde=True, title='正态分布')
    """
    fig, ax = plt.subplots(figsize=figsize)

    if kde:
        sns.histplot(data, bins=bins, kde=True, color=color, alpha=alpha, ax=ax)
    else:
        ax.hist(
            data, bins=bins, color=color, alpha=alpha, edgecolor="black", linewidth=1.2
        )

    if title:
        ax.set_title(title, fontsize=14, fontweight="bold", pad=15)
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel("频数", fontsize=12)

    ax.grid(True, alpha=0.3, linestyle="--", axis="y")
    plt.tight_layout()

    return fig, ax


@skill(
    category="utility",
)
def save_plot(
    fig: plt.Figure,
    filepath: Union[str, Path],
    dpi: int = 300,
    format: Optional[str] = None,
    bbox_inches: str = "tight",
) -> Path:
    """
    保存图表到文件

    以高质量格式保存图表，支持多种格式。

    Args:
        fig: matplotlib Figure 对象
        filepath: 保存路径
        dpi: 分辨率（每英寸点数），高质量输出建议 300
        format: 文件格式，如 'png', 'pdf', 'svg', 'jpg'。如果为 None，则从文件扩展名推断
        bbox_inches: 边界框设置，'tight' 表示自动裁剪空白边距

    Returns:
        保存的文件路径

    Example:
        >>> fig, ax = create_scatter_plot(x, y)
        >>> save_plot(fig, 'scatter.png', dpi=300)
    """
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)

    fig.savefig(
        path,
        dpi=dpi,
        format=format,
        bbox_inches=bbox_inches,
        facecolor="white",
        edgecolor="none",
    )

    return path
