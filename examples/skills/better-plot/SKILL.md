---
description: A set of functions to help you create high quality plots through matplotlib and seaborn
name: better-plot
license: MIT
compatibility: python>=3.8
---

# better-plot

一套用于创建高质量图表的工具函数，基于 matplotlib 和 seaborn。

## 功能特性

- **样式设置**: 一键配置专业的绘图样式和调色板
- **多种图表类型**: 支持散点图、线图、柱状图、直方图等常见图表
- **高质量输出**: 支持高分辨率保存，适合论文和报告使用
- **自动美化**: 自动添加网格、标签、图例等元素

## 依赖

- matplotlib >= 3.5.0
- seaborn >= 0.12.0
- numpy >= 1.20.0

## 主要函数

### 样式设置

- `setup_plot_style()`: 配置全局绘图样式

### 图表创建

- `create_scatter_plot()`: 创建散点图
- `create_line_plot()`: 创建线图
- `create_bar_plot()`: 创建柱状图
- `create_histogram()`: 创建直方图

### 工具函数

- `save_plot()`: 保存图表到文件

## 使用示例

```python
from better_plot import setup_plot_style, create_scatter_plot, save_plot
import numpy as np

# 设置样式
setup_plot_style(style='whitegrid', palette='Set2', font_scale=1.2)

# 创建散点图
x = np.random.randn(100)
y = np.random.randn(100)
fig, ax = create_scatter_plot(x, y, title='数据分布', xlabel='X轴', ylabel='Y轴')

# 保存图表
save_plot(fig, 'output.png', dpi=300)
```

## 详细文档

每个函数的详细文档和使用示例请查看 `docs/` 目录下自动生成的文档文件。

