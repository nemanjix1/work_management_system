from django.urls import path
from . import views

urlpatterns = [
    path('',views.home_page, name='home'),
    path('attendance/', views.attendance_page, name='attendance'),
    path('attendance_login/', views.attendance_login_page, name='attendance_login'),
    path('login/', views.login_page, name='login_page'),
    path('logout/', views.logout_view, name='logout_view'),
]
    