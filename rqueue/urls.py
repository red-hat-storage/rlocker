from django.urls import path
from rqueue import views

urlpatterns = [
    path('pendingrequests/', views.pending_requests_page, name='pending_requests_page'),
    path('finishedrequests/', views.finished_requests_page, name='finished_requests_page'),
]