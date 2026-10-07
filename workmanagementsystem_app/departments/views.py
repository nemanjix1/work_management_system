from django.shortcuts import render,redirect,get_object_or_404
from .models import Attendance,AttendanceEvent,Project,Department
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import ProjectForm,DepartmentForm
from django.contrib.auth.decorators import permission_required
from django.core.paginator import Paginator
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
    projects=Project.objects.filter(is_archived=False)
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
        form=ProjectForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('projects_list')
    else:
        form=ProjectForm()
    return render(request, 
    'departments/projects_add.html', 
    {'form': form})

@login_required
@permission_required('departments.view_project', raise_exception=True)
def project_details(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    return render(request,
                    'departments/project_details.html',
                    {'project': project}
                    )

@login_required
@permission_required('departments.change_project', raise_exception=True)
def project_edit(request, project_id):
    project=get_object_or_404(Project, pk=project_id)
    if request.method=="POST":
         form=ProjectForm(request.POST,instance=project)
         if form.is_valid():
            form.save()
            return redirect('projects_list')
    else:
        form=ProjectForm(instance=project)
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
    project=get_object_or_404(Project, pk=project_id)
    if request.method=="POST":
        project.is_archived=True
        project.archived_at=timezone.now()
        project.save()
    return redirect('projects_list')

@login_required
@permission_required('departments.view_project', raise_exception=True)
def archived_project(request):
    projects=Project.objects.filter(is_archived=True)
    return render(
        request,
        'departments/project_archived.html',
        {'projects': projects}
    )

@login_required
def departments_list(request):
    departments=Department.objects.all()
    return render(request,
                'departments/departments_list.html',
                {'departments': departments}

    )
@login_required
def department_detail(request, department_id):
    department=get_object_or_404(Department, pk=department_id)
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
            form.save()
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
    department=get_object_or_404(Department, pk=department_id)
    if request.method=="POST":
        form=DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            return redirect('departments_list')
    else:
        form=DepartmentForm(instance=department)
    return render(request,
                'departments/department_edit.html',
                {'form': form}

    )
