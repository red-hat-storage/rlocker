from django.apps import AppConfig


class RqueueConfig(AppConfig):
    name = "rqueue"

    def ready(self):
        """
        We override the ready method of AppConfig, so the application
            could start listening to the signal we create in signals.py
        :return: None
        """

        import rqueue.signals
