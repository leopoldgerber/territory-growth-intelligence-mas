import datetime

from dateutil.relativedelta import relativedelta


def build_months(month_amount: int, today: datetime.date | None = None) -> list[str]:
    """Build previous month names.
    Args:
        month_amount (int): Count of months.
        today (datetime.date | None): Reference date."""
    reference_date = today or datetime.date.today()
    month_list = [
        (reference_date - relativedelta(months=month_index)).strftime('%b')
        for month_index in range(1, month_amount + 1)
    ]
    return month_list


def metric_period(
    month_amount: int,
    today: datetime.date | None = None,
    report_year: int | None = None,
) -> tuple[str, str, str]:
    """Build metric period.
    Args:
        month_amount (int): Count of months.
        today (datetime.date | None): Reference date.
        report_year (int | None): Report year."""
    reference_date = today or datetime.date.today()
    first_month = (reference_date - relativedelta(months=month_amount)).strftime('%b')
    last_month = reference_date.strftime('%b')
    year = str(report_year) if report_year is not None else reference_date.strftime('%Y')
    return first_month, last_month, year


def month_number(month_name: str) -> int:
    """Convert month name to number.
    Args:
        month_name (str): Month name."""
    return datetime.datetime.strptime(month_name, '%b').month


def month_abbr(month_value: str) -> str:
    """Convert month number to name.
    Args:
        month_value (str): Month number."""
    return datetime.datetime.strptime(month_value, '%m').strftime('%b')


def add_month_year(month_name: str, year: str) -> str:
    """Build month year value.
    Args:
        month_name (str): Month name.
        year (str): Year value."""
    month_value = str(month_number(month_name))
    return datetime.datetime.strptime(f'{month_value} {year}', '%m %Y').strftime('%d.%m.%Y')
