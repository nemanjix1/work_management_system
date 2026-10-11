from .models import User, Department,Team, Machine,Issue, Project, AuditLog
from django.db.models import Q

def get_visible_workers(user):
    if user.role=='administrator':
        return User.objects.all()
    elif user.role=='manager':
        if user.department is None:
            return User.objects.none()
        return User.objects.filter(department=user.department)
    elif user.role=='team_leader':
        if user.team is None:
             return User.objects.none()
        return User.objects.filter(team=user.team)
    elif user.role=='operater':
        return User.objects.filter(pk=user.pk)
    else:
        return User.objects.none()

def get_visible_departments(user):
    if user.role=='administrator':
        return Department.objects.all()
    elif user.role in ['manager', 'team_leader','operater']:
        if user.department is None:
            return Department.objects.none()
        return Department.objects.filter(pk=user.department.pk)
    else:
        return Department.objects.none()

def get_visible_teams(user):
    if user.role=='administrator':
        return Team.objects.all()
    elif user.role=='manager':
        if user.department is None:
            return Team.objects.none()
        return Team.objects.filter(department=user.department)
    elif user.role in ['team_leader','operater']:
        if user.team is None:
            return Team.objects.none()
        return Team.objects.filter(pk=user.team.pk)
    else:
        return Team.objects.none()
    
def get_visible_machines(user):

    if user.role=='administrator':
        return Machine.objects.all()
    elif user.role in ['manager','team_leader','operater']:
        if user.department is None:
            return Machine.objects.none()
        return Machine.objects.filter(department=user.department)
    else:
        return Machine.objects.none()

def get_visible_projects(user):

    if user.role=='administrator':
        return Project.objects.all()
    elif user.role in ['manager','team_leader','operater']:
        if user.department is None:
            return Project.objects.none()
        return Project.objects.filter(departments=user.department)
    else:
        return Project.objects.none()

def get_visible_audit(user):

    if user.role=='administrator':
        return AuditLog.objects.all()
    elif user.role=='manager':
        if user.department is None:
            return AuditLog.objects.none()
        machine_ids = Machine.objects.filter(
         department=user.department
        ).values_list('id', flat=True)

        team_ids = Team.objects.filter(
            department=user.department
        ).values_list('id', flat=True)

        user_ids = User.objects.filter(
            department=user.department
        ).values_list('id', flat=True)

        project_ids = Project.objects.filter(
            departments=user.department
        ).values_list('id', flat=True)

        issue_ids=Issue.objects.filter(
            machine__department=user.department
        ).values_list('id', flat=True)

        return AuditLog.objects.filter(
            Q(object_type='Machine', object_id__in=machine_ids) |
            Q(object_type='Team', object_id__in=team_ids) |
            Q(object_type='User', object_id__in=user_ids) |
            Q(object_type='Project', object_id__in=project_ids) |
            Q(object_type='Department', object_id=user.department.id)|
            Q(object_type='Issue', object_id__in=issue_ids)
        )
    elif user.role=='team_leader':
        if user.team is None:
            return AuditLog.objects.none()
        team=user.team
        user_ids=User.objects.filter(team=team).values_list('id', flat=True)
        issue_ids=Issue.objects.filter(reported_by__team=user.team).values_list('id', flat=True)
        return AuditLog.objects.filter(
            Q(object_type='Team',object_id=team.id)|
            Q(object_type='User', object_id__in=user_ids)|
            Q(object_type='Issue', object_id__in=issue_ids)

        )
    elif user.role=='operater':
        return AuditLog.objects.filter(user=user)
    else:
        return AuditLog.objects.none()

def get_visible_issues(user):
    if user.role=='administrator':
        return Issue.objects.all()
    elif user.role=='manager':
        if user.department is None:
            return Issue.objects.none()
        return Issue.objects.filter(machine__department=user.department)
    elif user.role=='team_leader':
        if user.team is None:
            return Issue.objects.none()
        return Issue.objects.filter(reported_by__team=user.team)
    elif user.role=='operater':
        return Issue.objects.filter(reported_by=user)
    else:
        return Issue.objects.none()
