from django.urls import path

from rqueue.consumers import WSConsumer

ws_urlpatterns = [
    path('ws/some_url/', WSConsumer.as_asgi())
]