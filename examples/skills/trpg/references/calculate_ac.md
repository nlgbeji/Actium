# calculate_ac

计算护甲等级（AC）

## 函数签名

```python
def calculate_ac(base_ac: int, dex_modifier: int, armor_bonus: int = 0) -> int
```

## 参数

- `base_ac`: 基础 AC（通常为 10）
- `dex_modifier`: 敏捷调整值
- `armor_bonus`: 护甲加值（默认 0）

## 返回值

最终护甲等级

## 示例

```python
>>> calculate_ac(10, 2, 4)  # 基础 10 + 敏捷 +2 + 护甲 +4
16
```
