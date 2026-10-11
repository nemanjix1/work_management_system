from django.shortcuts import render,redirect,get_object_or_404
from .models import User,AuditLog,Attendance,AttendanceEvent,Project,Department,Machine,Team,IssueStatusChange,Intervention
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import ProjectForm,DepartmentForm,InterventionForm,WorkerForm,IssueStatusForm,WorkerCreateForm,MachineForm,TeamForm,IssueForm
from django.contrib.auth.decorators import permission_required
from django.core.paginator import Paginator
from .access import get_visible_workers,get_visible_issues, get_visible_teams,get_visible_projects,get_visible_departments,get_visible_machines,get_visible_audit
def attendance_login_page(request):
    if request.method=="POST":
        username=request.POST.get("username")
        password=request.POST.get("password")
        user=authenticate(username=username,
        password=password
        )
        if not user:
            messages.error(
                request,
                "Pogresan broj zaposlenog ili lozinka"
            )
        if user:
            login(request,user)
            return redirect('attendance')
    return render(request, 'departments/attendance_login.html')


@login_required
def attendance_page(request):
    if request.method=="POST":
        action=request.POST.get("action")
        if action=="check-in":
            attendance=Attendance(
                user=request.user
            )
            try:
                attendance.full_clean()
                attendance.save()
                logout(request)
                return render(
                        request,
                        'departments/attendance_result.html',
                        {'result_message':'Uspesno ste se prijavili na posao'}
                    )
                
            except ValidationError as e:
                messages.error(request, e.messages[0])
            return redirect('attendance')
        elif action=="check-out":
            attendance=Attendance.objects.filter(
                    user=request.user,
                    check_out__isnull=True
                ).first()
            if attendance:
                try:
                    attendance.check_out=timezone.now()
                    attendance.full_clean()
                    attendance.save()
                    logout(request)
                    return render(
                        request,
                        'departments/attendance_result.html',
                        {'result_message':'Uspesno ste se odjavili sa posla'}
                    )
                   
                except ValidationError as e:
                    messages.error(request,e.messages[0])
            else:
                messages.error(
                    request,
                    "Nemate aktivnu prijavu na poslu"
                )
            return redirect('attendance')
    active_attendance=Attendance.objects.filter(
        user=request.user,
        check_out__isnull=True
    ).first()
    last_event=None
    if active_attendance:
        last_event=AttendanceEvent.objects.filter(attendance=active_attendance
        ).order_by('-event_time').first()
    return render(request,
        'departments/attendance.html',
        {'active_attendance': active_attendance,
        'last_event': last_event
        }
    )

def login_page(request):
    if request.method=="POST":
        form=AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            user=form.get_user()
            login(request,user)
            return redirect('home')

    else:
        form=AuthenticationForm()

    return render(
            request,
            'departments/login.html',
            {'form': form}
        )

def logout_view(request):
    if request.method=="POST":
        logout(request)
        return redirect('login_page')
    return redirect('home')     


@login_required
def home_page(request):
    return render(request, 'departments/home.html')


@login_required
def projects_list(request):
    visible_projects=get_visible_projects(request.user)
    projects=visible_projects.filter(is_archived=False)
    paginator=Paginator(projects, 4)
    page_number=request.GET.get('page')
    page_obj=paginator.get_page(page_number)    
    return render(request, 
    'departments/projects_list.html',
     {'page_obj': page_obj})

@login_required
@permission_required('departments.add_project', raise_exception=True)
def project_add(request):
    if request.method=="POST":
        form=ProjectForm(request.POST,current_user=request.user)
        if form.is_valid():
            project=form.save()
           
            AuditLog.objects.create(user=request.user,action=f'project_created',
                    object_type='Project',object_id=project.id,
                    old_value="",new_value=project.name
                    )
            return redirect('projects_list')
    else:
        form=ProjectForm(current_user=request.user)
    return render(request, 
    'departments/projects_add.html', 
    {'form': form})

@login_required
@permission_required('departments.view_project', raise_exception=True)
def project_details(request, project_id):
    visible_projects=get_visible_projects(request.user)
    project = get_object_or_404(visible_projects, pk=project_id)
    return render(request,
                    'departments/project_details.html',
                    {'project': project}
                    )

@login_required
@permission_required('departments.change_project', raise_exception=True)
def project_edit(request, project_id):
    visible_projects=get_visible_projects(request.user)
    project=get_object_or_404(visible_projects, pk=project_id)
    if request.method=="POST":
        old_values={
            'name': project.name,
            'code': project.code,
            'status': project.status

        }
        old_departments=set(project.departments.values_list('id',flat=True))
        form=ProjectForm(request.POST,instance=project,current_user=request.user)
        if form.is_valid():
            form.save()
            new_values={
            'name': project.name,
            'code': project.code,
            'status': project.status
            }
            new_departments=set(project.departments.values_list('id',flat=True))

            for field_name in old_values:
                if old_values[field_name]!=new_values[field_name]:
                    AuditLog.objects.create(user=request.user,action=f'project_{field_name}_changed',
                    object_type='Project',object_id=project.id,
                    old_value=str(old_values[field_name]),new_value=str(new_values[field_name])
                    )
            if old_departments!=new_departments:
                AuditLog.objects.create(user=request.user,action=f'project_departments_changed',
                    object_type='Project',object_id=project.id,
                    old_value=str(old_departments),new_value=str(new_departments)
                    )
            return redirect('projects_list')
    else:
        form=ProjectForm(instance=project,current_user=request.user)
    return render(
        request,
        'departments/project_edit.html',
        {'form': form,
         'project': project
         }
    )
@login_required
@permission_required('departments.change_project', raise_exception=True)
def project_archive(request, project_id):
    visible_projects=get_visible_projects(request.user)
    project=get_object_or_404(visible_projects, pk=project_id)
   
    if request.method=="POST":
        old_archived=project.is_archived
        project.is_archived=True
        project.archived_at=timezone.now()
        project.save()
        new_archived=project.is_archived
        if old_archived!=new_archived:
            AuditLog.objects.create(user=request.user,action='project_archived',
                                    object_type='Project',object_id=project.id,
                                    old_value=str(old_archived), new_value=str(new_archived)
                                    )
    return redirect('projects_list')

@login_required
@permission_required('departments.view_project', raise_exception=True)
def archived_project(request):
    visible_projects=get_visible_projects(request.user)
    projects=visible_projects.filter(is_archived=True)
    return render(
        request,
        'departments/project_archived.html',
        {'projects': projects}
    )

@login_required
def departments_list(request):
    departments=get_visible_departments(request.user)
    return render(request,
                'departments/departments_list.html',
                {'departments': departments}

    )
@login_required
def department_detail(request, department_id):
    visible_departments=get_visible_departments(request.user)
    department=get_object_or_404(visible_departments, pk=department_id)
    return render(
        request,
        'departments/department_details.html',
        {'department': department}
    )

@login_required
@permission_required('departments.add_department', raise_exception=True)
def department_add(request):
    if request.method=="POST":
        form=DepartmentForm(request.POST)
        if form.is_valid():
            department=form.save()
            AuditLog.objects.create(user=request.user,action='department_created',
                    object_type='Department',object_id=department.id,
                    old_value="",new_value=department.name
                    )
            return redirect('departments_list')
    else:
         form=DepartmentForm()
    return render(request,
                    'departments/department_add.html',
                    {'form': form}
        )

@login_required
@permission_required('departments.change_department', raise_exception=True)
def department_edit(request, department_id):
    visible_departments=get_visible_departments(request.user)
    department=get_object_or_404(visible_departments, pk=department_id)
    if request.method=="POST":
        old_values={
            'name': department.name,
            'description': department.description,
            'location': department.location,
            'code': department.code
        }
        form=DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            new_values={
            'name': department.name,
            'description': department.description,
            'location': department.location,
            'code': department.code
        }
            for field_name in old_values:
                if old_values[field_name]!=new_values[field_name]:
                    AuditLog.objects.create(user=request.user,action=f'department_{field_name}_changed',
                        object_type='Department',object_id=department.id,
                        old_value=str(old_values[field_name]),new_value=str(new_values[field_name])
                        )
            return redirect('departments_list')
    else:
        form=DepartmentForm(instance=department)
    return render(request,
                'departments/department_edit.html',
                {'form': form}

    )

@login_required
def machines_list(request):
    machines=get_visible_machines(request.user)
    return render(request,
                    'departments/machines_list.html',
                    {'machines': machines}
                    )
@login_required
def machine_detail(request, machine_id):
    visible_machines=get_visible_machines(request.user)
    machine=get_object_or_404(visible_machines,pk=machine_id)
    return render(request,
                    'departments/machine_detail.html',
                    {'machine': machine}
                    )

@login_required
@permission_required('departments.add_machine', raise_exception=True)
def machine_add(request):
    if request.method=="POST":
        form=MachineForm(request.POST,current_user=request.user)
        if form.is_valid():
            machine=form.save()
            AuditLog.objects.create(user=request.user,action='machine_created',
                    object_type='Machine',object_id=machine.id,
                    old_value="",new_value=machine.name
                    )
            return redirect('machines_list')
    else:
        form=MachineForm(current_user=request.user)
    return render(request,
                    'departments/machine_add.html',
                    {'form':form}
                    )
                    
@login_required
@permission_required('departments.change_machine', raise_exception=True)
def machine_edit(request, machine_id):
    visible_machines=get_visible_machines(request.user)
    machine=get_object_or_404(visible_machines, pk=machine_id)
    if request.method=="POST":
        form=MachineForm(request.POST, instance=machine, current_user=request.user)
        old_values={
            'name': machine.name,
            'code': machine.code,
            'status': machine.status,
            'department': machine.department
        }
        if form.is_valid():
            form.save()
            new_values={
            'name': machine.name,
            'code': machine.code,
            'status': machine.status,
            'department': machine.department
            }
            for field_name in old_values:
                if old_values[field_name]!=new_values[field_name]:
                    AuditLog.objects.create(user=request.user,action=f'machine_{field_name}_changed',
                                            object_type='Machine',object_id=machine.id,
                                            old_value=str(old_values[field_name]),new_value=str(new_values[field_name])
                                          )
            return redirect('machines_list')
    else:
        form=MachineForm(instance=machine,current_user=request.user)
    return render(request,
                    'departments/machine_edit.html',
                    {'form':form}
                    )

@login_required
def teams_list(request):
    teams=get_visible_teams(request.user)
    return render(request,
                    'departments/teams_list.html',
                    {'teams':teams}
                    )

@login_required
def team_detail(request,team_id):
    visible_teams=get_visible_teams(request.user)
    team=get_object_or_404(visible_teams,pk=team_id)
    users=User.objects.filter(team=team)
    return render(request,
                    'departments/team_detail.html',
                    {'team':team,
                     'users':users}
                    )

@login_required
@permission_required('departments.add_team', raise_exception=True)
def team_add(request):
    if request.method=="POST":
        form=TeamForm(request.POST,current_user=request.user)
        if form.is_valid():
            team=form.save()
            AuditLog.objects.create(user=request.user,action='team_created',
                    object_type='Team',object_id=team.id,
                    old_value="",new_value=team.name
                    )
            return redirect('teams_list')
    else:
        form=TeamForm(current_user=request.user)
    return render(request,
                    'departments/team_add.html',
                    {'form':form}

    )

@login_required
@permission_required('departments.change_team', raise_exception=True)
def team_edit(request, team_id):
    visible_teams=get_visible_teams(request.user)
    team=get_object_or_404(visible_teams,pk=team_id)
    if request.method=="POST":
        form=TeamForm(request.POST, instance=team, current_user=request.user)
        old_values={
            'name': team.name,
            'department': team.department,
            'team_leader': team.team_leader
        }
        if form.is_valid():
            form.save()
            new_values={
            'name': team.name,
            'department': team.department,
            'team_leader': team.team_leader
                }
            for field_name in old_values:
                if old_values[field_name]!=new_values[field_name]:
                    AuditLog.objects.create(user=request.user,action=f'team_{field_name}_changed',
                        object_type='Team',object_id=team.id,
                        old_value=str(old_values[field_name]),new_value=str(new_values[field_name])
                        )
            return redirect('teams_list')
    else:
        form=TeamForm(instance=team,current_user=request.user)
    return render(request,
                    'departments/team_edit.html',
                    {'form':form}
                    )

@login_required
def workers_list(request):
    workers=get_visible_workers(request.user)
    return render(request,
                    'departments/workers_list.html',
                    {'workers':workers}
                )
@login_required
def worker_detail(request, worker_id):
    visible_workers=get_visible_workers(request.user)
    worker=get_object_or_404(visible_workers, pk=worker_id)
    return render(request,
                    'departments/worker_detail.html',
                    {'worker':worker}
                    )

@login_required
@permission_required('departments.change_user', raise_exception=True)
def worker_edit(request, worker_id):
    visible_workers = get_visible_workers(request.user)
    worker=get_object_or_404(visible_workers, pk=worker_id)
    if request.method=="POST":
        old_values={
            'role': worker.role,
            'department': worker.department,
            'team': worker.team,
            'phone_number': worker.phone_number
            }
        form=WorkerForm(request.POST, instance=worker, current_user=request.user)
        if form.is_valid():
           
            form.save()
            new_values={
                'role': worker.role,
                'department': worker.department,
                'team': worker.team,
                'phone_number': worker.phone_number
                }
            for field_name in old_values:
                if old_values[field_name]!=new_values[field_name]:
                    AuditLog.objects.create(user=request.user,action=f'worker_{field_name}_changed',
                    object_type='User',object_id=worker.id,
                    old_value=str(old_values[field_name]),new_value=str(new_values[field_name])
                    )
            return redirect('workers_list')
    else:
        form=WorkerForm(instance=worker,current_user=request.user)
    return render(request,
                    'departments/worker_edit.html',
                    {'form': form}
                    )

@login_required
@permission_required('departments.add_user', raise_exception=True)
def worker_add(request):

    if request.method=="POST":
        form=WorkerCreateForm(request.POST,current_user=request.user)
        if form.is_valid():
            worker=form.save()
            AuditLog.objects.create(user=request.user,action='worker_created',
                    object_type='User',object_id=worker.id,
                    old_value="",new_value=worker.username
                    )
            return redirect('workers_list')
    else:
        form=WorkerCreateForm(current_user=request.user)
    return render(request,
                    'departments/worker_add.html',
                    {'form':form}
                    )
@login_required
def audit_log_list(request):
    audit_logs=get_visible_audit(request.user)
    audit_logs=audit_logs.order_by('-created_at')
    return render(request,
                    'departments/audit_logs.html',
                    {'audit_logs': audit_logs}
                    )

@login_required
def issues_list(request):
    visible_issues=get_visible_issues(request.user).order_by("-reported_at")
    return render(request,
                    'departments/issues_list.html',
                    {'visible_issues':visible_issues})

@login_required
def issue_detail(request, issue_id):
    visible_issues=get_visible_issues(request.user)
    issue=get_object_or_404(visible_issues,pk=issue_id)
    status_history=IssueStatusChange.objects.filter(issue=issue).order_by('-changed_at')
    interventions=Intervention.objects.filter(issue=issue).order_by('-started_at')
    return render(request,
                    'departments/issue_detail.html',
                    {'issue': issue,
                     'status_history': status_history,
                     'interventions': interventions}
                    
                    )
@login_required
def issue_add(request):
    if request.method=='POST':
        form=IssueForm(request.POST, current_user=request.user)
        if form.is_valid():
            issue=form.save(commit=False)
            issue.reported_by=request.user
            issue.save()

            AuditLog.objects.create(
                user=request.user,
                action='issue_created',
                object_type='Issue',
                object_id=issue.id,
                old_value='',
                new_value=issue.description
            )

            return redirect('issues_list')
    else:
        form=IssueForm(current_user=request.user)
    return render(request,
                    'departments/issue_add.html',
                    {'form':form}
        )

@login_required
@permission_required('departments.change_issue', raise_exception=True)
def issue_status_update(request, issue_id):

    visible_issues=get_visible_issues(request.user)
    issue=get_object_or_404(visible_issues,pk=issue_id)
    old_status=issue.issue_status
    if request.method=='POST':
        form=IssueStatusForm(request.POST, instance=issue)
        if form.is_valid():
            updated_issue=form.save(commit=False)
            updated_issue.full_clean()
            new_status=updated_issue.issue_status
            updated_issue.save()
            issue_status_change=IssueStatusChange.objects.create(
                issue=issue,
                old_status=old_status,
                new_status=new_status,
                changed_by=request.user
            )
            AuditLog.objects.create(
                user=request.user, action='issue_status_changed',
                object_type='Issue', object_id=issue.id,
                old_value=old_status, new_value=new_status
            )
            return redirect('issue_detail', issue.id)
    else:
        form=IssueStatusForm(instance=issue)
    return render(request,
                    'departments/issue_status_update.html',
                    {'form':form,
                    'issue': issue}

    )

@login_required
def intervention_add(request,issue_id):

    visible_issues=get_visible_issues(request.user)
    issue=get_object_or_404(visible_issues,pk=issue_id)
    if request.method=='POST':
        form=InterventionForm(request.POST)
        if form.is_valid():
            intervention=form.save(commit=False)
            intervention.issue=issue
            intervention.performed_by=request.user
            intervention.save()
            AuditLog.objects.create(user=request.user, action='intervention_created',
                                    object_type='Issue', object_id=issue.id,
                                    old_value="", new_value=intervention.description)
            return redirect('issue_detail', issue.id)
    else:
        form=InterventionForm()
    return render(request,
                'departments/intervention_add.html',
                {'form': form}
                )        

@login_required
@permission_required('departments.change_intervention', raise_exception=True)
def intervention_finish(request, intervention_id):
    intervention=get_object_or_404(Intervention, pk=intervention_id)
    visible_issues=get_visible_issues(request.user)
    issue=get_object_or_404(visible_issues, pk=intervention.issue.id)
    if intervention.finished_at:
        return redirect('issue_detail', issue.id)
    if request.method=="POST":
        intervention.finished_at=timezone.now()
        intervention.save()
        AuditLog.objects.create(user=request.user, action='intervention_finished',
                                object_type='Issue', object_id=intervention.issue.id,
                                old_value="", new_value=str(intervention.finished_at)
                                )
        return redirect('issue_detail', issue.id)
    else:
        return render(request,
                    'departments/intervention_finish_confirm.html',
                     {'intervention': intervention,
                        'issue': issue
                        }
                )
