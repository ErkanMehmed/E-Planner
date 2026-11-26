from django.apps import AppConfig
from django.db.models.signals import post_migrate


def create_groups(sender, **kwargs):
    from django.contrib.auth.models import Group
    for name in ('Cooks', 'Guests'):
        Group.objects.get_or_create(name=name)


class AccountsConfig(AppConfig):
    name = 'accounts'

    def ready(self):
        from . import signals
        post_migrate.connect(create_groups, sender=self)
