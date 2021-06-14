from django.urls import path
from api import views

urlpatterns = [
    path("", views.redirect_to_prior_location, name="redirect_to_prior_location"),
    path("resources/", views.resources_view, name="resources_view"),
    path(
        "resource/retrieve_entrypoint/<search_string>",
        views.retrieve_resource_entrypoint,
        name="retrieve_resource_entrypoint",
    ),
    # Example from web browser UI:
    # http://127.0.0.1:8000/api/resource/retrieve_name/aws-resource-3%3Fpriority=1%3Fsignoff=cerginba-cluster66666
    path(
        "resource/retrieve_name/<name>?priority=<priority>?signoff=<signoff>",
        views.retrieve_resource_by_name,
        name="retrieve_resource_by_name",
    ),
    path(
        "resource/retrieve_label/<label>?priority=<priority>?signoff=<signoff>",
        views.retrieve_resource_by_label,
        name="retrieve_resource_by_label",
    ),
    path("resource/<slug>", views.resource_view, name="resource_view"),
    path("rqueue/<slug>", views.rqueue_view, name="rqueue_view"),
    path("rqueues", views.rqueues_view, name="rqueues_view"),
    path(
        "pendingrequests",
        views.rqueues_status_pending_view,
        name="rqueues_status_pending_view",
    ),
    path(
        "present_requests",
        views.rqueues_status_present_view,
        name="rqueues_status_present_view",
    ),
]
