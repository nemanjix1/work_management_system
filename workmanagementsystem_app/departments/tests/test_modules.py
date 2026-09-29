import pytest
from django.urls import reverse
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from departments.models import AttendanceEvent,WorkSession,Project,Product,User,Department,Team,ProductionEntry,Attendance

@pytest.mark.django_db
def test_create_department():
    department=Department.objects.create(
        name="Production",
        description="Production department",
        location="Hall A",
        code="PROD"
    )
    assert department.name=="Production"
    assert department.code=="PROD"
    assert department.location=="Hall A"
    
@pytest.mark.django_db
def test_department_str():
    department=Department.objects.create(
        name="Production",
        code="PROD"
    )
    assert str(department)=="Production"

@pytest.mark.django_db
def test_two_departments_with_the_same_name():
    department=Department.objects.create(
        name="Production"
    )
    with pytest.raises(IntegrityError):
        Department.objects.create(
            name="Production"
        ) 
@pytest.mark.django_db
def test_two_departments_with_the_same_code():
    department=Department.objects.create(
        code="PROD"
    )
    with pytest.raises(IntegrityError):
        Department.objects.create(
            code="PROD"
        ) 
@pytest.mark.django_db
def test_same_team_name_sllowed_in_different_department():
    production=Department.objects.create(
        name="Production",
        code="PROD"
    )
    foundry=Department.objects.create(
        name="Foundry",
        code="FOUND"
    )
    team1=Team.objects.create(
        name="A",
        department=production
    )
    team2=Team.objects.create(
        name="A",
        department=foundry
    )

    assert team1.name==team2.name
    assert team1.department != team2.department

@pytest.mark.django_db
def test_same_team_name_doesnot_allowed_in_the_same_department():
    production=Department.objects.create(
        name="Production",
        code="PROD"
    )
    Team.objects.create(
        name="A",
        department=production
    )

    with pytest.raises(IntegrityError):
        Team.objects.create(
            name="A",
            department=production
        )

@pytest.mark.django_db
def test_valid_username():
    user = User(username="123456")
    user.set_password("test-password")

    user.full_clean()  


@pytest.mark.django_db
@pytest.mark.parametrize("username", [
    "12345",    
    "1234567",  
    "12345a",   
    "123 56",   
    "",         
])
def test_invalid_username(username):
    user = User(username=username)
    user.set_password("test-password")

    with pytest.raises(ValidationError):
        user.full_clean()

def test_scrap_quantity_is_less_than_quantity(production_entry):
    production_entry.full_clean()


def test_scrap_quantity_cannot_exceed_quantity(production_entry):
    production_entry.scrap_quantity = 301

    with pytest.raises(
        ValidationError,
        match="Kolicina ne moze da bude manja od broja skartova",
    ):
        production_entry.full_clean()




@pytest.mark.django_db
def test_check_in_creates_attendance(client):
    user = User.objects.create_user(
        username="123456",
        password="test12345"
    )

    client.force_login(user)
    response=client.post(
        reverse("attendance"),
        data={"action": "check-in"},
        )   
    assert response.status_code == 200

    assert Attendance.objects.filter(
        user=user,
        check_out__isnull=True
    ).count() == 1

    
@pytest.mark.django_db
def test_check_in_cannot_create_two_active_attendances(client):
    user = User.objects.create_user(
        username="123456",
        password="test12345",
    )

    client.force_login(user)

    response = client.post(
        reverse("attendance"),
        data={"action": "check-in"},
    )

    assert response.status_code == 200

    client.force_login(user)

    response = client.post(
        reverse("attendance"),
        data={"action": "check-in"},
    )

    assert response.status_code == 200
    

    assert Attendance.objects.filter(
        user=user,
        check_out__isnull=True,
    ).count() == 1

@pytest.mark.django_db
def test_check_out_of_attendance(client):
    user = User.objects.create_user(
        username="123456",
        password="test12345"
    )
    attendance=Attendance.objects.create(
        user=user,
       
    )
    client.force_login(user)

    response=client.post(
        reverse("attendance"),
        data={"action":"check-out"}
    )
    
    assert response.status_code == 302

    attendance.refresh_from_db()
    assert attendance.check_out is not None

    assert Attendance.objects.filter(
        user=user,
        check_out__isnull=True
    ).count() == 0

@pytest.mark.django_db
def test_check_if_there_is_yet_out_of_attendance(client):
    user = User.objects.create_user(
        username="123456",
        password="test12345"
    )
    
    client.force_login(user)

    response=client.post(
        reverse("attendance"),
        data={"action":"check-out"}
    )
    
    assert response.status_code == 302

    assert Attendance.objects.filter(
        user=user,
        check_out__isnull=True
    ).count() == 0

@pytest.mark.django_db
def test_is_someone_a_user(client):
    response=client.get(
        reverse('attendance')
    )
   
    assert response.status_code==302

@pytest.mark.django_db
def test_private_in_cannot_be_first_event():
    user = User.objects.create_user(
        username="123456",
        password="test12345"
    )

    attendance = Attendance.objects.create(
        user=user
    )

    event = AttendanceEvent(
        attendance=attendance,
        events="private_in"
    )

    with pytest.raises(ValidationError):
        event.full_clean()

@pytest.mark.django_db
def test_private_out_then_private_in_is_allowed():
    user = User.objects.create_user(
        username="123456",
        password="test12345"
    )

    attendance = Attendance.objects.create(
        user=user
    )

    first_event = AttendanceEvent(
        attendance=attendance,
        events="private_out"
    )

    first_event.full_clean()
    first_event.save()

    second_event = AttendanceEvent(
        attendance=attendance,
        events="private_in"
    )

    second_event.full_clean()
