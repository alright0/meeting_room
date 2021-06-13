from django.test import TestCase
from new_site.forms import RoomForm, ScheduleForm
from django.contrib.auth.models import User, Group
from new_site.models import Room, Schedule


class TestScheduleForm(TestCase):
    def setUp(self):
        self.room = Room.objects.create(
            name="Room 2001",
            seats=12,
            board=True,
            projector=False,
        )

        self.coworker = User.objects.create(
            username="coworker",
            password="UserUser1",
            first_name="test",
            last_name="coworker",
            email="a@a.ru",
        )

        self.manager = User.objects.create(
            username="manager",
            password="UserUser1",
            first_name="test",
            last_name="manager",
            email="b@a.ru",
        )

        manager_group = Group.objects.get(name="manager")
        manager_group.user_set.add(self.manager.id)

    def test_validate_room(self):
        """Валидация ожидаемых данных в RoomForm"""

        data = {
            "name": "test_room 201",
            "seats": 25,
            "board": True,
            "projector": True,
            "description": "TestDescription",
        }

        form = RoomForm(data=data)

    def test_validate_correct_schedule(self):
        """Валидация формы расписания с ожидаемыми данными"""

        data = {
            "start_time": "2021-12-13T21:00",
            "end_time": "2021-12-13T22:00",
            "manager_id": self.manager,
            "title": "any title avalaible",
        }
        form = ScheduleForm(room_id=self.room.id, data=data)
        self.assertTrue(form.is_valid())

    def test_validate_incorrect_yesterday_schedule(self):
        """Валидация формы расписания с датами раньше сегодня"""

        data = {
            "start_time": "2020-01-01T21:00",
            "end_time": "2020-01-01T22:00",
            "manager_id": self.manager,
            "title": "any title avalaible",
        }
        form = ScheduleForm(room_id=self.room.id, data=data)
        self.assertFalse(form.is_valid())

    def test_validate_incorrect_end_gt_start_schedule(self):
        """Валидация формы расписания с датой конца раньше начала"""

        data = {
            "start_time": "2020-02-01T21:00",
            "end_time": "2020-01-01T22:00",
            "manager_id": self.manager,
            "title": "any title avalaible",
        }
        form = ScheduleForm(room_id=self.room.id, data=data)
        self.assertFalse(form.is_valid())

    def test_validate_incorrect_role_schedule(self):
        """Валидация формы расписания с некорректной ролью менеджера"""

        data = {
            "start_time": "2021-02-01T21:00",
            "end_time": "2021-02-01T22:00",
            "manager_id": self.coworker,
            "title": "any title avalaible",
        }
        form = ScheduleForm(room_id=self.room.id)

        self.assertFalse(form.is_valid())
