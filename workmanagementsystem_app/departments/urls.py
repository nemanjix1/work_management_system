from django.urls import path
from . import views

urlpatterns = [
    path('',views.home_page, name='home'),
    path('attendance/', views.attendance_page, name='attendance'),
    path('attendance_login/', views.attendance_login_page, name='attendance_login'),
    path('login/', views.login_page, name='login_page'),
    path('logout/', views.logout_view, name='logout_view'),
    path('projects/', views.projects_list, name='projects_list'),
    path('projects/add_project/', views.project_add, name='projects_add_project'),
    path('projects/project_detail/<int:project_id>/', views.project_details, name='project_details'),
    path('projects/project_edit/<int:project_id>/', views.project_edit, name='project_edit'),
    path('projects/archived/', views.archived_project, name='archived_projects'),
    path('projects/<int:project_id>/archive/', views.project_archive, name='project_archive'),
    path('departments/', views.departments_list, name='departments_list'),
    path('departments/<int:department_id>/', views.department_detail, name='department_detail'),
    path('departments/department_add/', views.department_add, name='department_add'),
    path('departments/department_edit/<int:department_id>/', views.department_edit, name='department_edit')
]
    