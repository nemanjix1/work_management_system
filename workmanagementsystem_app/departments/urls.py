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
    path('departments/department_edit/<int:department_id>/', views.department_edit, name='department_edit'),
    path('machines/', views.machines_list, name='machines_list'),
    path('machines/<int:machine_id>/', views.machine_detail, name='machine_detail'),
    path('machines/machine_add/', views.machine_add, name='machine_add'),
    path('machines/machine_edit/<int:machine_id>', views.machine_edit, name='machine_edit'),
    path('teams/',views.teams_list, name='teams_list'),
    path('teams/<int:team_id>/', views.team_detail, name='team_detail'),
    path('teams/team_add/',views.team_add, name='team_add'),
    path('teams/team_edit/<int:team_id>/', views.team_edit, name='team_edit'),
    path('workers/', views.workers_list, name='workers_list'),
    path('workers/<int:worker_id>/', views.worker_detail, name='worker_detail'),
    path('workers/worker_edit/<int:worker_id>/', views.worker_edit, name='worker_edit'),
    path('workers/worker_add/',views.worker_add, name='worker_add'),
    path('audit_logs/', views.audit_log_list, name='audit_logs'),
    path('issues/',views.issues_list, name='issues_list'),
    path('issues/<int:issue_id>/',views.issue_detail,name='issue_detail'),
    path('issues/issue_add/', views.issue_add, name='issue_add'),
    path('issues/issue_status_update/<int:issue_id>/', views.issue_status_update, name='issue_status_update'),
    path('issues/<int:issue_id>/intervention_add', views.intervention_add, name='intervention_add'),
    path('issues/interventions/<int:intervention_id>/finish/', views.intervention_finish, name='intervention_finish'),
    path('issues/<int:issue_id>/comment_add', views.comment_add, name='comment_add'),
    path('issues/<int:issue_id>/attachment_add/',views.issue_attachment_add, name='issue_attachment_add'),
    path('attachments/<int:attachment_id>/delete/',views.attachment_delete, name='attachment_delete')

]
    