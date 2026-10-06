"""Check that tenor arithmetic preserves consistent calendar and time fields."""

import pytest

from financepy.utils.date import Date
from financepy.utils.tenor import Tenor


def assert_same_date(actual, expected):
    """Check fields as well as the Excel serial used by Date equality."""
    assert actual.datetime() == expected.datetime()
    assert actual.excel_dt == expected.excel_dt
    assert actual.weekday == expected.weekday
    assert Date.from_excel(actual.excel_dt).datetime() == actual.datetime()


@pytest.mark.parametrize("time", [(0, 0, 0), (0, 0, 1), (13, 14, 15), (23, 59, 59)])
@pytest.mark.parametrize("tenor_type", [str, Tenor])
@pytest.mark.parametrize(
    "tenor, expected_date",
    [
        ("1d", (1, 2, 2024)),
        ("0D", (31, 1, 2024)),
        ("-1D", (30, 1, 2024)),
        ("1W", (7, 2, 2024)),
        ("0w", (31, 1, 2024)),
        ("-1W", (24, 1, 2024)),
        ("1M", (29, 2, 2024)),
        ("0M", (31, 1, 2024)),
        ("-1m", (31, 12, 2023)),
        ("13M", (28, 2, 2025)),
        ("-11M", (28, 2, 2023)),
        ("1y", (31, 1, 2025)),
        ("0Y", (31, 1, 2024)),
        ("-1Y", (31, 1, 2023)),
    ],
)
def test_add_tenor_preserves_time(tenor, expected_date, tenor_type, time):
    """Positive, zero and negative tenors preserve intraday values in every unit."""
    original = Date(31, 1, 2024, *time)

    result = original.add_tenor(tenor_type(tenor))

    assert_same_date(result, Date(*expected_date, *time))
    assert result is not original
    assert_same_date(original, Date(31, 1, 2024, *time))


@pytest.mark.parametrize(
    "tenor, expected_date",
    [
        ("1D", (1, 3, 2024)),
        ("-1W", (22, 2, 2024)),
        ("1M", (29, 3, 2024)),
        ("12M", (28, 2, 2025)),
        ("-12M", (28, 2, 2023)),
        ("1Y", (28, 2, 2025)),
        ("-1Y", (28, 2, 2023)),
    ],
)
def test_add_tenor_from_leap_day(tenor, expected_date):
    """Leap-day adjustments preserve time and clamp to the target month end."""
    original = Date(29, 2, 2024, 13, 14, 15)

    result = original.add_tenor(tenor)

    assert_same_date(result, Date(*expected_date, 13, 14, 15))


def test_add_tenor_list_preserves_time():
    """Mixed string and Tenor inputs are independently applied to the same date."""
    original = Date(31, 1, 2024, 13, 14, 15)
    tenors = ["1D", Tenor("-1W"), "1M", Tenor("1Y"), "0M"]
    expected_dates = [
        (1, 2, 2024),
        (24, 1, 2024),
        (29, 2, 2024),
        (31, 1, 2025),
        (31, 1, 2024),
    ]

    results = original.add_tenor(tenors)

    assert isinstance(results, list)
    assert len(results) == len(expected_dates)
    for result, expected_date in zip(results, expected_dates):
        assert_same_date(result, Date(*expected_date, 13, 14, 15))
        assert result is not original
    assert_same_date(original, Date(31, 1, 2024, 13, 14, 15))
