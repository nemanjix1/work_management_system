from django.urls import path
from . import views

urlpatterns = [
    path('attendance/', views.attendance_page, name='attendance'),
    path('attendance_login', views.attendance_login_page, name='attendance_login'),
]
    