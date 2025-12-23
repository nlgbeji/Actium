# roll_ability_check

属性检定

## 函数签名

```python
def roll_ability_check(ability_modifier: int, proficiency_bonus: int = 0) -> Dict[str, Any]
```

## 参数

- `ability_modifier`: 属性调整值（如力量 +3）
- `proficiency_bonus`: 熟练加值（默认 0）

## 返回值

包含投掷结果、调整值和总和的字典

## 示例

```python
>>> roll_ability_check(3, 2)  # 力量 +3，熟练 +2
{'d20_roll': 12, 'ability_modifier': 3, 'proficiency_bonus': 2, 'total': 17}
```
