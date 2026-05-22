from django.db import models
from django.contrib.auth.models import User

class Department(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Shift(models.Model):
    name = models.CharField(max_length=100)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.name} ({self.start_time} - {self.end_time})"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    shift = models.ForeignKey(Shift, on_delete=models.SET_NULL, null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    profile_pic = models.ImageField(upload_to='profile_pics/', default='profile_pics/default.png', blank=True)
    bio = models.TextField(max_length=500, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.department.name if self.department else 'No Dept'}"


class Device(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    device_id = models.CharField(max_length=255)
    user_agent = models.TextField(blank=True)
    device_type = models.CharField(max_length=100, blank=True)
    screen_resolution = models.CharField(max_length=50, blank=True)  # Add this
    timezone = models.CharField(max_length=100, blank=True)  # Add this
    language = models.CharField(max_length=10, blank=True)  # Add this
    hardware_info = models.TextField(blank=True)  # Add this
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'device_id']
    
    def __str__(self):
        return f"{self.user.username} - {self.device_id}"

class Attendance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    login_time = models.DateTimeField()
    logout_time = models.DateTimeField(null=True, blank=True)
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    is_late = models.BooleanField(default=False)
    selfie = models.ImageField(upload_to='attendance_selfies/', null=True, blank=True)
    
    def duration_hours(self):
        if self.logout_time:
            duration = self.logout_time - self.login_time
            return duration.total_seconds() / 3600
        return 0
    
    def attendance_status(self):
        if self.logout_time:
            return "Present"
        return "Pending"
    
    class Meta:
        ordering = ['-login_time']

class LeaveRequest(models.Model):
    LEAVE_TYPES = [
        ('Sick Leave', 'Sick Leave'),
        ('Casual Leave', 'Casual Leave'),
    ]
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPES)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.leave_type} ({self.status})"