from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r"rooms/(?P<post_id>\d+)/$", consumers.ChatConsumer.as_asgi()),
]