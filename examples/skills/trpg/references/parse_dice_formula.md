# parse_dice_formula

解析骰子公式

## 函数签名

```python
def parse_dice_formula(formula: str) -> Tuple[int, int, int]
```

## 参数

- `formula`: 骰子公式（如 "2d6+3" 或 "1d8-1"）

## 返回值

(骰子数量, 骰子面数, 调整值) 的元组

## 示例

```python
>>> parse_dice_formula("2d6+3")
(2, 6, 3)
>>> parse_dice_formula("1d8-1")
(1, 8, -1)
```
