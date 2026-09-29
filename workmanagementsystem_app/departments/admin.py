from django.contrib import admin
from .models import (
    Department,
    User,
    Team,
    Project,
    Machine,
    Issue,
    Intervention,
    Comment,
    IssueStatusChange,
    Attendance,
    Product,
    WorkSession,
    ProductionEntry
)

# Register your models here.

admin.site.register(Department)
admin.site.register(User)
admin.site.register(Team)
admin.site.register(Project)
admin.site.register(Machine)
admin.site.register(Issue)
admin.site.register(Intervention)
admin.site.register(Comment)
admin.site.register(IssueStatusChange)
admin.site.register(Attendance)
admin.site.register(Product)
admin.site.register(WorkSession)
admin.site.register(ProductionEntry)