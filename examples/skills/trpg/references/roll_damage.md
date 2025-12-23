# roll_damage

伤害投骰

## 函数签名

```python
def roll_damage(dice_formula: str) -> Dict[str, Any]
```

## 参数

- `dice_formula`: 骰子公式（如 "2d6+3" 表示 2 个 D6 + 3）

## 返回值

包含每次投掷结果、总和和总伤害的字典

## 示例

```python
>>> roll_damage("2d6+3")
{'rolls': [4, 5], 'dice_total': 9, 'modifier': 3, 'total_damage': 12}
```
