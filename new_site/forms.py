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


class LoginForm(forms.Form):
    """логин"""

    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class UserForm(forms.ModelForm):
    """Форма обновления данных пользователя"""

    users = User.objects.all()
    user_list = [(user.id, f"{user.first_name} {user.last_name}") for user in users]

    groups = forms.BooleanField()
    user = forms.ChoiceField(choices=user_list)

    class Meta:
        model = User
        fields = ["groups", "id"]  # , "first_name", "last_name", "email"]

        labels = {
            "id": "Сотрудник",
            # "first_name": "Имя",
            # "last_name": "Фамилия",
            # "email": "E-Mail",
            # "groups": "Менеджер",
        }

        # users = User.objects.all()
        # user_list = [(user.id, f"{user.first_name} {user.last_name}") for user in users]

        """widgets = {
            # "groups": forms.BooleanField(),
            "id": forms.ChoiceField(choices=user_list),
        }"""

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)


class RoomForm(forms.ModelForm):
    """Форма создания и обновления комнаты"""

    def _get_rooms_for_combobox():
        """возвращает список комнат для выпадающего списка"""

        rooms = Room.objects.all()
        rooms_list = []
        rooms_list.append(list((0, "+ Новая Комната")))
        for room in rooms:
            rooms_list.append(list((room.id, room.name)))

        return rooms_list

    new_name = forms.ChoiceField(choices=_get_rooms_for_combobox())

    class Meta:
        model = Room
        fields = "__all__"

        labels = {
            "new_name": "Комнаты",
            "name": "Название комнаты",
            "seats": "количество мест",
            "board": "маркерная доска",
            "projector": "Проектор",
            "description": "Описание",
        }

    def clean_seats(self):
        cleaned_data = self.clean()
        seats = cleaned_data["seats"]

        if seats == 0:
            raise ValidationError(_("Количество мест должно быть больше 0!"))

        return seats

    def __init__(self, *args, **kwargs):
        super(RoomForm, self).__init__(*args, **kwargs)


class ScheduleForm(forms.ModelForm):
    """Форма создания встречи"""

    managers_queryset = User.objects.filter(groups=1).all()
    manager_id = ModelChoiceField(queryset=managers_queryset)

    class Meta:
        model = Schedule

        fields = ["manager_id", "title", "start_time", "end_time"]
        labels = {
            "manager_id": "Менеджер:",
            "title": "Тема:",
            "start_time": "Начало:",
            "end_time": "Конец:",
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
