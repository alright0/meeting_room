from django.db import models
from django.db.models.base import Model
from django.db.models.fields import CharField

# Create your models here.


class Role(models.Model):
    """Describe user roles"""

    id = models.AutoField(primary_key=True, unique=True)
    role = models.CharField(max_length=150, unique=True, default="Coworker")

    def __repr__(self):
        pass


class User(models.Model):
    """Describe users"""

    id = models.AutoField(primary_key=True, unique=True)
    login = models.CharField(max_length=50, unique=True)
    password_hash = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150, unique=False)
    last_name = models.CharField(max_length=150, unique=False)
    role_id = models.ForeignKey(
        Role, related_name="id_C", on_delete=models.SET_NULL, null=True
    )

    def __repr__(self):
        pass


class Room(models.Model):
    """Describe rooms"""

    id = models.AutoField(primary_key=True, unique=True)
    name = models.CharField(max_length=150, unique=True)
    seats = models.IntegerField(null=True)
    has_desk = models.BooleanField(default=False)
    has_proj = models.BooleanField(default=False)
    description = models.TextField(default="No description")

    def __repr__(self) -> str:

        include_desk = "With desk. " if self.has_desk else ""

        include_proj = "With projector. " if self.has_proj else ""

        description = (
            f"Description: {self.description}"
            if self.description != "No description. "
            else ""
        )

        return f"Room: {self.name}. {self.seats} seats. {include_desk}{include_proj}{description}."


class Schedule(models.Model):
    """Describe schedule model"""

    Organizator_id = models.ForeignKey(
        User, related_name="id_organizator", on_delete=models.SET_NULL, null=True
    )
    manager_id = models.ForeignKey(
        User, related_name="id_manager", on_delete=models.SET_NULL, null=True
    )
    room_id = models.ForeignKey(
        Room, related_name="id_role", on_delete=models.SET_NULL, null=True
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = CharField(max_length=1, default="W")
