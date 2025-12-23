# pivot_dataframe

透视表转换

## 函数签名

```python
def pivot_dataframe(df: pandas.core.frame.DataFrame, index: Union[str, List[str]], columns: Union[str, List[str], NoneType] = None, values: Union[str, List[str], NoneType] = None, aggfunc: Union[str, Callable, List[Union[str, Callable]]] = 'mean', fill_value: Optional[Any] = None) -> pandas.core.frame.DataFrame
```

## 参数

- `df`: 要转换的 DataFrame
- `index`: 作为行索引的列名或列名列表
- `columns`: 作为列索引的列名或列名列表
- `values`: 要聚合的列名或列名列表
- `aggfunc`: 聚合函数（'mean', 'sum', 'count' 等）
- `fill_value`: 用于填充缺失值的值

## 返回值

透视表 DataFrame

## 示例

```python
df_pivot = pivot_dataframe(df, index='date', columns='category', values='sales')
```

```python
df_pivot = pivot_dataframe(df, index=['date', 'region'], values='sales')
```
