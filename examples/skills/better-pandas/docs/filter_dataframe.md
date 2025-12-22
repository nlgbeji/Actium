# filter_dataframe

根据条件过滤 DataFrame

## 函数签名

```python
def filter_dataframe(df: pandas.core.frame.DataFrame, conditions: Optional[Dict[str, tuple]] = None, query: Optional[str] = None) -> pandas.core.frame.DataFrame
```

## 参数

- `df`: 要过滤的 DataFrame
- `conditions`: 条件字典，格式为 {列名: (操作符, 值)}，操作符支持 '==', '!=', '>', '<', '>=', '<=', 'in', 'not in'
- `query`: pandas query 字符串（如果提供，将优先使用此方式）

## 返回值

过滤后的 DataFrame

## 示例

```python
df_filtered = filter_dataframe(df, conditions={'age': ('>=', 18), 'city': ('==', 'Beijing')})
```

```python
df_filtered = filter_dataframe(df, query='age >= 18 and city == "Beijing"')
```
