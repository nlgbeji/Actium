---
description: A set of functions to help you create high-quality plots quickly, detailed docs or reference could be found in references/ folder under ./skills/better-plot
name: better-plot
license: MIT
compatibility: python>=3.8
---

# better-plot

一套用于快速创建高质量图表的工具函数，提供美观专业的可视化接口。

# IMPORTANT: 在你使用matplotlib 或者本技能的函数，无比将 matplotlib 的backend 设置为 "Agg"，否则图表无法保存。
```python
import matplotlib
matplotlib.use("Agg")
```

## 功能特性

- **样式设置**: 统一配置 matplotlib 和 seaborn 的绘图样式，确保图表美观一致
- **散点图**: 支持颜色和大小映射的高质量散点图
- **线图**: 支持多条线、自动图例和网格的线图
- **柱状图**: 支持水平和垂直方向，自动添加数值标签的柱状图
- **直方图**: 支持核密度估计曲线的直方图
- **图表保存**: 高质量保存图表到多种格式（PNG、PDF、SVG 等）

## 依赖

- matplotlib >= 3.5.0
- seaborn >= 0.12.0
- numpy >= 1.20.0

## 主要函数

### 样式设置

- `setup_plot_style()`: 设置高质量绘图样式（样式、调色板、字体、DPI 等）

### 绘图函数

- `create_scatter_plot()`: 创建散点图
- `create_line_plot()`: 创建线图
- `create_bar_plot()`: 创建柱状图
- `create_histogram()`: 创建直方图

### 工具函数

- `save_plot()`: 保存图表到文件

## 详细文档

每个函数的详细文档和使用示例请查看 `references/` 目录下自动生成的文档文件。

