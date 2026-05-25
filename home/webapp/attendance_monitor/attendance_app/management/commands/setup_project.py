from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from attendance_app.models import Department, Shift

class Command(BaseCommand):
    help = 'Initialize the project with default admin, departments, and shifts'

    def handle(self, *args, **options):
        # 1. Create Admin if not exists
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            self.stdout.write(self.style.SUCCESS('Admin created: admin/admin123'))
        else:
            self.stdout.write('Admin already exists.')

        # 2. Create Departments
        departments = ['Sales', 'Web', 'BI', 'HR', 'Marketing']
        for dept_name in departments:
            Department.objects.get_or_create(name=dept_name)
        self.stdout.write(self.style.SUCCESS(f'Departments ensured: {", ".join(departments)}'))

        # 3. Create Shifts
        Shift.objects.get_or_create(
            name='Morning Shift', 
            defaults={'start_time': '09:00:00', 'end_time': '18:00:00'}
        )
        Shift.objects.get_or_create(
            name='Night Shift', 
            defaults={'start_time': '21:00:00', 'end_time': '06:00:00'}
        )
        self.stdout.write(self.style.SUCCESS('Default shifts ensured.'))
