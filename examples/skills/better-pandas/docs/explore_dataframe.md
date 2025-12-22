# explore_dataframe

快速探索 DataFrame 的基本信息

## 函数签名

```python
def explore_dataframe(df: pandas.core.frame.DataFrame, include_stats: bool = True, sample_size: int = 5) -> Dict[str, Any]
```

## 参数

- `df`: 要探索的 DataFrame
- `include_stats`: 是否包含数值列的统计信息
- `sample_size`: 显示的前 N 行样本数量

## 返回值

包含探索信息的字典

## 示例

```python
summary = explore_dataframe(df)
```

```python
summary = explore_dataframe(df, include_stats=True)
```
