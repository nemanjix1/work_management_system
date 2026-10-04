from django.shortcuts import render,redirect
from .models import Attendance,AttendanceEvent
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.forms import AuthenticationForm
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

def home_page(request):
    return render(request, 'departments/home.html')