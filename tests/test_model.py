"""model.py 的单元测试：正常、边界与异常输入。"""

import datetime
import unittest

from calendarquiz.model import (
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


class LeapYearTests(unittest.TestCase):
    def test_common_leap_year(self) -> None:
        self.assertTrue(is_leap_year(2024))
        self.assertTrue(is_leap_year(1996))

    def test_common_year(self) -> None:
        self.assertFalse(is_leap_year(2023))
        self.assertFalse(is_leap_year(2021))

    def test_century_is_not_leap(self) -> None:
        self.assertFalse(is_leap_year(1900))
        self.assertFalse(is_leap_year(2100))

    def test_four_hundred_year_is_leap(self) -> None:
        self.assertTrue(is_leap_year(2000))
        self.assertTrue(is_leap_year(1600))

    def test_supported_bounds_and_out_of_range(self) -> None:
        self.assertFalse(is_leap_year(1))
        self.assertFalse(is_leap_year(9999))
        with self.assertRaises(ValueError):
            is_leap_year(0)
        with self.assertRaises(ValueError):
            is_leap_year(10000)

    def test_invalid_types(self) -> None:
        for value in (True, False, 2024.0, "2024", None):
            with self.subTest(value=value):
                with self.assertRaises(TypeError):
                    is_leap_year(value)  # type: ignore[arg-type]


class DaysInMonthTests(unittest.TestCase):
    def test_non_leap_year_all_months(self) -> None:
        expected = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
        for month in range(1, 13):
            with self.subTest(month=month):
                self.assertEqual(days_in_month(2023, month), expected[month - 1])

    def test_leap_february(self) -> None:
        self.assertEqual(days_in_month(2024, 2), 29)
        self.assertEqual(days_in_month(2000, 2), 29)

    def test_non_leap_february(self) -> None:
        self.assertEqual(days_in_month(1900, 2), 28)
        self.assertEqual(days_in_month(2023, 2), 28)

    def test_month_out_of_range(self) -> None:
        for month in (0, 13, -1):
            with self.subTest(month=month):
                with self.assertRaises(ValueError):
                    days_in_month(2024, month)

    def test_month_invalid_types(self) -> None:
        for month in (True, 2.0, "2", None):
            with self.subTest(month=month):
                with self.assertRaises(TypeError):
                    days_in_month(2024, month)  # type: ignore[arg-type]

    def test_year_invalid(self) -> None:
        with self.assertRaises(ValueError):
            days_in_month(0, 1)
        with self.assertRaises(TypeError):
            days_in_month("2024", 1)  # type: ignore[arg-type]


class ParseDateTests(unittest.TestCase):
    def test_valid_date(self) -> None:
        self.assertEqual(parse_date("2024-05-01"), datetime.date(2024, 5, 1))

    def test_valid_leap_day(self) -> None:
        self.assertEqual(parse_date("2024-02-29"), datetime.date(2024, 2, 29))

    def test_supported_bounds(self) -> None:
        self.assertEqual(parse_date("0001-01-01"), datetime.date(1, 1, 1))
        self.assertEqual(parse_date("9999-12-31"), datetime.date(9999, 12, 31))

    def test_invalid_calendar_dates(self) -> None:
        for text in ("2023-02-29", "2024-13-01", "2024-00-10", "2024-04-31", "0000-01-01"):
            with self.subTest(text=text):
                with self.assertRaises(ValueError) as context:
                    parse_date(text)
                self.assertIn("日期", str(context.exception))

    def test_bad_formats(self) -> None:
        for text in ("2024/05/01", "2024-5-1", "20240501", "", " 2024-05-01", "2024-05-01 "):
            with self.subTest(text=text):
                with self.assertRaises(ValueError):
                    parse_date(text)

    def test_non_string(self) -> None:
        for value in (20240501, None, b"2024-05-01"):
            with self.subTest(value=value):
                with self.assertRaises(TypeError):
                    parse_date(value)  # type: ignore[arg-type]


class FormatDateTests(unittest.TestCase):
    def test_iso_format(self) -> None:
        self.assertEqual(format_date(datetime.date(2024, 5, 1)), "2024-05-01")
        self.assertEqual(format_date(datetime.date(1, 1, 1)), "0001-01-01")

    def test_invalid_type(self) -> None:
        for value in ("2024-05-01", None, 20240501):
            with self.subTest(value=value):
                with self.assertRaises(TypeError):
                    format_date(value)  # type: ignore[arg-type]

    def test_datetime_rejected(self) -> None:
        with self.assertRaises(TypeError):
            format_date(datetime.datetime(2024, 5, 1, 8, 30))  # type: ignore[arg-type]


class WeekdayTests(unittest.TestCase):
    def test_monday_is_zero(self) -> None:
        self.assertEqual(weekday_index("2024-05-13"), 0)

    def test_sunday_is_six(self) -> None:
        self.assertEqual(weekday_index("2024-05-19"), 6)

    def test_invalid_input(self) -> None:
        with self.assertRaises(ValueError):
            weekday_index("2023-02-29")
        with self.assertRaises(TypeError):
            weekday_index(None)  # type: ignore[arg-type]

    def test_all_weekday_names(self) -> None:
        expected = ("星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日")
        for index, name in enumerate(expected):
            with self.subTest(index=index):
                self.assertEqual(weekday_name(index), name)

    def test_name_out_of_range(self) -> None:
        for index in (-1, 7, 100):
            with self.subTest(index=index):
                with self.assertRaises(ValueError):
                    weekday_name(index)

    def test_name_invalid_types(self) -> None:
        for value in (True, 1.0, "1", None):
            with self.subTest(value=value):
                with self.assertRaises(TypeError):
                    weekday_name(value)  # type: ignore[arg-type]


class MonthGridTests(unittest.TestCase):
    def test_shape_is_six_by_seven(self) -> None:
        grid = month_grid(2024, 5)
        self.assertEqual(len(grid), 6)
        self.assertTrue(all(len(row) == 7 for row in grid))

    def test_february_2021_starts_on_monday(self) -> None:
        grid = month_grid(2021, 2)
        self.assertEqual(grid[0][0], 1)
        self.assertEqual(grid[0][6], 7)

    def test_may_2024_first_day_offset(self) -> None:
        grid = month_grid(2024, 5)
        self.assertIsNone(grid[0][0])
        self.assertIsNone(grid[0][1])
        self.assertEqual(grid[0][2], 1)
        self.assertEqual(grid[0][3], 2)

    def test_each_day_appears_once_and_tail_is_blank(self) -> None:
        grid = month_grid(2024, 5)
        days = [cell for row in grid for cell in row if cell is not None]
        self.assertEqual(days, list(range(1, 32)))
        self.assertEqual(grid[4][4], 31)
        self.assertEqual(grid[5], [None] * 7)

    def test_invalid_input(self) -> None:
        with self.assertRaises(ValueError):
            month_grid(2024, 0)
        with self.assertRaises(TypeError):
            month_grid(2024, True)  # type: ignore[arg-type]


class CountWeekdayTests(unittest.TestCase):
    def test_five_fridays(self) -> None:
        self.assertEqual(count_weekday(2024, 3, 4), 5)

    def test_four_mondays(self) -> None:
        self.assertEqual(count_weekday(2024, 5, 0), 4)

    def test_all_counts_cover_month(self) -> None:
        total = sum(count_weekday(2024, 2, index) for index in range(7))
        self.assertEqual(total, 29)

    def test_invalid_input(self) -> None:
        with self.assertRaises(ValueError):
            count_weekday(2024, 5, 7)
        with self.assertRaises(ValueError):
            count_weekday(2024, 13, 0)
        with self.assertRaises(TypeError):
            count_weekday(2024, 5, True)  # type: ignore[arg-type]


class NthWeekdayTests(unittest.TestCase):
    def test_first_monday(self) -> None:
        self.assertEqual(nth_weekday(2024, 5, 0, 1), "2024-05-06")

    def test_fourth_monday(self) -> None:
        self.assertEqual(nth_weekday(2024, 5, 0, 4), "2024-05-27")

    def test_fifth_thursday_in_leap_february(self) -> None:
        self.assertEqual(nth_weekday(2024, 2, 3, 5), "2024-02-29")

    def test_missing_fifth_weekday(self) -> None:
        with self.assertRaises(ValueError) as context:
            nth_weekday(2024, 5, 0, 5)
        self.assertIn("没有", str(context.exception))

    def test_n_out_of_range(self) -> None:
        for value in (0, 6, -1, True):
            with self.subTest(value=value):
                with self.assertRaises((TypeError, ValueError)):
                    nth_weekday(2024, 5, 0, value)

    def test_weekday_out_of_range(self) -> None:
        with self.assertRaises(ValueError):
            nth_weekday(2024, 5, 7, 1)
        with self.assertRaises(TypeError):
            nth_weekday(2024, 5, "0", 1)  # type: ignore[arg-type]


class DateDiffTests(unittest.TestCase):
    def test_same_day(self) -> None:
        self.assertEqual(date_diff("2024-05-01", "2024-05-01"), 0)

    def test_forward(self) -> None:
        self.assertEqual(date_diff("2024-01-01", "2024-01-31"), 30)

    def test_reverse_is_absolute(self) -> None:
        self.assertEqual(date_diff("2024-01-31", "2024-01-01"), 30)

    def test_leap_year_span(self) -> None:
        self.assertEqual(date_diff("2023-01-01", "2024-01-01"), 365)
        self.assertEqual(date_diff("2024-01-01", "2025-01-01"), 366)

    def test_invalid_dates(self) -> None:
        with self.assertRaises(ValueError):
            date_diff("2024-02-29", "2023-02-29")
        with self.assertRaises(ValueError):
            date_diff("2024-05-01", "2024-15-01")


class AddDaysTests(unittest.TestCase):
    def test_add_positive_days(self) -> None:
        self.assertEqual(add_days("2024-05-01", 10), "2024-05-11")

    def test_add_negative_days(self) -> None:
        self.assertEqual(add_days("2024-05-10", -10), "2024-04-30")

    def test_add_zero(self) -> None:
        self.assertEqual(add_days("2024-02-29", 0), "2024-02-29")

    def test_cross_month_and_year(self) -> None:
        self.assertEqual(add_days("2023-12-31", 1), "2024-01-01")
        self.assertEqual(add_days("2024-01-01", -1), "2023-12-31")

    def test_leap_day(self) -> None:
        self.assertEqual(add_days("2024-02-28", 1), "2024-02-29")
        self.assertEqual(add_days("2023-02-28", 1), "2023-03-01")

    def test_invalid_days_types(self) -> None:
        for value in (True, 1.5, "1", None):
            with self.subTest(value=value):
                with self.assertRaises(TypeError):
                    add_days("2024-05-01", value)  # type: ignore[arg-type]

    def test_overflow_both_directions(self) -> None:
        with self.assertRaises(ValueError):
            add_days("9999-12-31", 1)
        with self.assertRaises(ValueError):
            add_days("0001-01-01", -1)
        with self.assertRaises(ValueError):
            add_days("2024-05-01", 10 ** 9)

    def test_invalid_date(self) -> None:
        with self.assertRaises(ValueError):
            add_days("2024-02-30", 1)


class MakeQuizTests(unittest.TestCase):
    def test_structure_and_length(self) -> None:
        items = make_quiz(10, 7)
        self.assertEqual(len(items), 10)
        for item in items:
            self.assertIsInstance(item, dict)
            for key in ("question", "answer", "options", "explanation"):
                self.assertIn(key, item)
                self.assertIsInstance(item[key], str if key != "options" else list)

    def test_options_are_four_unique_choices(self) -> None:
        for item in make_quiz(12, 3):
            options = item["options"]
            self.assertIsInstance(options, list)
            assert isinstance(options, list)
            self.assertEqual(len(options), 4)
            self.assertEqual(len(set(options)), 4)
            self.assertIn(item["answer"], options)

    def test_same_seed_is_reproducible(self) -> None:
        self.assertEqual(make_quiz(8, 7), make_quiz(8, 7))

    def test_different_seed_changes_questions(self) -> None:
        self.assertNotEqual(make_quiz(8, 7), make_quiz(8, 8))

    def test_four_question_kinds(self) -> None:
        kinds = set()
        for item in make_quiz(8, 11):
            question = item["question"]
            assert isinstance(question, str)
            if "星期几" in question:
                kinds.add("weekday")
            elif "共有多少天" in question:
                kinds.add("days")
            elif "哪一年是闰年" in question:
                kinds.add("leap")
            elif "相差多少天" in question:
                kinds.add("diff")
            else:
                self.fail("未知题型：%s" % question)
        self.assertEqual(kinds, {"weekday", "days", "leap", "diff"})

    def test_explanations_are_non_empty(self) -> None:
        for item in make_quiz(6, 5):
            explanation = item["explanation"]
            assert isinstance(explanation, str)
            self.assertTrue(explanation.strip())

    def test_invalid_count(self) -> None:
        for value in (0, -1, 201):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    make_quiz(value, 7)
        with self.assertRaises(TypeError):
            make_quiz(True, 7)  # type: ignore[arg-type]

    def test_invalid_seed(self) -> None:
        for value in (True, 7.0, "7", None):
            with self.subTest(value=value):
                with self.assertRaises(TypeError):
                    make_quiz(4, value)  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
