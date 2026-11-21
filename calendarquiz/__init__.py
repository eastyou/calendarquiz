"""calendarquiz：面向课堂的日历与日期推理小工具。"""

from .model import (
    add_days,
    count_weekday,
    date_diff,
    days_in_month,
    format_date,
    is_leap_year,
    make_quiz,
    month_grid,
    nth_weekday,
    parse_date,
    weekday_index,
    weekday_name,
)
from .render import demo_html, month_calendar_html, quiz_html

__all__ = [
    "add_days",
    "count_weekday",
    "date_diff",
    "days_in_month",
    "format_date",
    "is_leap_year",
    "make_quiz",
    "month_grid",
    "nth_weekday",
    "parse_date",
    "weekday_index",
    "weekday_name",
    "demo_html",
    "month_calendar_html",
    "quiz_html",
]

__version__ = "0.1.0"
