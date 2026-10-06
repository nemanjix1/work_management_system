from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

# Create your models here.
employee_number_validator = RegexValidator(
    regex=r'^\d{6}$',
    message='Korisnički broj mora imati tačno 6 cifara.'
)
class Department(models.Model):
    name=models.CharField(
        max_length=100,
        unique=True
    )
    description=models.TextField(
        blank=True
    )
    location=models.CharField(
        max_length=150,
        blank=True
    )
    code=models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True
    )
    def __str__(self):
        return self.name

class User(AbstractUser):

    username = models.CharField(
        max_length=6,
        unique=True,
        validators=[employee_number_validator]
    )
    ROLE_CHOICES=[
        ('operater', 'Operater'),
        ('team_leader', 'Team-Leader'),
        ('manager','Manager'),
        ('administrator','administrator'),
    ]
    role=models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='operater'
    )

    phone_number=models.CharField(
        max_length=25,
        blank=True
    )


    department=models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name='users',
        null=True,
        blank=True
    )
    
    team=models.ForeignKey(
        'Team',
        on_delete=models.PROTECT,
        related_name='users',
        null=True,
        blank=True
    )
   
    def __str__(self):
        return self.username
    def clean(self):
        super().clean()

        if self.team and self.department != self.team.department:
            raise ValidationError(
                "Tim ne pripada izabranom departmanu."
            )

class Team(models.Model):
    name=models.CharField(
        max_length=10
       
    )
    department=models.ForeignKey(
        Department,
        on_delete=models.PROTECT
    )
    team_leader=models.OneToOneField(
        User, 
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='led_team'
    )
    def __str__(self):
        return self.name
        
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['department', 'name'],
                name='unique_team_name_per_department'
            )
        ]

class Project(models.Model):
    STATUS_CHOICES=[
        ('planned', 'Planned'),
        ('active', 'Active'),
        ('completed','Completed'),
        ('postponed', 'Postponed'),
        ('cancelled', 'Cancelled'),
    ]
    name=models.CharField(
        max_length=50,
        unique=True
    )
    status=models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='planned'

        
    )
    code=models.CharField(
        max_length=10,
        unique=True
    )
    departments=models.ManyToManyField(
        Department
       
    )
    is_archived=models.BooleanField(
        default=False
    )

    archived_at=models.DateTimeField(
        null=True,
        blank=True
    )
    

    def __str__(self):
        return self.name
    
class Machine(models.Model):
    STATUS_CHOICES=[
        ('active', 'Active'),
        ('broken', 'Broken'),
        ('maintenance', 'Maintenance'),
        ('inactive', 'Inactive'),
    ]
    name=models.CharField(
        max_length=50
    )
    code=models.CharField(
        max_length=10,
        unique=True
    )
    department=models.ForeignKey(
        Department,
        on_delete=models.PROTECT

    )
    status=models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )

    def __str__(self):
        return f'{self.name} {self.code}'

class Issue(models.Model):

    PRIORITY_CHOICES = (
    ('low', 'Low'),
    ('medium', 'Medium'),
    ('high', 'High'),
    )

    ISSUESTATUS_CHOICES=[
        ('open', 'Open'),
        ('in_progress', 'In_progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]

    machine=models.ForeignKey(
        Machine,
        on_delete=models.PROTECT
    )

    reported_by=models.ForeignKey(
        User,
        on_delete=models.PROTECT
    )

    reported_at=models.DateTimeField(auto_now_add=True)

    description=models.TextField(

    )

    issue_status=models.CharField(
        max_length=20,
        choices=ISSUESTATUS_CHOICES,
        default='open'
    )

    priority = models.CharField(
    max_length=10,
    choices=PRIORITY_CHOICES,
    default='medium'
)

    def __str__(self):
        return f'{self.machine} : {self.reported_at}'
    def clean(self):
        super().clean()
        if self.pk:
            old_issue=Issue.objects.get(pk=self.pk)
            old_status=old_issue.issue_status
            current_status=self.issue_status
            if old_status==current_status:
                return
            if not (
                    (old_status=='open' and current_status=='in_progress')
                    or
                    (old_status=='in_progress'and current_status=='resolved') 
                    or
                    (old_status=='resolved' and current_status=='closed')
                    ):
                        raise ValidationError("nedozvoljeni prelazi izmedju statusa kvara")

class Intervention(models.Model):

    issue=models.ForeignKey(
        Issue,
        on_delete=models.PROTECT
    )

    performed_by=models.ForeignKey(
        User,
        on_delete=models.PROTECT
    )

    started_at=models.DateTimeField(auto_now_add=True)

    finished_at=models.DateTimeField(
        null=True,
        blank=True
    )

    description=models.TextField()

    def __str__(self):
        return f'{self.issue} : {self.performed_by} : {self.started_at}'

class Comment(models.Model):
    issue=models.ForeignKey(
        Issue,
        on_delete=models.PROTECT
    )        

    author=models.ForeignKey(
        User,
        on_delete=models.PROTECT
    )

    text=models.TextField()

    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.author} : {self.created_at}'

class IssueStatusChange(models.Model):
    issue=models.ForeignKey(
        Issue,
        on_delete=models.PROTECT
    )

    old_status=models.CharField(
        max_length=20,
        choices=Issue.ISSUESTATUS_CHOICES
    )

    new_status=models.CharField(
        max_length=20,
        choices=Issue.ISSUESTATUS_CHOICES
       
    )

    changed_by=models.ForeignKey(
        User,
        on_delete=models.PROTECT
    )

    changed_at=models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f'{self.issue} : {self.new_status}'

class Attendance(models.Model):
    user=models.ForeignKey(
        User,
        on_delete=models.PROTECT
    )
    check_in=models.DateTimeField(auto_now_add=True)
    check_out=models.DateTimeField(
        null=True,
        blank=True
    )

    def __str__(self):
        return f'{self.user.username} : {self.check_in}'
    def clean(self):
        super().clean()
        if self.check_out and self.check_in>self.check_out:
            raise ValidationError(
                "Vrijeme odlaska ne moze biti prije vremena dolaska"
            )
        if self.user_id and not self.check_out:
            active_attendance=Attendance.objects.filter(
                user=self.user,
                check_out__isnull=True
            ).exclude(pk=self.pk).exists()
            if active_attendance:
                raise ValidationError(
                    " Korisnik vec ima aktivnu evidenciju dolaska"
                )

class Product(models.Model):
    name=models.CharField(
        max_length=50
    )
    code=models.CharField(
        max_length=20,
        unique=True
    )
    project=models.ForeignKey(
        Project,
        on_delete=models.PROTECT
    )

    def __str__(self):
        return f'{self.name} : {self.code}'

class WorkSession(models.Model):
    user=models.ForeignKey(
        User,
        on_delete=models.PROTECT
    )
    project=models.ForeignKey(
        Project,
        on_delete=models.PROTECT
    )
    machine=models.ForeignKey(
        Machine,
        on_delete=models.PROTECT
    )
    started_at=models.DateTimeField(auto_now_add=True)
    finished_at=models.DateTimeField(
        null=True,
        blank=True
    )

    def __str__(self):
        return f'{self.user.username} : {self.machine.name}'
    
    def clean(self):
        super().clean()
        if not self.project.departments.filter(
            pk=self.machine.department_id
            ).exists():
            raise ValidationError(
                "Mašina ne pripada nijednom departmentu ovog projekta."
            )
        if self.finished_at and self.started_at>self.finished_at:
            raise ValidationError(
                " Vreme zavrsetka projekta ne moze biti prije vremena pocetka rada"
            )
        if self.user_id and not self.finished_at:
            active_session=WorkSession.objects.filter(
                user=self.user,
                finished_at__isnull=True
                ).exclude(pk=self.pk).exists()
            if active_session:
                raise ValidationError(
                    "Korisnik vec ima aktivnu radnu sesiju"
                )

class ProductionEntry(models.Model):
    work_session=models.ForeignKey(
        WorkSession,
        on_delete=models.PROTECT
    )
    product=models.ForeignKey(
        Product,
        on_delete=models.PROTECT
    )
    quantity=models.PositiveIntegerField()
    scrap_quantity=models.PositiveIntegerField(default=0)
    recorded_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.product.name} : {self.quantity}'

    def clean(self):
        if self.quantity<self.scrap_quantity:
            raise ValidationError(
                "Kolicina ne moze da bude manja od broja skartova"
            )
        if self.product.project != self.work_session.project:
            raise ValidationError(
                "Izabrani proizvod ne pripada projektu ove radne sesije"
            )


class AttendanceEvent(models.Model):
    attendance=models.ForeignKey(
        Attendance,
        on_delete=models.PROTECT
    )
    CHOICES_EVENTS=(
        ('private_out', 'Private out'),
        ('private_in', 'Private in'),
        ('business_out', 'Business out'),
        ('business_in', 'Business in')
    )
    events=models.CharField(
        max_length=20,
        choices=CHOICES_EVENTS
    )
    event_time=models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f'{self.attendance.user.username}-{self.events}-{self.event_time}'

    def clean(self):
        super().clean()
        attendance_event=AttendanceEvent.objects.filter(
            attendance=self.attendance
        )
        last_event=attendance_event.order_by('-event_time').first()
        if last_event is not None:
            if last_event.events=='private_out' and ((self.events=='business_in') or (self.events=='business_out')or(self.events=='private_out')):
                raise ValidationError("nedozvoljena akcija")
            if last_event.events=='business_out' and ((self.events=='private_out' or self.events=='private_in')or(self.events=='business_out')):
                raise ValidationError("nedozvoljena akcija")
            if (last_event.events=='private_in' or last_event.events=='business_in')and(self.events!='private_out' and self.events!='business_out'):
                raise ValidationError("nedozvoljena akcija")
        else:
            if self.events!='private_out'and self.events!='business_out':
                raise ValidationError("nedozvoljena akcija")