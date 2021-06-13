from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import RequestFactory, TestCase

from new_site.models import Room
from new_site.views import add_room, coworkers, index, room_schedule


User = get_user_model()

class coworker_user_access(TestCase):
    def setUp(self) -> None:
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

        self.room = Room.objects.create(
            name="Room 2001",
            seats=12,
            board=True,
            projector=False,
        )

    def test_coworker_access(self):
        """статус коды для роли сотрудника"""

        factory = RequestFactory()
        request = factory.get("")
        request.user = self.coworker

        self.assertEqual(index(request).status_code, 200)
        self.assertEqual(room_schedule(request, self.room.id).status_code, 200)
        self.assertEqual(coworkers(request).status_code, 302)
        self.assertEqual(add_room(request).status_code, 302)

    def test_manager_access(self):
        """статус коды для роли менеджера"""

        factory = RequestFactory()
        request = factory.get("")
        request.user = self.manager

        self.assertEqual(index(request).status_code, 200)
        self.assertEqual(room_schedule(request, self.room.id).status_code, 200)
        self.assertEqual(coworkers(request).status_code, 200)
        self.assertEqual(add_room(request).status_code, 200)
