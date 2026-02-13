"""rlocker URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings

urlpatterns = [
    path("admin/", admin.site.urls),
    path("lockable_resource/", include("lockable_resource.urls")),
    path("api/", include("api.urls")),
    path("", include("account.urls")),
    path("", include("rqueue.urls")),
    path("", include("dashboard.urls")),
    path("", include("health.urls")),
    path("admin_tools/", include("admin_tools.urls")),
    path("patch_notifier/", include("patch_notifier.urls")),
    path("patch_notifier/", include("patch_notifier.urls")),
    path('resoucesdc/', include('resoucesdc.urls')),
]
# AddOns Urls
for addon in settings.INSTALLED_ADDONS:
    urlpatterns.append(path(f"{addon}/", include(f"{addon}.urls")))
