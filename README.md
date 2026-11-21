# calendarquiz

[![CI](https://github.com/eastyou/calendarquiz/actions/workflows/ci.yml/badge.svg)](https://github.com/eastyou/calendarquiz/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)

面向课堂的日历与日期推理工具：生成可打印月历、推算星期、计算日期差，并批量生成四选一练习页。

## 功能

- 严格解析 `YYYY-MM-DD`，格式错误或日期不存在时给出中文提示
- 判断闰年、统计每月天数，年份支持 1 ~ 9999
- 生成周一开头的 6 行 × 7 列月历网格，空白格用 `None` 表示
- 推算某天是星期几，统计某月星期几的出现次数
- 找出某月第 n 个星期几，自动识别不存在的第 5 个星期几
- 计算两个日期的绝对天数差，支持按天数前后推算
- 生成自包含 A4 月历页面，内联 CSS，可直接打印
- 生成日期推理练习页，至少四种题型，随机种子保证可复现
- 所有动态文本均做 HTML 转义，避免注入风险

## 安装

```bash
pip install -e .
```

项目只使用 Python 标准库，无需安装其他依赖。也可以不安装，直接在仓库根目录运行 `python -m calendarquiz`。

## 使用

```bash
# 生成可打印月历；省略 -o 时把 HTML 打印到终端
calendarquiz month 2024 5 -o examples/month.html --title "2024 年 5 月"

# 推算星期几（0 = 周一，6 = 周日）
calendarquiz weekday 2024-05-13

# 两个日期相差的天数（取绝对值）
calendarquiz diff 2024-01-01 2024-01-31

# 找出 2024 年 5 月第 2 个星期一；WEEKDAY 用 0-6，0=周一
calendarquiz nth 2024 5 0 2

# 生成 10 道题，随机种子 7；加 --answers 同时输出答案与解析
calendarquiz quiz --count 10 --seed 7 -o examples/quiz.html
calendarquiz quiz --count 10 --seed 7 --answers -o quiz-answers.html

# 生成包含月历、练习与答案的演示页
calendarquiz demo -o demo.html
```

`weekday` 的输出示例：

```text
2024-05-13 是星期一
```

`nth` 的输出示例：

```text
2024 年 5 月第 2 个星期一：2024-05-13
```

## 作为库使用

```python
from calendarquiz import (
    add_days,
    date_diff,
    is_leap_year,
    month_grid,
    nth_weekday,
    weekday_name,
)

assert is_leap_year(2024)
assert month_grid(2024, 5)[0][2] == 1
assert weekday_name(0) == "星期一"
assert nth_weekday(2024, 5, 0, 2) == "2024-05-13"
assert date_diff("2024-01-01", "2024-01-31") == 30
assert add_days("2024-02-28", 1) == "2024-02-29"
```

参数校验规则：整数参数拒绝 `bool` 与小数；日期必须是 `YYYY-MM-DD` 字符串；年份限定 1 ~ 9999，月份 1 ~ 12，星期编号 0 ~ 6。违反规则会抛出带中文说明的 `TypeError` 或 `ValueError`。

## 示例

- [examples/month.html](examples/month.html)：2024 年 5 月月历，含 A4 打印样式
- [examples/quiz.html](examples/quiz.html)：10 道日期推理练习题，随机种子 7

## 测试

```bash
python -m unittest discover -s tests -v
```

共 95 项单元测试，覆盖闰年、每月天数、严格日期解析、月历网格、星期统计、第 n 个星期几、日期差、日期推算、练习生成、HTML 转义与命令行错误退出码。CI 在 Linux、macOS、Windows 上运行 Python 3.9 ~ 3.13。

## 许可

MIT © 2026 eastyou
