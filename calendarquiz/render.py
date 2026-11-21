"""把月历与练习题渲染成自包含、可打印的 HTML 页面。"""

from __future__ import annotations

import html
from typing import Dict, List, Sequence, Tuple

from .model import days_in_month, is_leap_year, make_quiz, month_grid

_OPTION_LABELS = "ABCD"
_WEEK_HEADERS: Tuple[str, ...] = ("周一", "周二", "周三", "周四", "周五", "周六", "周日")

_CSS = """
:root { color-scheme: light; }
* { box-sizing: border-box; }
@page { size: A4 portrait; margin: 16mm; }
body {
  margin: 0;
  padding: 24px 16px 40px;
  background: #eef2f7;
  color: #1f2937;
  font-family: "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Noto Sans CJK SC", sans-serif;
  line-height: 1.6;
}
.sheet {
  width: 100%;
  max-width: 190mm;
  margin: 0 auto 24px;
  padding: 28px 30px 24px;
  background: #ffffff;
  border: 1px solid #dbe3ee;
  border-radius: 10px;
  box-shadow: 0 6px 20px rgba(15, 23, 42, 0.06);
}
header { border-bottom: 2px solid #2563eb; padding-bottom: 12px; margin-bottom: 18px; }
h1 { margin: 0; font-size: 24px; letter-spacing: 0.5px; color: #1e3a8a; }
h2 { margin: 0 0 14px; font-size: 20px; color: #1e3a8a; }
.meta { margin: 6px 0 0; font-size: 13px; color: #64748b; }
table.calendar { width: 100%; border-collapse: collapse; table-layout: fixed; }
table.calendar th {
  padding: 8px 0;
  font-size: 14px;
  color: #334155;
  background: #eff6ff;
  border: 1px solid #cbd5e1;
}
table.calendar td {
  height: 62px;
  padding: 6px 8px;
  vertical-align: top;
  font-size: 17px;
  font-weight: 600;
  border: 1px solid #cbd5e1;
}
table.calendar td.weekend { background: #fff7ed; color: #b45309; }
table.calendar td.blank { background: #f8fafc; }
footer { margin-top: 16px; font-size: 12px; color: #94a3b8; text-align: right; }
ol.questions { margin: 0; padding-left: 22px; }
li.quiz-item { margin-bottom: 20px; break-inside: avoid; }
.question { margin: 0 0 8px; font-size: 16px; font-weight: 600; }
ul.options {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 6px 16px;
}
li.option {
  padding: 6px 10px;
  font-size: 14px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
}
.label {
  display: inline-block;
  width: 18px;
  font-weight: 700;
  color: #2563eb;
}
.answers { margin-top: 28px; page-break-before: always; break-before: page; }
.answers h2 { border-bottom: 2px solid #f59e0b; padding-bottom: 10px; }
ol.answer-list { margin: 0; padding-left: 22px; }
li.answer-item { margin-bottom: 14px; break-inside: avoid; }
.answer { margin: 0; font-weight: 600; color: #b45309; }
.explanation { margin: 2px 0 0; font-size: 14px; color: #475569; }
@media print {
  body { background: #ffffff; padding: 0; }
  .sheet { max-width: none; margin: 0; padding: 0; border: none; box-shadow: none; }
}
""".strip()


def _require_title(title: object, default: str) -> str:
    if not isinstance(title, str):
        raise TypeError("标题必须是字符串")
    cleaned = title.strip()
    return cleaned if cleaned else default


def _document(title: str, body: str) -> str:
    safe_title = html.escape(title, quote=True)
    return (
        "<!DOCTYPE html>\n"
        '<html lang="zh-CN">\n'
        "<head>\n"
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        "<title>%s</title>\n"
        "<style>\n%s\n</style>\n"
        "</head>\n"
        "<body>\n%s\n</body>\n"
        "</html>\n" % (safe_title, _CSS, body)
    )


def _month_section(year: int, month: int, title: str) -> str:
    total = days_in_month(year, month)
    grid = month_grid(year, month)
    header_cells = "".join("<th>%s</th>" % name for name in _WEEK_HEADERS)
    rows: List[str] = []
    for row in grid:
        cells: List[str] = []
        for column, day in enumerate(row):
            if day is None:
                cells.append('<td class="blank"></td>')
                continue
            classes = "day weekend" if column >= 5 else "day"
            cells.append('<td class="%s">%d</td>' % (classes, day))
        rows.append("<tr>%s</tr>" % "".join(cells))
    leap_text = "闰年" if is_leap_year(year) else "平年"
    return (
        '<main class="sheet month-sheet">\n'
        "<header>\n<h1>%s</h1>\n"
        '<p class="meta">%d 年 %d 月 · 共 %d 天 · %s</p>\n'
        "</header>\n"
        '<table class="calendar">\n<thead><tr>%s</tr></thead>\n<tbody>\n%s\n</tbody>\n</table>\n'
        "<footer>calendarquiz · A4 可打印月历</footer>\n"
        "</main>" % (
            html.escape(title, quote=True),
            year,
            month,
            total,
            leap_text,
            header_cells,
            "\n".join(rows),
        )
    )


def _require_text(value: object, message: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(message)
    return value


def _quiz_entries(
    items: Sequence[Dict[str, object]]
) -> List[Tuple[str, str, List[str], str]]:
    if not isinstance(items, (list, tuple)):
        raise TypeError("题目必须是列表")
    if not items:
        raise ValueError("至少需要一道题目")
    entries: List[Tuple[str, str, List[str], str]] = []
    for index, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            raise TypeError("第 %d 题必须是字典" % index)
        question = _require_text(item.get("question"), "第 %d 题缺少有效的 question" % index)
        answer = _require_text(item.get("answer"), "第 %d 题缺少有效的 answer" % index)
        explanation = _require_text(
            item.get("explanation"), "第 %d 题缺少有效的 explanation" % index
        )
        options_raw = item.get("options")
        if not isinstance(options_raw, (list, tuple)):
            raise TypeError("第 %d 题的 options 必须是列表" % index)
        if len(options_raw) != 4:
            raise ValueError("第 %d 题必须提供 4 个选项" % index)
        options: List[str] = []
        for option in options_raw:
            if not isinstance(option, str) or not option:
                raise ValueError("第 %d 题的选项必须是非空字符串" % index)
            options.append(option)
        if len(set(options)) != 4:
            raise ValueError("第 %d 题的选项不能重复" % index)
        if answer not in options:
            raise ValueError("第 %d 题的答案必须出现在选项中" % index)
        entries.append((question, answer, options, explanation))
    return entries


def _quiz_section(
    entries: Sequence[Tuple[str, str, List[str], str]], title: str, show_answers: bool
) -> str:
    questions: List[str] = []
    answers: List[str] = []
    for number, (question, answer, options, explanation) in enumerate(entries, start=1):
        option_html = "".join(
            '<li class="option"><span class="label">%s</span>%s</li>'
            % (_OPTION_LABELS[position], html.escape(option, quote=True))
            for position, option in enumerate(options)
        )
        questions.append(
            '<li class="quiz-item">\n'
            '<p class="question">%d. %s</p>\n'
            '<ul class="options">%s</ul>\n'
            "</li>" % (number, html.escape(question, quote=True), option_html)
        )
        letter = _OPTION_LABELS[options.index(answer)]
        answers.append(
            '<li class="answer-item">\n'
            '<p class="answer">%d. 答案：%s（%s）</p>\n'
            '<p class="explanation">解析：%s</p>\n'
            "</li>"
            % (
                number,
                letter,
                html.escape(answer, quote=True),
                html.escape(explanation, quote=True),
            )
        )
    sections = [
        '<main class="sheet quiz-sheet">\n<header>\n<h1>%s</h1>\n'
        '<p class="meta">共 %d 题 · 四选一 · 建议限时完成</p>\n</header>\n'
        '<ol class="questions">\n%s\n</ol>\n</main>'
        % (
            html.escape(title, quote=True),
            len(entries),
            "\n".join(questions),
        )
    ]
    if show_answers:
        sections.append(
            '<section class="sheet answers">\n<h2>答案与解析</h2>\n'
            '<ol class="answer-list">\n%s\n</ol>\n</section>' % "\n".join(answers)
        )
    return "\n".join(sections)


def month_calendar_html(year: int, month: int, title: str = "") -> str:
    """生成自包含 A4 月历页面。"""
    page_title = _require_title(title, "%d 年 %d 月" % (year, month))
    return _document(page_title, _month_section(year, month, page_title))


def quiz_html(
    items: Sequence[Dict[str, object]], title: str, show_answers: bool = False
) -> str:
    """生成练习页；``show_answers`` 为真时追加答案与解析页。"""
    if not isinstance(show_answers, bool):
        raise TypeError("show_answers 必须是布尔值")
    page_title = _require_title(title, "日期推理练习")
    entries = _quiz_entries(items)
    return _document(page_title, _quiz_section(entries, page_title, show_answers))


def demo_html(
    year: int, month: int, count: int, seed: int, title: str = ""
) -> str:
    """生成同时包含月历、练习与答案的演示页面。"""
    page_title = _require_title(title, "日历与日期推理 · 演示")
    entries = _quiz_entries(make_quiz(count, seed))
    body = "\n".join(
        (
            _month_section(year, month, "%d 年 %d 月" % (year, month)),
            _quiz_section(entries, "日期推理练习（含答案）", True),
        )
    )
    return _document(page_title, body)
