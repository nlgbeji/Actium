# clean_dataframe

清理 DataFrame 数据

## 函数签名

```python
def clean_dataframe(df: pandas.core.frame.DataFrame, drop_duplicates: bool = True, fill_method: Optional[str] = None, remove_outliers: bool = False, outlier_method: str = 'iqr') -> pandas.core.frame.DataFrame
```

## 参数

- `df`: 要清理的 DataFrame
- `drop_duplicates`: 是否删除重复行
- `fill_method`: 填充缺失值的方法（'mean', 'median', 'mode', 'forward', 'backward'），None 表示不填充
- `remove_outliers`: 是否移除异常值
- `outlier_method`: 异常值检测方法（'iqr' 或 'zscore'）

## 返回值

清理后的 DataFrame

## 示例

```python
df_clean = clean_dataframe(df)
```

```python
df_clean = clean_dataframe(df, drop_duplicates=True, fill_method='mean')
```
