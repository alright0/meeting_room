from django.contrib.auth.models import User
from django.db import models
from django.db.models.base import Model
from django.db.models.fields import CharField
from django.utils import timezone

from .logic import formatted_time


# Create your models here.
class Room(models.Model):
    """Описывает комнаты"""

    id = models.AutoField(primary_key=True, unique=True)
    name = models.CharField(max_length=150, unique=True)
    seats = models.PositiveIntegerField(null=True)
    board = models.BooleanField(default=False)
    projector = models.BooleanField(default=False)
    description = models.TextField(default="Нет описания")

    def __str__(self) -> str:

        include_board = "С маркерной доской. " if self.board else ""
        include_projector = "С проектором. " if self.projector else ""
        description = (
            f"Описание: {self.description}"
            if self.description != "Нет описания. "
            else ""
        )

        return f"{self.name}. {self.seats} мест(а). {include_board}{include_projector}{description}."


class Schedule(models.Model):
    """Описывает расписание комнат"""

    id = models.AutoField(primary_key=True, unique=True)
    organizator_id = models.ForeignKey(
        User, related_name="id_organizator", on_delete=models.CASCADE, null=True
    )
    manager_id = models.ForeignKey(
        User, related_name="id_manager", on_delete=models.CASCADE, null=True
    )
    room_id = models.ForeignKey(
        Room, related_name="id_role", on_delete=models.SET_NULL, null=True
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.BooleanField(default=False)
    title = models.CharField(max_length=140, default="(Без названия)")

    def __str__(self):

        status = "Подтвеждено" if self.status else "Ожидает подтверждения"
        start_time = formatted_time(self.start_time)
        end_time = formatted_time(self.end_time)

        return f"Начало: {start_time}, Конец: {end_time}. Статус: {status}"

    @classmethod
    def get_room_statuses(cls, rooms) -> dict:
        """Возвращает словарь ``{room_id: ближайшая дата совещания}``"""

        schedule = dict()

        for room in rooms:
            nearest_meeting = (
                cls.objects.filter(
                    room_id_id=room.id, status=True, start_time__gt=timezone.now()
                )
                .order_by("start_time")
                .first()
            )

            if nearest_meeting:
                start_time = formatted_time(nearest_meeting.start_time)
                end_time = formatted_time(nearest_meeting.end_time)

                nearest_meet = f"Занята с: {start_time} до: {end_time}"
            else:
                nearest_meet = "Свободна"

            schedule[str(room.id)] = nearest_meet

        return schedule

    @classmethod
    def get_room_schedule(cls, room) -> list:
        """Принимает экземпляр комнаты и Возвращает расписание комнаты"""

        return list(
            cls.objects.filter(
                room_id_id=room.id, status=True, start_time__gt=timezone.now()
            )
            .order_by("start_time")
            .all()
        )

    @classmethod
    def meetings_to_approve(cls, user_id):
        """Принимает ``user_id`` и возвращает список встречь для подтверждения"""

        return list(
            cls.objects.filter(
                manager_id_id=user_id, status=False, start_time__gt=timezone.now()
            )
            .values(
                "organizator_id__first_name",
                "organizator_id__last_name",
                "title",
                "room_id__name",
                "start_time",
                "end_time",
                "id",
            )
            .order_by("start_time")
            .all()
        )