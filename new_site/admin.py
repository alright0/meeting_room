from django.contrib import admin
from .models import Room, Schedule, User, Role

# Register your models here.
admin.site.register(Room)
admin.site.register(Role)
admin.site.register(User)
admin.site.register(Schedule)
