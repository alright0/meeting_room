import json

from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.serializers.json import DjangoJSONEncoder

from .models import Schedule


class NotificationConsumer(AsyncWebsocketConsumer):
    """Класс обслуживания каналов"""

    async def connect(self):
        self.user_id = self.scope["url_route"]["kwargs"]["user_id"]
        self.user_group_name = "user_%s" % self.user_id

        await self.channel_layer.group_add(self.user_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.user_group_name, self.channel_name)

    async def receive(self, text_data):
        await self.channel_layer.group_send(
            self.user_group_name,
            {"type": "meeting_answer", "message": json.loads(text_data)},
        )

    async def meeting_answer(self, event):

        meeting_id = await self.meeting_details(event)
        await self.send(text_data=meeting_id)

    @database_sync_to_async
    def meeting_details(self, text):

        meeting_id = int(text["message"]["meeting_id"].replace("meeting_id_", ""))
        meeting_dateils = Schedule.meeting_details(meeting_id)
        meeting_dateils["answer"] = text["message"]["answer"]

        return json.dumps(meeting_dateils, cls=DjangoJSONEncoder)
