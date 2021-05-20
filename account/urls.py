from account import views
from django.urls import path

urlpatterns = [
    path('login/', views.login_page, name='login_page'),
    path('change_password/', views.change_password_page, name='change_password_page'),
    path('logout/', views.logout_page, name='logout_page'),
]