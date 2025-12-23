# aggregate_by_group

按组聚合数据

## 函数签名

```python
def aggregate_by_group(df: pandas.core.frame.DataFrame, group_by: Union[str, List[str]], agg_funcs: Optional[Dict[str, Union[str, List[str]]]] = None, sort: bool = True) -> pandas.core.frame.DataFrame
```

## 参数

- `df`: 要聚合的 DataFrame
- `group_by`: 分组列名或列名列表
- `agg_funcs`: 聚合函数字典，格式为 {列名: 聚合函数}，如果为 None 则对所有数值列求均值
- `sort`: 是否对结果排序

## 返回值

聚合后的 DataFrame

## 示例

```python
summary = aggregate_by_group(df, group_by='category', agg_funcs={'price': 'mean', 'quantity': 'sum'})
```

```python
summary = aggregate_by_group(df, group_by=['category', 'region'])
```
