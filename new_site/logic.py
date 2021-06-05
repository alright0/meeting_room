from datetime import datetime, timedelta


def formatted_time(date_formatted: datetime) -> str:
    """Возвращает отформатированную дату"""

    return date_formatted.strftime("%d.%m.%Y %H:%M")


def datetimelocal_value(offset_hours):
    """возвращает текущее значение времени для datetime-local"""
    return datetime.strftime(
        datetime.now() + timedelta(hours=offset_hours), "%Y-%m-%dT%H:00"
    )
