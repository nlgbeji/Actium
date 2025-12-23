# merge_dataframes

合并两个 DataFrame

## 函数签名

```python
def merge_dataframes(left: pandas.core.frame.DataFrame, right: pandas.core.frame.DataFrame, on: Union[str, List[str], NoneType] = None, left_on: Union[str, List[str], NoneType] = None, right_on: Union[str, List[str], NoneType] = None, how: str = 'inner', suffixes: tuple = ('_x', '_y')) -> pandas.core.frame.DataFrame
```

## 参数

- `left`: 左侧 DataFrame
- `right`: 右侧 DataFrame
- `on`: 用于合并的列名（两个 DataFrame 都有该列时使用）
- `left_on`: 左侧 DataFrame 用于合并的列名
- `right_on`: 右侧 DataFrame 用于合并的列名
- `how`: 合并方式（'left', 'right', 'outer', 'inner'）
- `suffixes`: 重复列名的后缀

## 返回值

合并后的 DataFrame

## 示例

```python
df_merged = merge_dataframes(df1, df2, on='id')
```

```python
df_merged = merge_dataframes(df1, df2, left_on='id1', right_on='id2', how='outer')
```
