# save_dataframe

智能保存 DataFrame 到文件

## 函数签名

```python
def save_dataframe(df: pandas.core.frame.DataFrame, file_path: Union[str, pathlib._local.Path], file_type: Optional[str] = None, **kwargs: Any) -> None
```

## 参数

- `df`: 要保存的 DataFrame
- `file_path`: 保存路径
- `file_type`: 文件类型（'csv', 'excel', 'json', 'parquet'），如果为 None 则根据扩展名自动识别
- `**kwargs`: 传递给相应 pandas 保存函数的额外参数

## 返回值

None

## 示例

```python
save_dataframe(df, 'output.csv')
```

```python
save_dataframe(df, 'output.xlsx', index=False)
```

```python
save_dataframe(df, 'output.json', file_type='json', orient='records')
```
