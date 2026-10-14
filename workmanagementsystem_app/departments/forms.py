from django import forms
from .models import Attachment, Project,User, Department, Issue,Intervention,Machine,Team,IssueStatusChange,Comment
from django.contrib.auth.forms import UserCreationForm
from .access import get_visible_issues, get_visible_departments,get_visible_teams,get_visible_machines,get_visible_projects

class ProjectForm(forms.ModelForm):

    class Meta:
        model=Project
        fields=[
            'name',
            'code',
            'status',
            'departments',
        ]

    def __init__(self,*args,current_user=None,**kwargs):
        super().__init__(*args,**kwargs)

        if current_user:
                self.fields['departments'].queryset=get_visible_departments(current_user)

class DepartmentForm(forms.ModelForm):

    class Meta:
        model=Department
        fields=[
            'name',
            'code',
            'location',
            'description',
        ]

class MachineForm(forms.ModelForm):

    class Meta:
        model=Machine
        fields=[
            'name',
            'code',
            'status',
            'department',
        ]
    def __init__(self,*args,current_user=None,**kwargs):
        super().__init__(*args,**kwargs)

        if current_user:
            self.fields['department'].queryset=get_visible_departments(current_user)

class TeamForm(forms.ModelForm):

    class Meta:
        model=Team
        fields=[
            'name',
            'department',
            'team_leader',
            ]
    def __init__(self,*args,current_user=None,**kwargs):
        super().__init__(*args,**kwargs)

        if current_user:
            self.fields['department'].queryset=get_visible_departments(current_user)
            if current_user.role=='administrator':
                self.fields['team_leader'].queryset=User.objects.filter(role='team_leader')
            elif current_user.role=='manager':
                 self.fields['team_leader'].queryset=User.objects.filter(role='team_leader',department=current_user.department)
            else:
                self.fields['team_leader'].queryset=User.objects.none()

class WorkerForm(forms.ModelForm):

    class Meta:
        model=User
        fields=[
            'department',
            'team',
            'role',
            'phone_number'
        ]
    def __init__(self,*args,current_user=None,**kwargs):
        
        super().__init__(*args,**kwargs)

        if current_user:
            self.fields['department'].queryset=get_visible_departments(current_user)
            self.fields['team'].queryset=get_visible_teams(current_user)
            if current_user.role=='administrator':
                self.fields['role'].choices=[('administrator', 'Administrator'),('manager','Manager'),('team_leader','Team_leader'),('operater','Operater')]
            if current_user.role=='manager':
               self.fields['role'].choices=[('team_leader','Team_leader'),('operater','Operater')]
            if current_user.role=='team_leader':
                self.fields['role'].choices=[('operater','Operater')]

class WorkerCreateForm(UserCreationForm):


    class Meta:
        model=User
        fields=[
            'username',
            'first_name',
            'last_name',
            'role',
            'department',
            'team',
            'phone_number',
        ]
    def __init__(self, *args,current_user=None,**kwargs):

        super().__init__(*args,**kwargs)

        if current_user:
            self.fields['department'].queryset=get_visible_departments(current_user)
            self.fields['team'].queryset=get_visible_teams(current_user)
            if current_user.role=='administrator':
                self.fields['role'].choices=[('administrator', 'Administrator'),('manager','Manager'),('team_leader','Team_leader'),('operater','Operater')]
            if current_user.role=='manager':
               self.fields['role'].choices=[('team_leader','Team_leader'),('operater','Operater')]
            if current_user.role=='team_leader':
                self.fields['role'].choices=[('operater','Operater')]

class IssueForm(forms.ModelForm):
    class Meta:

        model=Issue
        fields=[
            'machine',
            'priority',
            'description'
        ]
    def __init__(self,*args,current_user=None,**kwargs):
        super().__init__(*args,**kwargs)

        if current_user:
            self.fields['machine'].queryset=get_visible_machines(current_user)

class IssueStatusForm(forms.ModelForm):
    class Meta:
        model=Issue
        fields=[
            'issue_status'
        ]

class InterventionForm(forms.ModelForm):

    class Meta:
        model=Intervention
        fields=[
            'description',
            'finished_at'
        ]

class CommentForm(forms.ModelForm):

    class Meta:
        model=Comment
        fields=[
            'text'
        ]

class AttachmentForm(forms.ModelForm):
    class Meta:
        model=Attachment
        fields=[
            'file'
        ]