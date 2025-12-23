# get_character_info

获取角色信息

## 函数签名

```python
def get_character_info(character_name: str, file_path: str = 'game_state.json') -> Dict[str, Any]
```

## 参数

- `character_name`: 角色名称（如 "warrior"）
- `file_path`: 游戏状态文件路径（默认 "game_state.json"）

## 返回值

角色信息字典，如果角色不存在则返回空字典

## 示例

```python
>>> info = get_character_info("warrior")
>>> print(info.get("hp"))
```
