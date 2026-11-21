"""render.py 的单元测试：关键片段、转义与参数校验。"""

import unittest
from typing import Dict, List

from calendarquiz.render import demo_html, month_calendar_html, quiz_html


def _sample_items() -> List[Dict[str, object]]:
    return [
        {
            "question": "2024-05-13 是星期几？",
            "answer": "星期一",
            "options": ["星期一", "星期二", "星期三", "星期四"],
            "explanation": "2024-05-13 的星期编号为 0。",
        },
        {
            "question": "2024 年 2 月共有多少天？",
            "answer": "29",
            "options": ["28", "29", "30", "31"],
            "explanation": "2024 年是闰年，2 月有 29 天。",
        },
    ]


class MonthCalendarHtmlTests(unittest.TestCase):
    def test_self_contained_a4_document(self) -> None:
        content = month_calendar_html(2024, 5, "五月月历")
        self.assertTrue(content.startswith("<!DOCTYPE html>"))
        self.assertIn('lang="zh-CN"', content)
        self.assertIn("<style>", content)
        self.assertIn("@page", content)
        self.assertIn("A4", content)
        self.assertIn("</html>", content)

    def test_title_and_meta(self) -> None:
        content = month_calendar_html(2024, 5, "五月月历")
        self.assertIn("五月月历", content)
        self.assertIn("2024 年 5 月", content)
        self.assertIn("共 31 天", content)
        self.assertIn("闰年", content)

    def test_weekday_headers_and_first_week(self) -> None:
        content = month_calendar_html(2024, 5)
        for name in ("周一", "周二", "周三", "周四", "周五", "周六", "周日"):
            self.assertIn(name, content)
        self.assertIn('<td class="day">1</td>', content)
        self.assertEqual(content.count('<td class="blank"></td>'), 11)

    def test_weekend_cells_are_marked(self) -> None:
        content = month_calendar_html(2024, 5)
        self.assertEqual(content.count('<td class="day weekend">'), 8)

    def test_title_is_escaped(self) -> None:
        content = month_calendar_html(2024, 5, '<script>alert("x")</script>')
        self.assertNotIn("<script>", content)
        self.assertIn("&lt;script&gt;", content)

    def test_invalid_input(self) -> None:
        with self.assertRaises(ValueError):
            month_calendar_html(2024, 13)
        with self.assertRaises(TypeError):
            month_calendar_html(2024, 5, 123)  # type: ignore[arg-type]


class QuizHtmlTests(unittest.TestCase):
    def test_questions_options_and_labels(self) -> None:
        content = quiz_html(_sample_items(), "日期推理练习")
        self.assertIn("日期推理练习", content)
        self.assertIn("2024-05-13 是星期几？", content)
        self.assertIn('<span class="label">A</span>', content)
        self.assertIn('<span class="label">D</span>', content)
        self.assertEqual(content.count('class="option"'), 8)
        self.assertIn("共 2 题", content)

    def test_dynamic_text_is_escaped(self) -> None:
        items: List[Dict[str, object]] = [
            {
                "question": "<b>危险</b>问题",
                "answer": "<1>",
                "options": ["<1>", "2", "3", "4"],
                "explanation": "<em>解析</em>",
            }
        ]
        content = quiz_html(items, "<script>标题</script>", True)
        self.assertNotIn("<b>", content)
        self.assertNotIn("<1>", content)
        self.assertNotIn("<em>", content)
        self.assertNotIn("<script>", content)
        self.assertIn("&lt;b&gt;", content)
        self.assertIn("&lt;1&gt;", content)
        self.assertIn("&lt;em&gt;", content)
        self.assertIn("&lt;script&gt;", content)

    def test_answers_hidden_by_default(self) -> None:
        content = quiz_html(_sample_items(), "日期推理练习")
        self.assertNotIn("答案与解析", content)
        self.assertNotIn("解析：", content)

    def test_answers_shown_when_requested(self) -> None:
        content = quiz_html(_sample_items(), "日期推理练习", True)
        self.assertIn("答案与解析", content)
        self.assertIn("解析：", content)
        self.assertIn("答案：A", content)
        self.assertIn("page-break-before", content)

    def test_invalid_items(self) -> None:
        cases = [
            ([], ValueError),
            ({"question": "x"}, TypeError),
            (["不是字典"], TypeError),
        ]
        for items, error in cases:
            with self.subTest(items=items):
                with self.assertRaises(error):
                    quiz_html(items, "标题")  # type: ignore[arg-type]

    def test_invalid_item_fields(self) -> None:
        base: Dict[str, object] = {
            "question": "题目",
            "answer": "A",
            "options": ["A", "B", "C", "D"],
            "explanation": "解析",
        }
        missing = dict(base)
        missing.pop("explanation")
        three_options = dict(base, options=["A", "B", "C"])
        duplicated = dict(base, options=["A", "A", "B", "C"])
        answer_missing = dict(base, answer="E")
        for item in (missing, three_options, duplicated, answer_missing):
            with self.subTest(item=item):
                with self.assertRaises(ValueError):
                    quiz_html([item], "标题")

    def test_show_answers_must_be_bool(self) -> None:
        with self.assertRaises(TypeError):
            quiz_html(_sample_items(), "标题", 1)  # type: ignore[arg-type]


class DemoHtmlTests(unittest.TestCase):
    def test_demo_contains_month_and_answers(self) -> None:
        content = demo_html(2024, 2, 4, 7, "课堂演示")
        self.assertIn("课堂演示", content)
        self.assertIn('<table class="calendar">', content)
        self.assertIn("2024 年 2 月", content)
        self.assertIn("答案与解析", content)


if __name__ == "__main__":
    unittest.main()
