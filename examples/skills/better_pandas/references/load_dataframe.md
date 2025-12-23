# load_dataframe

智能加载数据文件为 DataFrame

## 函数签名

```python
def load_dataframe(file_path: Union[str, pathlib._local.Path], file_type: Optional[str] = None, **kwargs: Any) -> pandas.core.frame.DataFrame
```

## 参数

- `file_path`: 文件路径
- `file_type`: 文件类型（'csv', 'excel', 'json', 'parquet'），如果为 None 则根据扩展名自动识别
- `**kwargs`: 传递给相应 pandas 读取函数的额外参数

## 返回值

加载的 DataFrame

## 示例

```python
df = load_dataframe('data.csv')
```

```python
df = load_dataframe('data.xlsx', sheet_name='Sheet1')
```

```python
df = load_dataframe('data.json', file_type='json')
```
