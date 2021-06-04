import json
from datetime import datetime

from django.contrib.auth.models import Group, User
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone

from .logic import formatted_time
from .models import Room, Schedule
from .forms import ScheduleForm


# Create your views here.
def index(request):
    """Возвращает страницу со списком всех комнат и их описанием.
    Для менеджеров также возвращает список совещаний для подтверждения"""

    if request.method == "POST":

        if request.user.groups.filter(name="manager"):

            answer = request.POST.get("answer")
            meeting_id = request.POST.get("meeting_id")

            # здесь отклоняется или подтверждается встреча
            if answer:
                meet_id = int(meeting_id.replace("meeting_id ", ""))
                if answer == "accept":
                    this_meeting = Schedule.objects.get(id=meet_id)
                    this_meeting.status = True
                    this_meeting.save()
                    result = {"answer": "Встреча подтверждена!"}
                elif answer == "decline":
                    Schedule.objects.get(id=meet_id).delete()
                    result = {"answer": "Встреча отклонена!"}

                return HttpResponse(
                    json.dumps(result, cls=DjangoJSONEncoder),
                    content_type="application/json",
                )

            meetings_to_approve = json.dumps(
                Schedule.meetings_to_approve(request.user.id), cls=DjangoJSONEncoder
            )

        else:
            meetings_to_approve = json.dumps([{}])

        return HttpResponse(meetings_to_approve, content_type="application/json")

    rooms = Room.objects.all()
    schedule = Schedule.get_room_statuses(rooms)

    if request.user.groups.filter(name="manager"):
        meetings_to_approve = Schedule.meetings_to_approve(request.user.id)
    else:
        meetings_to_approve = None

    context = {
        "title": "Main Page",
        "rooms": rooms,
        "schedule": schedule,
        "meetings_to_approve": meetings_to_approve,
    }

    return render(request, "new_site/index.html", context)


def room_schedule(request, room_id):
    """Возвращает страницу с расписанием комнаты"""

    if request.method == "POST":
        form = ScheduleForm(room_id, request.POST)
        if form.is_valid():

            new_meeting = Schedule(
                start_time=request.POST["start_time"],
                end_time=request.POST["end_time"],
                organizator_id=request.user,
                manager_id=User.objects.get(id=request.POST["manager_id"]),
                room_id=Room.objects.get(id=room_id),
                title=request.POST["title"],
            )
            new_meeting.save()

    else:
        form = ScheduleForm(room_id)

    room = Room.objects.get(id=room_id)
    schedule = Schedule.get_room_schedule(room)

    context = {
        "title": f"{room.name}. Расписание",
        "room": room,
        "schedule": schedule,
        "form": form,
    }

    return render(request, "new_site/room_schedule.html", context)


def coworkers(request):

    users = User.objects.all()

    for user in users:

        user.groups.change(2)

    context = {"user": users}

    return render(request, "new_site/coworkers.html", context)


def login(request):
    pass
