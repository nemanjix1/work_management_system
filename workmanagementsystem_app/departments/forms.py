from django import forms
from .models import Project, Department

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
