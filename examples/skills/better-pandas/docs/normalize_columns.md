# normalize_columns

标准化数值列

## 函数签名

```python
def normalize_columns(df: pandas.core.frame.DataFrame, columns: Optional[List[str]] = None, method: str = 'standard') -> pandas.core.frame.DataFrame
```

## 参数

- `df`: 要处理的 DataFrame
- `columns`: 要标准化的列名列表，如果为 None 则标准化所有数值列
- `method`: 标准化方法（'standard' 为 Z-score，'minmax' 为 Min-Max）

## 返回值

标准化后的 DataFrame

## 示例

```python
df_normalized = normalize_columns(df, columns=['age', 'income'])
```

```python
df_normalized = normalize_columns(df, method='minmax')
```
