# check_dc

DC 判定

## 函数签名

```python
def check_dc(roll_result: int, difficulty_class: int) -> Dict[str, Any]
```

## 参数

- `roll_result`: 投掷结果（已包含所有调整值）
- `difficulty_class`: 难度等级（DC）

## 返回值

包含判定结果的字典

## 示例

```python
>>> check_dc(17, 15)
{'roll_result': 17, 'dc': 15, 'success': True, 'margin': 2}
```
