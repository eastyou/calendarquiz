"""日历与日期推理的核心逻辑：解析、月历网格、星期推算与练习生成。"""

from __future__ import annotations

import datetime
import random
import re
from typing import Dict, List, Optional, Sequence, Tuple

MIN_YEAR = 1
MAX_YEAR = 9999
DAYS_PER_WEEK = 7
GRID_ROWS = 6

_DATE_PATTERN = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")
_WEEKDAY_NAMES: Tuple[str, ...] = (
    "星期一",
    "星期二",
    "星期三",
    "星期四",
    "星期五",
    "星期六",
    "星期日",
)
_DAYS_IN_MONTH: Tuple[int, ...] = (0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)


def _require_int(value: object, name: str) -> int:
    """校验参数必须是整数，拒绝 bool 与小数。"""
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError("%s 必须是整数" % name)
    return value


def _require_month(month: object) -> int:
    value = _require_int(month, "月份")
    if not 1 <= value <= 12:
        raise ValueError("月份应在 1 到 12 之间")
    return value


def _require_weekday(weekday: object) -> int:
    value = _require_int(weekday, "星期编号")
    if not 0 <= value <= 6:
        raise ValueError("星期编号应在 0 到 6 之间（0=周一）")
    return value


def is_leap_year(year: int) -> bool:
    """判断是否为闰年，年份需在 1 到 9999 之间。"""
    value = _require_int(year, "年份")
    if not MIN_YEAR <= value <= MAX_YEAR:
        raise ValueError("年份应在 %d 到 %d 之间" % (MIN_YEAR, MAX_YEAR))
    return value % 4 == 0 and (value % 100 != 0 or value % 400 == 0)


def days_in_month(year: int, month: int) -> int:
    """返回指定年月的天数。"""
    leap = is_leap_year(year)
    value = _require_month(month)
    if value == 2:
        return 29 if leap else 28
    return _DAYS_IN_MONTH[value]


def parse_date(text: str) -> datetime.date:
    """严格解析 ``YYYY-MM-DD`` 日期字符串。"""
    if not isinstance(text, str):
        raise TypeError("日期必须是字符串，例如 2024-05-01")
    match = _DATE_PATTERN.match(text)
    if match is None:
        raise ValueError("日期格式应为 YYYY-MM-DD，例如 2024-05-01")
    year = int(match.group(1))
    month = int(match.group(2))
    day = int(match.group(3))
    try:
        return datetime.date(year, month, day)
    except ValueError:
        raise ValueError("日期不合法：%s 不是有效日期" % text) from None


def format_date(value: datetime.date) -> str:
    """把日期格式化成 ``YYYY-MM-DD``。"""
    if isinstance(value, datetime.datetime) or not isinstance(value, datetime.date):
        raise TypeError("日期必须是 datetime.date")
    return value.isoformat()


def weekday_index(text: str) -> int:
    """返回星期编号，0 表示周一，6 表示周日。"""
    return parse_date(text).weekday()


def weekday_name(index: int) -> str:
    """把 0 到 6 的星期编号转换成中文名称。"""
    value = _require_weekday(index)
    return _WEEKDAY_NAMES[value]


def month_grid(year: int, month: int) -> List[List[Optional[int]]]:
    """生成固定 6 行 7 列的月历网格，周一开头，空格为 None。"""
    days = days_in_month(year, month)
    first = datetime.date(year, month, 1)
    cells: List[Optional[int]] = [None] * first.weekday()
    cells.extend(range(1, days + 1))
    cells.extend([None] * (GRID_ROWS * DAYS_PER_WEEK - len(cells)))
    return [cells[row * DAYS_PER_WEEK:(row + 1) * DAYS_PER_WEEK] for row in range(GRID_ROWS)]


def count_weekday(year: int, month: int, weekday: int) -> int:
    """统计某月某个星期几出现的次数。"""
    days = days_in_month(year, month)
    target = _require_weekday(weekday)
    total = 0
    for day in range(1, days + 1):
        if datetime.date(year, month, day).weekday() == target:
            total += 1
    return total


def nth_weekday(year: int, month: int, weekday: int, n: int) -> str:
    """返回某月第 n 个星期几的日期，n 为 1 到 5。"""
    target = _require_weekday(weekday)
    position = _require_int(n, "序号")
    if not 1 <= position <= 5:
        raise ValueError("序号 n 应在 1 到 5 之间")
    days = days_in_month(year, month)
    seen = 0
    for day in range(1, days + 1):
        current = datetime.date(year, month, day)
        if current.weekday() == target:
            seen += 1
            if seen == position:
                return format_date(current)
    raise ValueError(
        "%d 年 %d 月没有第 %d 个%s" % (year, month, position, weekday_name(target))
    )


def date_diff(start: str, end: str) -> int:
    """返回两个日期之间相差的绝对天数。"""
    begin = parse_date(start)
    finish = parse_date(end)
    return abs((finish - begin).days)


def add_days(text: str, days: int) -> str:
    """在日期上增加天数，负数表示向前推算。"""
    delta = _require_int(days, "天数")
    value = parse_date(text)
    try:
        result = value + datetime.timedelta(days=delta)
    except (OverflowError, ValueError):
        raise ValueError("结果日期超出 0001-01-01 到 9999-12-31 的范围") from None
    return format_date(result)


def _build_options(
    rng: random.Random, answer: str, candidates: Sequence[str]
) -> List[str]:
    """从候选答案中挑选 3 个干扰项，得到打乱后的四选一列表。"""
    options: List[str] = [answer]
    for candidate in candidates:
        if candidate in options:
            continue
        options.append(candidate)
        if len(options) == 4:
            break
    if len(options) != 4:
        raise ValueError("选项不足 4 个，无法生成四选一题目")
    rng.shuffle(options)
    return options


def _weekday_question(rng: random.Random) -> Dict[str, object]:
    year = rng.randint(1990, 2030)
    month = rng.randint(1, 12)
    day = rng.randint(1, days_in_month(year, month))
    value = datetime.date(year, month, day)
    answer = weekday_name(value.weekday())
    others = [name for name in _WEEKDAY_NAMES if name != answer]
    rng.shuffle(others)
    return {
        "question": "%s 是星期几？" % format_date(value),
        "answer": answer,
        "options": _build_options(rng, answer, others),
        "explanation": "%s 的星期编号是 %d（0=周一），所以是%s。"
        % (format_date(value), value.weekday(), answer),
    }


def _days_question(rng: random.Random) -> Dict[str, object]:
    year = rng.randint(1900, 2100)
    month = rng.randint(1, 12)
    total = days_in_month(year, month)
    answer = str(total)
    candidates = [str(value) for value in (28, 29, 30, 31) if str(value) != answer]
    rng.shuffle(candidates)
    leap_text = "是闰年" if is_leap_year(year) else "不是闰年"
    return {
        "question": "%d 年 %d 月共有多少天？" % (year, month),
        "answer": answer,
        "options": _build_options(rng, answer, candidates),
        "explanation": "%d 年%s，%d 月共有 %d 天。" % (year, leap_text, month, total),
    }


def _leap_question(rng: random.Random) -> Dict[str, object]:
    leap_year = rng.randint(1600, 2096)
    while not is_leap_year(leap_year):
        leap_year = rng.randint(1600, 2096)
    distractors: List[str] = []
    while len(distractors) < 3:
        candidate = rng.randint(1600, 2100)
        text = str(candidate)
        if candidate != leap_year and not is_leap_year(candidate) and text not in distractors:
            distractors.append(text)
    return {
        "question": "下面哪一年是闰年？",
        "answer": str(leap_year),
        "options": _build_options(rng, str(leap_year), distractors),
        "explanation": "%d 年能被 4 整除，且不是整百年或能被 400 整除，因此是闰年。"
        % leap_year,
    }


def _diff_question(rng: random.Random) -> Dict[str, object]:
    start = datetime.date(rng.randint(2018, 2028), rng.randint(1, 12), 1)
    start += datetime.timedelta(days=rng.randint(0, 27))
    delta = rng.randint(1, 400)
    end = start + datetime.timedelta(days=delta)
    answer = str(delta)
    candidates = [
        str(delta + offset)
        for offset in (1, -1, 2, -2, 3, -3)
        if delta + offset > 0
    ]
    return {
        "question": "从 %s 到 %s 相差多少天？" % (format_date(start), format_date(end)),
        "answer": answer,
        "options": _build_options(rng, answer, candidates),
        "explanation": "%s 到 %s 按自然日计算，共相差 %d 天。"
        % (format_date(start), format_date(end), delta),
    }


def make_quiz(count: int, seed: int) -> List[Dict[str, object]]:
    """生成可复现的四选一日期推理题，至少包含四种题型。"""
    amount = _require_int(count, "题目数量")
    if amount < 1:
        raise ValueError("题目数量必须大于 0")
    if amount > 200:
        raise ValueError("题目数量不能超过 200")
    rng = random.Random(_require_int(seed, "随机种子"))
    builders = (_weekday_question, _days_question, _leap_question, _diff_question)
    items: List[Dict[str, object]] = []
    for index in range(amount):
        items.append(builders[index % len(builders)](rng))
    return items
