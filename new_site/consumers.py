import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.post_id = self.scope["url_route"]["kwargs"]["post_id"]
        self.post_group_name = "post_%s" % self.post_id

        await self.channel_layer.group_add(self.post_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.post_group_name, self.channel_name)

    async def receive(self, text_data):
        print(text_data)
        text_data_json = json.loads(text_data)
        # text_data_json = json.loads(text_data)
        # new_comment = await self.create_new_comment(text_data_json)

        await self.channel_layer.group_send(
            self.post_group_name, {"type": "new_comment", "message": text_data_json}
        )

    async def new_comment(self, event):
        await self.send(text_data=json.dumps({"message": "message"}))

    @database_sync_to_async
    def create_new_comment(self, text):
        pass
