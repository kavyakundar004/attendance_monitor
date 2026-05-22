from django.core.management.base import BaseCommand
from attendance_app.models import Attendance
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Delete attendance records older than 1 year'

    def handle(self, *args, **options):
        one_year_ago = timezone.now() - timedelta(days=365)
        old_records = Attendance.objects.filter(login_time__lt=one_year_ago)
        count = old_records.count()
        old_records.delete()
        
        self.stdout.write(self.style.SUCCESS(f'Successfully deleted {count} old attendance records.'))
