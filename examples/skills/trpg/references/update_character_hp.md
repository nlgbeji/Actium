# update_character_hp

更新角色生命值

## 函数签名

```python
def update_character_hp(character_name: str, new_hp: int, file_path: str = 'game_state.json') -> None
```

## 参数

- `character_name`: 角色名称（如 "warrior"）
- `new_hp`: 新的生命值
- `file_path`: 游戏状态文件路径（默认 "game_state.json"）

## 返回值

None

## 示例

```python
>>> update_character_hp("warrior", 15)
```
