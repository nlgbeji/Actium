# save_game_state

保存游戏状态到文件

## 函数签名

```python
def save_game_state(state: Dict[str, Any], file_path: str = 'game_state.json') -> None
```

## 参数

- `state`: 游戏状态字典
- `file_path`: 保存路径（默认 "game_state.json"）

## 返回值

None

## 示例

```python
>>> state = {"scene": "森林", "turn": 1}
>>> save_game_state(state)
```
