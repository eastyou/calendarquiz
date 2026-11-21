"""cli.py 的单元测试：成功输出、文件生成与错误退出码。"""

import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from typing import List, Tuple

from calendarquiz import cli


def _run(args: List[str]) -> Tuple[int, str, str]:
    out = io.StringIO()
    err = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = cli.main(args)
    return code, out.getvalue(), err.getvalue()


class HelpTests(unittest.TestCase):
    def test_help_exits_zero(self) -> None:
        out = io.StringIO()
        err = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            with self.assertRaises(SystemExit) as context:
                cli.main(["--help"])
        self.assertEqual(context.exception.code, 0)
        self.assertIn("month", out.getvalue())
        self.assertIn("星期", out.getvalue())

    def test_missing_command_exits_two(self) -> None:
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            with self.assertRaises(SystemExit) as context:
                cli.main([])
        self.assertEqual(context.exception.code, 2)
        self.assertIn("usage", err.getvalue())


class MonthCommandTests(unittest.TestCase):
    def test_writes_html_file_with_custom_title(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "month.html"
            code, out, err = _run(
                ["month", "2024", "5", "-o", str(path), "--title", "五月课堂月历"]
            )
            self.assertEqual(code, 0)
            self.assertEqual(err, "")
            self.assertIn("已生成", out)
            content = path.read_text(encoding="utf-8")
            self.assertIn("五月课堂月历", content)
            self.assertIn("2024 年 5 月", content)
            self.assertIn("@page", content)

    def test_prints_html_to_stdout_without_output(self) -> None:
        code, out, err = _run(["month", "2024", "2"])
        self.assertEqual(code, 0)
        self.assertEqual(err, "")
        self.assertIn("<!DOCTYPE html>", out)
        self.assertIn("2024 年 2 月", out)
        self.assertIn("共 29 天", out)

    def test_invalid_month_returns_two(self) -> None:
        code, out, err = _run(["month", "2024", "13"])
        self.assertEqual(code, 2)
        self.assertEqual(out, "")
        self.assertTrue(err.startswith("错误："))
        self.assertIn("月份", err)

    def test_non_integer_year_exits_two(self) -> None:
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            with self.assertRaises(SystemExit) as context:
                cli.main(["month", "abc", "5"])
        self.assertEqual(context.exception.code, 2)


class WeekdayCommandTests(unittest.TestCase):
    def test_prints_chinese_weekday(self) -> None:
        code, out, err = _run(["weekday", "2024-05-13"])
        self.assertEqual(code, 0)
        self.assertEqual(err, "")
        self.assertEqual(out.strip(), "2024-05-13 是星期一")

    def test_invalid_date_returns_two(self) -> None:
        code, out, err = _run(["weekday", "2023-02-29"])
        self.assertEqual(code, 2)
        self.assertEqual(out, "")
        self.assertTrue(err.startswith("错误："))
        self.assertIn("日期", err)


class DiffCommandTests(unittest.TestCase):
    def test_prints_day_difference(self) -> None:
        code, out, err = _run(["diff", "2024-01-01", "2024-01-31"])
        self.assertEqual(code, 0)
        self.assertEqual(err, "")
        self.assertIn("相差 30 天", out)

    def test_invalid_date_returns_two(self) -> None:
        code, out, err = _run(["diff", "2024-01-01", "2024-02-30"])
        self.assertEqual(code, 2)
        self.assertEqual(out, "")
        self.assertTrue(err.startswith("错误："))


class NthCommandTests(unittest.TestCase):
    def test_prints_nth_weekday(self) -> None:
        code, out, err = _run(["nth", "2024", "5", "0", "2"])
        self.assertEqual(code, 0)
        self.assertEqual(err, "")
        self.assertIn("第 2 个星期一", out)
        self.assertIn("2024-05-13", out)

    def test_missing_nth_returns_two(self) -> None:
        code, out, err = _run(["nth", "2024", "5", "0", "5"])
        self.assertEqual(code, 2)
        self.assertEqual(out, "")
        self.assertIn("没有", err)

    def test_invalid_weekday_returns_two(self) -> None:
        code, out, err = _run(["nth", "2024", "5", "7", "1"])
        self.assertEqual(code, 2)
        self.assertEqual(out, "")
        self.assertTrue(err.startswith("错误："))


class QuizCommandTests(unittest.TestCase):
    def test_generates_practice_page(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "quiz.html"
            code, out, err = _run(
                ["quiz", "--count", "5", "--seed", "7", "-o", str(path)]
            )
            self.assertEqual(code, 0)
            self.assertEqual(err, "")
            self.assertIn("已生成", out)
            content = path.read_text(encoding="utf-8")
            self.assertIn("日期推理练习", content)
            self.assertIn("共 5 题", content)
            self.assertNotIn("答案与解析", content)

    def test_answers_flag_adds_answer_page(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "quiz.html"
            code, _, _ = _run(
                ["quiz", "--count", "4", "--seed", "7", "-o", str(path), "--answers"]
            )
            self.assertEqual(code, 0)
            content = path.read_text(encoding="utf-8")
            self.assertIn("答案与解析", content)
            self.assertIn("解析：", content)

    def test_invalid_count_returns_two(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "quiz.html"
            code, out, err = _run(
                ["quiz", "--count", "0", "--seed", "7", "-o", str(path)]
            )
            self.assertEqual(code, 2)
            self.assertEqual(out, "")
            self.assertTrue(err.startswith("错误："))
            self.assertFalse(path.exists())

    def test_non_integer_seed_exits_two(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "quiz.html"
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                with self.assertRaises(SystemExit) as context:
                    cli.main(
                        ["quiz", "--count", "4", "--seed", "abc", "-o", str(path)]
                    )
            self.assertEqual(context.exception.code, 2)


class DemoCommandTests(unittest.TestCase):
    def test_generates_demo_page(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "demo.html"
            code, out, err = _run(["demo", "-o", str(path), "--title", "课堂演示"])
            self.assertEqual(code, 0)
            self.assertEqual(err, "")
            self.assertIn("已生成", out)
            content = path.read_text(encoding="utf-8")
            self.assertIn("课堂演示", content)
            self.assertIn('<table class="calendar">', content)
            self.assertIn("答案与解析", content)


if __name__ == "__main__":
    unittest.main()
