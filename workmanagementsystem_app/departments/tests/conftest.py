import pytest

from departments.models import (
    Department,
    User,
    Project,
    Machine,
    WorkSession,
    Product,
    ProductionEntry,
)


@pytest.fixture
def production_entry(db):
    department = Department.objects.create(
        name="Production",
        code="PROD",
    )

    user = User.objects.create_user(
        username="123456",
        password="test-password",
        department=department,
    )

    project = Project.objects.create(
        name="Test project",
        code="PRJ1",
    )
    project.departments.add(department)

    machine = Machine.objects.create(
        name="Machine 1",
        code="M1",
        department=department,
    )

    work_session = WorkSession.objects.create(
        user=user,
        project=project,
        machine=machine,
    )

    product = Product.objects.create(
        name="Product 1",
        code="P1",
        project=project,
    )

    return ProductionEntry.objects.create(
        work_session=work_session,
        product=product,
        quantity=300,
        scrap_quantity=12,
    )