from datetime import datetime


def formatted_time(date_formatted: datetime) -> str:
    """Возвращает отформатированную дату"""

    return date_formatted.strftime("%x %X")
