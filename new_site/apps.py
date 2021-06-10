from django.apps import AppConfig
from django.db.models.signals import post_migrate


def create_permissions(codenames: list) -> list:
    from django.contrib.auth.models import Permission

    return [Permission.objects.get(codename=codename) for codename in codenames]


def create_groups(sender, **kwargs):
    """проверка и создание групп при миграции"""

    from django.contrib.auth.models import Group, Permission

    coworker_group, _ = Group.objects.get_or_create(name="coworker")
    manager_group, _ = Group.objects.get_or_create(name="manager")

    coworker_permissions = [
        "view_room",
        "add_schedule",
        "view_schedule",
    ]
    manager_permissions = [
        "add_room",
        "change_room",
        "delete_room",
        "view_room",
        "add_schedule",
        "change_schedule",
        "delete_schedule",
        "view_schedule",
        "add_user",
        "change_user",
        "view_user",
    ]

    [
        coworker_group.permissions.add(permission)
        for permission in create_permissions(coworker_permissions)
    ]

    [
        manager_group.permissions.add(permission)
        for permission in create_permissions(manager_permissions)
    ]


class NewSiteConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "new_site"

    def ready(self):
        post_migrate.connect(create_groups, sender=self)
        import new_site.signals.handlers
