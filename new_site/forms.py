from datetime import datetime

from django import forms
from django.core.exceptions import ValidationError
from django.forms.widgets import DateTimeInput
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .models import Room, Schedule, User
from .logic import datetimelocal_value


class ScheduleForm(forms.ModelForm):
    """Форма создания встречи"""

    class Meta:
        model = Schedule
        fields = ["manager_id", "title", "start_time", "end_time"]
        labels = {
            "title": "Тема:",
            "manager_id": "Менеджер",
            "start_time": "Начало встречи",
            "end_time": "Окончание встречи",
        }
        widgets = {
            "start_time": DateTimeInput(
                attrs={
                    "type": "datetime-local",
                    "min": datetime.now().strftime("%Y-%m-%dT%H:00"),
                    "value": datetimelocal_value(1),
                }
            ),
            "end_time": DateTimeInput(
                attrs={
                    "type": "datetime-local",
                    "min": datetime.now().strftime("%Y-%m-%dT%H:00"),
                    "value": datetimelocal_value(2),
                }
            ),
        }

    def __init__(self, room_id, *args, **kwargs):
        super(ScheduleForm, self).__init__(*args, **kwargs)
        self.room_schedule = Schedule.objects.filter(
            room_id=room_id, status=True, start_time__gt=timezone.now()
        ).all()

    def clean(self, *args, **kwargs):
        room_schedule = self.room_schedule
        cleaned_data = self.cleaned_data
        start_time = cleaned_data["start_time"]
        end_time = cleaned_data["end_time"]

        if start_time < timezone.now():
            raise ValidationError(_("Дата начала меньше текущего времени!"))

        if end_time < start_time:
            raise ValidationError(_("Дата окончания совещания меньше даты начала!"))

        for record in room_schedule:
            if (
                start_time >= record.start_time
                and start_time <= record.end_time
                or end_time >= record.start_time
                and end_time <= record.end_time
            ):
                raise ValidationError(
                    _("Эта дата уже занята! Пожалуйста, выберите другую дату")
                )

        return cleaned_data
