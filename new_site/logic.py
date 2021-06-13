from datetime import datetime
from django.utils import timezone


def formatted_time(date_formatted: datetime) -> str:
    """Возвращает отформатированную дату"""

    date_formatted = timezone.localtime(date_formatted)
    return date_formatted.strftime("%d.%m.%Y %H:%M")


def parse_meeting_id(meeting_id: str) -> int:
    return int(meeting_id.replace("meeting_id_", ""))
