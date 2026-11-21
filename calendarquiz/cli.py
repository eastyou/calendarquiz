"""calendarquiz 命令行入口。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional, Sequence

from .model import (
    date_diff,
    format_date,
    make_quiz,
    nth_weekday,
    parse_date,
    weekday_name,
)
from .render import demo_html, month_calendar_html, quiz_html


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="calendarquiz",
        description="日历与日期推理：月历生成、星期推算、日期差与课堂练习",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    month = sub.add_parser("month", help="生成可打印的 A4 月历")
    month.add_argument("year", type=int, help="年份，1 到 9999")
    month.add_argument("month", type=int, help="月份，1 到 12")
    month.add_argument("-o", "--output", help="输出 HTML 路径；省略时打印到终端")
    month.add_argument("--title", default="", help="页面标题，默认按年月生成")

    weekday = sub.add_parser("weekday", help="推算某个日期是星期几")
    weekday.add_argument("date", help="日期，严格格式 YYYY-MM-DD")

    diff = sub.add_parser("diff", help="计算两个日期相差的天数")
    diff.add_argument("start", help="开始日期 YYYY-MM-DD")
    diff.add_argument("end", help="结束日期 YYYY-MM-DD")

    nth = sub.add_parser("nth", help="找出某月第 n 个星期几")
    nth.add_argument("year", type=int, help="年份")
    nth.add_argument("month", type=int, help="月份")
    nth.add_argument("weekday", type=int, help="星期编号：0=周一，1=周二，…，6=周日")
    nth.add_argument("n", type=int, help="第几个，1 到 5")

    quiz = sub.add_parser("quiz", help="生成日期推理四选一练习页")
    quiz.add_argument("--count", type=int, default=10, help="题目数量，默认 10")
    quiz.add_argument("--seed", type=int, default=7, help="随机种子，默认 7")
    quiz.add_argument("-o", "--output", required=True, help="输出 HTML 路径")
    quiz.add_argument("--title", default="日期推理练习", help="页面标题")
    quiz.add_argument("--answers", action="store_true", help="同时输出答案与解析页")

    demo = sub.add_parser("demo", help="生成包含月历、练习与答案的演示页")
    demo.add_argument("-o", "--output", required=True, help="输出 HTML 路径")
    demo.add_argument("--title", default="日历与日期推理 · 演示", help="页面标题")

    return parser


def _write_html(output: str, content: str) -> None:
    path = Path(output)
    path.write_text(content, encoding="utf-8")
    print("已生成：%s" % path)


def _run(args: argparse.Namespace) -> int:
    if args.command == "month":
        content = month_calendar_html(args.year, args.month, args.title)
        if args.output:
            _write_html(args.output, content)
        else:
            print(content)
        return 0
    if args.command == "weekday":
        value = parse_date(args.date)
        print("%s 是%s" % (format_date(value), weekday_name(value.weekday())))
        return 0
    if args.command == "diff":
        days = date_diff(args.start, args.end)
        print("%s 到 %s 相差 %d 天" % (args.start, args.end, days))
        return 0
    if args.command == "nth":
        result = nth_weekday(args.year, args.month, args.weekday, args.n)
        print(
            "%d 年 %d 月第 %d 个%s：%s"
            % (args.year, args.month, args.n, weekday_name(args.weekday), result)
        )
        return 0
    if args.command == "quiz":
        items = make_quiz(args.count, args.seed)
        content = quiz_html(items, args.title, args.answers)
        _write_html(args.output, content)
        return 0
    if args.command == "demo":
        content = demo_html(2024, 2, 8, 7, args.title)
        _write_html(args.output, content)
        return 0
    raise ValueError("未知命令：%s" % args.command)


def _ensure_utf8_console() -> None:
    """Windows 控制台默认编码可能无法输出中文，尽量切换为 UTF-8。"""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:
            continue
        try:
            reconfigure(encoding="utf-8", errors="replace")
        except (ValueError, OSError):
            continue


def main(argv: Optional[Sequence[str]] = None) -> int:
    _ensure_utf8_console()
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return _run(args)
    except (TypeError, ValueError) as exc:
        print("错误：%s" % exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
