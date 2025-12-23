# roll_attack

攻击检定

## 函数签名

```python
def roll_attack(attack_bonus: int, advantage: bool = False, disadvantage: bool = False) -> Dict[str, Any]
```

## 参数

- `attack_bonus`: 攻击加值
- `advantage`: 是否使用优势（默认 False）
- `disadvantage`: 是否使用劣势（默认 False）

## 返回值

包含投掷结果、加值和总和的字典

## 示例

```python
>>> roll_attack(5, advantage=True)
{'d20_rolls': [12, 18], 'd20_result': 18, 'attack_bonus': 5, 'total': 23, 'advantage': True}
```
