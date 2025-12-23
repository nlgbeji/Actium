# apply_damage

应用伤害

## 函数签名

```python
def apply_damage(current_hp: int, damage: int) -> Dict[str, Any]
```

## 参数

- `current_hp`: 当前生命值
- `damage`: 受到的伤害值

## 返回值

包含新生命值和是否死亡的字典

## 示例

```python
>>> apply_damage(20, 5)
{'old_hp': 20, 'damage': 5, 'new_hp': 15, 'is_dead': False}
```
