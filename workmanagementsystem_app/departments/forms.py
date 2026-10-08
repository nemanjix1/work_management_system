from django import forms
from .models import Project,User, Department, Machine,Team

class ProjectForm(forms.ModelForm):

    class Meta:
        model=Project
        fields=[
            'name',
            'code',
            'status',
            'departments',
        ]

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

class TeamForm(forms.ModelForm):

    class Meta:
        model=Team
        fields=[
            'name',
            'department',
            'team_leader',
            ]
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

        self.fields['team_leader'].queryset=User.objects.filter(role='team_leader')
