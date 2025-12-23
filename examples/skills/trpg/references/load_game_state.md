# load_game_state

从文件加载游戏状态

## 函数签名

```python
def load_game_state(file_path: str = 'game_state.json') -> Dict[str, Any]
```

## 参数

- `file_path`: 文件路径（默认 "game_state.json"）

## 返回值

游戏状态字典，如果文件不存在则返回空字典

## 示例

```python
>>> state = load_game_state()
>>> print(state.get("scene"))
```
