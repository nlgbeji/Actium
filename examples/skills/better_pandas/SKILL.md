---
description: A set of functions to help you quickly operate pandas DataFrame, detailed docs or reference could be found in references/ folder under ./skills/better-pandas
name: better-pandas
license: MIT
compatibility: python>=3.8
---

# better-pandas

一套用于快速操作 pandas DataFrame 的工具函数，提供常用数据操作的便捷接口。

## 功能特性

- **数据加载和保存**: 智能识别文件类型，支持 CSV、Excel、JSON、Parquet 等格式
- **数据探索**: 快速获取 DataFrame 的基本信息和统计摘要
- **数据清洗**: 自动处理缺失值、重复值和异常值
- **数据转换**: 标准化、透视表转换等常用操作
- **数据聚合**: 灵活的分组聚合功能
- **数据合并**: 友好的 DataFrame 合并接口
- **数据过滤**: 支持多种条件过滤方式

## 依赖

- pandas >= 1.3.0
- numpy >= 1.20.0

## 主要函数

### 数据 I/O

- `load_dataframe()`: 智能加载数据文件为 DataFrame
- `save_dataframe()`: 智能保存 DataFrame 到文件

### 数据探索

- `explore_dataframe()`: 快速探索 DataFrame 的基本信息

### 数据清洗

- `clean_dataframe()`: 清理 DataFrame 数据（去重、填充缺失值、移除异常值）

### 数据转换

- `normalize_columns()`: 标准化数值列
- `pivot_dataframe()`: 透视表转换

### 数据聚合

- `aggregate_by_group()`: 按组聚合数据

### 数据合并

- `merge_dataframes()`: 合并两个 DataFrame

### 数据过滤

- `filter_dataframe()`: 根据条件过滤 DataFrame

## 详细文档

每个函数的详细文档和使用示例请查看 `references/` 目录下自动生成的文档文件。

