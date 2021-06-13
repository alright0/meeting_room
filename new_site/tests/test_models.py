from django.test import TestCase
from django.contrib.auth import get_user_model
from new_site.models import Room, Schedule


User = get_user_model()


class CoworkerValuebility(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create(
            username="test99",
            password="UserUser1",
            first_name="test",
            last_name="user",
            email="a@a.ru",
        )
        self.room = Room.objects.create(
            name="Room 2001",
            seats=12,
            board=True,
            projector=False,
        )

        self.schedule = Schedule.objects.create(
            start_time="2021-12-13T21:00",
            end_time="2021-12-13T22:00",
            organizator_id=User.objects.get(id=1),
            manager_id=User.objects.get(id=1),
            room_id=Room.objects.get(id=1),
            title="test_meeting",
        )

    def test_user_is_coworker(self):
        """автоназначение группы сотрудников после создания"""
        self.assertTrue(self.user.groups.filter(name="coworker"))

    def test_user_is_manager(self):
        """Не принадлежит группе менеджеров после создания"""
        self.assertFalse(self.user.groups.filter(name="manager"))

    def test_schedule_not_accepted(self):
        """Неопределенный статус собрания после создания"""
        self.assertIsNone(self.schedule.status)

    def test_room_autodescription(self):
        self.assertTrue(self.room.description == "Нет описания")
