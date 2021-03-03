from django.apps import AppConfig


class LockableResourceConfig(AppConfig):
    name = 'lockable_resource'

    def ready(self):
        import lockable_resource.signals
