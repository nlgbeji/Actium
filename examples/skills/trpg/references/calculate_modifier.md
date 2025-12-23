# calculate_modifier

计算属性调整值

## 函数签名

```python
def calculate_modifier(ability_score: int) -> int
```

## 参数

- `ability_score`: 属性值（如力量 16）

## 返回值

属性调整值（如力量 16 对应 +3）

## 示例

```python
>>> calculate_modifier(16)
3
>>> calculate_modifier(8)
-1
```
