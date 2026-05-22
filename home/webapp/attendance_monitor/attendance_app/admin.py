from django.contrib import admin
from .models import Department, UserProfile, Device, Attendance
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# Inline for UserProfile so it appears on the User admin page
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'

# Extend User admin to include department
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)

# Department admin
@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

# Device admin
@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('user', 'device_id', 'device_type', 'user_agent')
    search_fields = ('user__username', 'device_id', 'device_type')

# Attendance admin
@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('user', 'login_time', 'logout_time', 'device', 'duration_hours', 'attendance_status')
    list_filter = ('login_time', 'logout_time', 'user')
    search_fields = ('user__username',)
    readonly_fields = ('duration_hours', 'attendance_status')

# Unregister default User admin and register customized one
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
