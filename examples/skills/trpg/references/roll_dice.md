# roll_dice

基础投骰函数

## 函数签名

```python
def roll_dice(sides: int, count: int = 1) -> List[int]
```

## 参数

- `sides`: 骰子面数（如 6 表示 D6）
- `count`: 投掷次数（默认 1）

## 返回值

每次投掷的结果列表

## 示例

```python
>>> roll_dice(6, 3)  # 投掷 3 次 D6
[4, 2, 6]
```
