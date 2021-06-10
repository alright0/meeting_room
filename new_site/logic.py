from datetime import datetime, timedelta


def formatted_time(date_formatted: datetime) -> str:
    """Возвращает отформатированную дату"""

    return date_formatted.strftime("%d.%m.%Y %H:%M")
