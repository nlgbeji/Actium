# determine_hit

判定是否命中

## 函数签名

```python
def determine_hit(attack_roll: int, target_ac: int) -> bool
```

## 参数

- `attack_roll`: 攻击投掷结果（已包含所有调整值）
- `target_ac`: 目标护甲等级

## 返回值

是否命中

## 示例

```python
>>> determine_hit(18, 16)
True
>>> determine_hit(14, 16)
False
```
