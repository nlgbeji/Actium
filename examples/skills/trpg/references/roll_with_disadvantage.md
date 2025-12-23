# roll_with_disadvantage

劣势投骰（投两次 D20，取较低值）

## 函数签名

```python
def roll_with_disadvantage() -> Dict[str, Any]
```

## 返回值

包含两次投掷结果和最终结果的字典

## 示例

```python
>>> roll_with_disadvantage()
{'rolls': [15, 8], 'result': 8, 'disadvantage': True}
```
