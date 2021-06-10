from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save, post_migrate
from django.dispatch import receiver


@receiver(post_save, sender=User)
def add_user_to_group(sender, instance, created, **kwargs):
    if created:
        coworker_group = Group.objects.get(name="coworker")
        instance.groups.add(coworker_group)
