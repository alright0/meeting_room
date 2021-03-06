from datetime import datetime

from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.forms.fields import CharField
from django.forms.models import ModelChoiceField
from django.forms.widgets import DateTimeInput
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .models import Room, Schedule


class LoginForm(forms.Form):
    """логин"""

    username = CharField()
    password = CharField(widget=forms.PasswordInput)


class UserForm(forms.Form):
    """Форма обновления данных пользователя"""

    queryset = User.objects.all()
    user = ModelChoiceField(
        queryset=queryset,
        required=False,
        label="Сотрудник:",
    )
    groups = forms.BooleanField(
        label="Является менеджером:",
    )

    field_order = ["user", "groups"]

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)

        self.fields["user"].label_from_instance = lambda user: f"{user.get_full_name()}"


class RoomForm(forms.ModelForm):
    """Форма создания и обновления комнаты"""

    rooms = Room.objects.all()
    id = forms.ModelChoiceField(
        queryset=rooms, required=False, empty_label="+ создать комнату", label="Комнаты"
    )

    class Meta:
        model = Room
        fields = "__all__"

        labels = {
            "name": "Название комнаты",
            "seats": "количество мест",
            "board": "маркерная доска",
            "projector": "Проектор",
            "description": "Описание",
        }

    field_order = [
        "id",
        "name",
        "seats",
        "board",
        "projector",
        "description",
    ]

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
                }
            ),
            "end_time": DateTimeInput(
                attrs={
                    "type": "datetime-local",
                    "min": datetime.now().strftime("%Y-%m-%dT%H:00"),
                }
            ),
        }

    def __init__(self, room_id, *args, **kwargs):
        super(ScheduleForm, self).__init__(*args, **kwargs)
        self.room_schedule = Schedule.objects.filter(
            room_id=room_id,
            status=True,
            start_time__gt=timezone.now(),
        ).all()
        self.fields["manager_id"].queryset = User.objects.filter(groups__name="manager")
        self.fields[
            "manager_id"
        ].label_from_instance = lambda user: f"{user.get_full_name()}"

    def clean(self, *args, **kwargs):
        room_schedule = self.room_schedule
        cleaned_data = self.cleaned_data
        start_time = cleaned_data["start_time"]
        end_time = cleaned_data["end_time"]
        manager_id = cleaned_data["manager_id"]

        if start_time < timezone.localtime():
            raise ValidationError(_("Дата начала меньше текущего времени!"))

        if end_time < start_time:
            raise ValidationError(_("Дата окончания совещания меньше даты начала!"))

        manager = User.objects.get(id=manager_id.id)
        if not manager.groups.filter(name="manager"):
            raise ValidationError(
                _(
                    "Вы не можете назначить встречу сотруднику, не являющемуся офис-менеджером!"
                )
            )

        for record in room_schedule:
            if (
                start_time > record.start_time
                and start_time < record.end_time
                or end_time > record.start_time
                and end_time < record.end_time
            ):
                raise ValidationError(
                    _("Эта дата уже занята! Пожалуйста, выберите другую дату")
                )

        return cleaned_data
