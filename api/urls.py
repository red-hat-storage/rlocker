from django.urls import path
from api import views

urlpatterns = [
    path('', views.redirect_to_prior_location, name='redirect_to_prior_location'),
    path('resources/', views.resources_view, name='resources_view'),
    path('resource/retrieve/<search_string>', views.retrieve_resource_view, name='retrieve_resource_view'),
    path('resource/<slug>', views.resource_view, name='resource_view'),
    path('pendingrequest/<slug>', views.pendingrequest_view, name='pendingrequest_view'),
    path('pendingrequests', views.pendingrequests_view, name='pendingrequests_view'),
]