from datetime import datetime

from django import forms
from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError
from django.forms.fields import ChoiceField
from django.forms.models import ModelChoiceField
from django.forms.widgets import DateTimeInput, Select, SelectDateWidget, SelectMultiple
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .logic import datetimelocal_value
from .models import Room, Schedule


class UserForm(forms.ModelForm):
    """Форма обновления данных пользователя"""

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]


class RoomForm(forms.ModelForm):
    """Форма создания и обновления комнаты"""

    rooms = Room.objects.all()
    rooms_list = []
    rooms_list.append(list((0, "+ Новая Комната")))
    for room in rooms:
        rooms_list.append(list((room.id, room.name)))
    new_name = forms.ChoiceField(choices=rooms_list)

    def __init__(self, *args, **kwargs):
        super(RoomForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Room
        fields = "__all__"
        # exclude = []
        # fields = ["name", "seats", "board", "projector", "description"]
        labels = {
            "new_name": "Комнаты",
            "name": "Название комнаты",
            "seats": "количество мест",
            "board": "маркерная доска",
            "projector": "Проектор",
            "description": "Описание",
        }

        rooms = Room.objects.all()
        rooms_list = []
        rooms_list.append(list((0, "+ Новая Комната")))
        for room in rooms:
            rooms_list.append(list((room.id, room.name)))

    def clean_seats(self):
        cleaned_data = self.clean()
        seats = cleaned_data["seats"]

        if seats == 0:
            raise ValidationError(_("Количество мест должно быть больше 0!"))

        return seats


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
