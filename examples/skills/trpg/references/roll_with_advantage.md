# roll_with_advantage

优势投骰（投两次 D20，取较高值）

## 函数签名

```python
def roll_with_advantage() -> Dict[str, Any]
```

## 返回值

包含两次投掷结果和最终结果的字典

## 示例

```python
>>> roll_with_advantage()
{'rolls': [12, 18], 'result': 18, 'advantage': True}
```
