from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import JsonResponse
from .models import *
from .forms import *
import json
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone
from datetime import date
from django.contrib.admin.views.decorators import staff_member_required
from datetime import date, timedelta
from django.contrib.auth.models import User
from django.db import models
from .models import Attendance, LeaveRequest, UserProfile, Department, Shift
from calendar import monthrange
from django.contrib import messages
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import render, redirect

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            
            # Check if it's the employee's first login (password same as username)
            # and they are not a superuser/staff
            if not user.is_superuser and not user.is_staff and password == username:
                return redirect('set_password')

            # Check if user is admin
            if user.is_superuser or user.is_staff:
                return redirect('admin_dashboard')
            else:
                return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'login.html')

@login_required
def set_password_view(request):
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if new_password == confirm_password:
            request.user.set_password(new_password)
            request.user.save()
            # Re-authenticate and login to keep the session active after password change
            login(request, request.user)
            messages.success(request, 'Password set successfully!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Passwords do not match.')
            
    return render(request, 'set_password.html')


from django.contrib.auth.decorators import login_required

@login_required
def logout_view(request):
    logout(request)
    return render(request, 'logged_out.html')

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            department = form.cleaned_data.get('department')
            # Create profile
            UserProfile.objects.create(user=user, department=department)
            login(request, user)
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})


@login_required
def dashboard(request):
    records = Attendance.objects.filter(user=request.user).order_by('-login_time')[:7]
    
    today = date.today()
    today_attendance = Attendance.objects.filter(user=request.user, login_time__date=today).first()
    
    # Leave logic
    if request.method == 'POST' and 'apply_leave' in request.POST:
        leave_form = LeaveRequestForm(request.POST)
        if leave_form.is_valid():
            leave = leave_form.save(commit=False)
            leave.user = request.user
            leave.save()
            messages.success(request, 'Leave request submitted successfully.')
            return redirect('dashboard')
    else:
        leave_form = LeaveRequestForm()

    # Profile logic
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST' and 'update_profile' in request.POST:
        profile_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('dashboard')
    else:
        profile_form = UserProfileForm(instance=user_profile)

    user_leaves = LeaveRequest.objects.filter(user=request.user).order_by('-created_at')
    
    return render(request, 'dashboard.html', {
        'records': records,
        'today_attendance': today_attendance,
        'leave_form': leave_form,
        'profile_form': profile_form,
        'user_profile': user_profile,
        'user_leaves': user_leaves
    })

@staff_member_required
def approve_leave(request, leave_id):
    leave = LeaveRequest.objects.get(id=leave_id)
    leave.status = 'Approved'
    leave.save()
    messages.success(request, f'Leave for {leave.user.username} approved.')
    return redirect('admin_dashboard')

@staff_member_required
def reject_leave(request, leave_id):
    leave = LeaveRequest.objects.get(id=leave_id)
    leave.status = 'Rejected'
    leave.save()
    messages.warning(request, f'Leave for {leave.user.username} rejected.')
    return redirect('admin_dashboard')

@staff_member_required
def employee_details(request, user_id):
    employee = User.objects.get(id=user_id)
    
    # Calculate stats for charts
    present_days = Attendance.objects.filter(user=employee, logout_time__isnull=False).count()
    pending_days = Attendance.objects.filter(user=employee, logout_time__isnull=True).count()
    
    sick_leaves = LeaveRequest.objects.filter(user=employee, leave_type='Sick Leave', status='Approved').count()
    casual_leaves = LeaveRequest.objects.filter(user=employee, leave_type='Casual Leave', status='Approved').count()
    
    # For simplicity, we'll assume a standard 30-day view for "Absents" in this context
    # Or better, just show the actual counts of different statuses
    
    context = {
        'employee': employee,
        'present_days': present_days,
        'pending_days': pending_days,
        'sick_leaves': sick_leaves,
        'casual_leaves': casual_leaves,
        'all_attendance': Attendance.objects.filter(user=employee).order_by('-login_time'),
        'all_leaves': LeaveRequest.objects.filter(user=employee).order_by('-created_at')
    }
    return render(request, 'employee_details.html', context)

@staff_member_required
def delete_employee(request, user_id):
    employee = User.objects.get(id=user_id)
    employee.delete()
    messages.success(request, f'Employee {employee.username} deleted successfully.')
    return redirect('admin_dashboard')

@staff_member_required
def edit_employee(request, user_id):
    employee = User.objects.get(id=user_id)
    profile, created = UserProfile.objects.get_or_create(user=employee)
    
    if request.method == 'POST':
        employee.username = request.POST.get('username')
        employee.email = request.POST.get('email')
        employee.save()
        
        profile.department_id = request.POST.get('department')
        profile.shift_id = request.POST.get('shift')
        profile.phone_number = request.POST.get('phone_number')
        profile.save()
        
        messages.success(request, f'Details for {employee.username} updated.')
        return redirect('employee_details', user_id=user_id)
    
    context = {
        'employee': employee,
        'profile': profile,
        'departments': Department.objects.all(),
        'shifts': Shift.objects.all(),
    }
    return render(request, 'edit_employee.html', context)

@staff_member_required
def add_employee(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        dept_id = request.POST.get('department')
        shift_id = request.POST.get('shift')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        else:
            # Create user with username as initial password
            user = User.objects.create_user(username=username, password=username)
            UserProfile.objects.create(
                user=user, 
                department_id=dept_id,
                shift_id=shift_id
            )
            messages.success(request, f'New employee {user.username} added successfully. Initial password is the username.')
            return redirect('admin_dashboard')
            
    context = {
        'departments': Department.objects.all(),
        'shifts': Shift.objects.all(),
    }
    return render(request, 'add_employee.html', context)


# attendance_app/views.py
import json
from django.utils import timezone
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import Attendance, Device

from django.core.files.base import ContentFile
import base64
import cv2
import numpy as np
import os

def compare_faces(profile_pic_path, selfie_base64):
    try:
        # 1. Load Profile Image
        profile_img = cv2.imread(profile_pic_path)
        if profile_img is None:
            return False, "Could not load profile image."
        
        profile_gray = cv2.cvtColor(profile_img, cv2.COLOR_BGR2GRAY)
        
        # 2. Load Selfie Image from Base64
        format, imgstr = selfie_base64.split(';base64,')
        nparr = np.frombuffer(base64.b64decode(imgstr), np.uint8)
        selfie_img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if selfie_img is None:
            return False, "Could not decode captured selfie."
        
        selfie_gray = cv2.cvtColor(selfie_img, cv2.COLOR_BGR2GRAY)

        # 3. Use LBPH Face Recognizer with stricter parameters
        # radius=1, neighbors=8, grid_x=8, grid_y=8 are standard
        recognizer = cv2.face.LBPHFaceRecognizer_create(radius=1, neighbors=8, grid_x=8, grid_y=8)
        
        # Detect faces
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        face_cascade = cv2.CascadeClassifier(cascade_path)
        
        p_faces = face_cascade.detectMultiScale(profile_gray, 1.1, 5)
        s_faces = face_cascade.detectMultiScale(selfie_gray, 1.1, 5)
        
        if len(p_faces) == 0 or len(s_faces) == 0:
            return False, "Face not clearly visible in profile or selfie."

        # Extract and resize faces to a fixed size for better matching
        (x, y, w, h) = sorted(p_faces, key=lambda f: f[2]*f[3], reverse=True)[0]
        p_face = cv2.resize(profile_gray[y:y+h, x:x+w], (200, 200))
        
        (sx, sy, sw, sh) = sorted(s_faces, key=lambda f: f[2]*f[3], reverse=True)[0]
        s_face = cv2.resize(selfie_gray[sy:sy+sh, sx:sx+sw], (200, 200))

        # Train on profile
        recognizer.train([p_face], np.array([1]))
        
        # Predict
        label, confidence = recognizer.predict(s_face)
        
        # Lower confidence means better match. 
        # For 200x200 resized images, 50-65 is a very strict match.
        # 75 was too loose. Let's try 55 for high security.
        if confidence < 55:
            return True, "Face matched successfully."
        else:
            return False, "Face does not match your profile picture. Please look directly at the camera."

    except Exception as e:
        return False, f"Verification error: {str(e)}"

@login_required
@require_POST
@csrf_exempt
def mark_present(request):
    try:
        today = timezone.now().date()
        # Check if user already marked present today
        existing_attendance = Attendance.objects.filter(
            user=request.user, 
            login_time__date=today
        ).first()
        
        if existing_attendance:
            return JsonResponse({
                'status': 'fail', 
                'message': 'You have already marked present today.'
            })

        data = json.loads(request.body.decode('utf-8'))
        
        # Get User Profile for Face Comparison
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            if not user_profile.profile_pic:
                 return JsonResponse({
                    'status': 'fail', 
                    'message': 'No profile picture found. Please upload one in settings first.'
                })
            
            # Perform Face Recognition
            if 'selfie' in data and data['selfie']:
                is_match, message = compare_faces(user_profile.profile_pic.path, data['selfie'])
                if not is_match:
                    return JsonResponse({
                        'status': 'fail', 
                        'message': message
                    })
            else:
                return JsonResponse({
                    'status': 'fail', 
                    'message': 'Selfie verification is required.'
                })
        except UserProfile.DoesNotExist:
            return JsonResponse({
                'status': 'fail', 
                'message': 'User profile not found.'
            })

        # Create or update device with all fields
        device, created = Device.objects.get_or_create(
            user=request.user,
            device_id=data['device_id'],
            defaults={
                'user_agent': data.get('user_agent', ''),
                'device_type': data.get('device_type', ''),
                'screen_resolution': data.get('screen_resolution', ''),
                'timezone': data.get('timezone', ''),
                'language': data.get('language', ''),
                'hardware_info': data.get('hardware_info', '')
            }
        )
        
        # Update device info if it already exists
        if not created:
            device.user_agent = data.get('user_agent', device.user_agent)
            device.device_type = data.get('device_type', device.device_type)
            device.screen_resolution = data.get('screen_resolution', device.screen_resolution)
            device.timezone = data.get('timezone', device.timezone)
            device.language = data.get('language', device.language)
            device.hardware_info = data.get('hardware_info', device.hardware_info)
            device.save()
        
        # Check if late
        is_late = False
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            if user_profile.shift:
                current_time = timezone.now().time()
                if current_time > user_profile.shift.start_time:
                    is_late = True
        except UserProfile.DoesNotExist:
            pass

        # Create attendance record
        attendance = Attendance.objects.create(
            user=request.user, 
            login_time=timezone.now(), 
            device=device,
            is_late=is_late
        )

        # Handle Selfie if provided
        if 'selfie' in data and data['selfie']:
            format, imgstr = data['selfie'].split(';base64,')
            ext = format.split('/')[-1]
            attendance.selfie.save(
                f"selfie_{request.user.username}_{attendance.id}.{ext}",
                ContentFile(base64.b64decode(imgstr)),
                save=True
            )
        
        # Real-time update via WebSocket
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'attendance_updates',
            {
                'type': 'attendance_message',
                'message': {
                    'username': request.user.username,
                    'time': attendance.login_time.strftime('%H:%M:%S'),
                    'status': 'Present',
                    'is_late': is_late
                }
            }
        )
        
        # Store device ID in session for logout verification
        request.session['login_device_id'] = data['device_id']
        
        return JsonResponse({
            'status': 'ok',
            'attendance_id': attendance.id,
            'device_created': created
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'fail',
            'message': str(e)
        }, status=400)

@login_required
@require_POST
@csrf_exempt
def mark_logout(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        device_id = data.get('device_id')
        
        if not device_id:
            return JsonResponse({'status': 'fail', 'message': 'Device ID required'}, status=400)
        
        # Get the latest pending attendance record
        att = Attendance.objects.filter(
            user=request.user, 
            logout_time__isnull=True
        ).last()
        
        if not att:
            return JsonResponse({'status': 'fail', 'message': 'No active session found'}, status=400)
        
        # Check if logout is from the same device as login
        if att.device.device_id != device_id:
            return JsonResponse({
                'status': 'fail', 
                'message': 'Logout must be done from the same device used for login'
            }, status=400)
        
        # Proceed with logout
        att.logout_time = timezone.now()
        att.save()
        
        return JsonResponse({'status': 'ok', 'hours': att.duration_hours()})
        
    except Exception as e:
        return JsonResponse({'status': 'fail', 'message': str(e)}, status=400)


@staff_member_required
def admin_dashboard(request):
    # Get filters from GET
    year = int(request.GET.get('year', date.today().year))
    month = int(request.GET.get('month', date.today().month))
    department_id = request.GET.get('department', None)

    num_days = monthrange(year, month)[1]
    start_date = date(year, month, 1)
    end_date = date(year, month, num_days)

    # Filter departments
    if department_id:
        departments = Department.objects.filter(id=department_id)
    else:
        departments = Department.objects.all().order_by('name')

    department_tables = []
    total_presents = 0
    total_halves = 0
    total_absents = 0

    for dept in departments:
        employees = User.objects.filter(is_staff=False, userprofile__department=dept).order_by('username')
        table = []

        for emp in employees:
            row = {'user': emp.username, 'user_id': emp.id, 'days': [], 'present': 0, 'half': 0, 'absent': 0}
            for day in range(1, num_days + 1):
                current_date = date(year, month, day)
                status = 'A'  # default absent

                att = Attendance.objects.filter(user=emp, login_time__date=current_date).first()
                if att:
                    status = att.attendance_status()
                elif current_date.weekday() == 6:  # Sunday
                    status = 'Sunday'

                row['days'].append(status)

                if status == 'P':
                    row['present'] += 1
                    total_presents += 1
                elif status == 'H':
                    row['half'] += 1
                    total_halves += 1
                elif status == 'A':
                    row['absent'] += 1
                    total_absents += 1

            row['month_days'] = num_days
            table.append(row)

        department_tables.append({'department': dept.name, 'table': table})

    # Calculate attendance rate
    total_days = total_presents + total_halves + total_absents
    attendance_rate = round((total_presents + total_halves * 0.5) / total_days * 100, 2) if total_days > 0 else 0

    pending_leaves = LeaveRequest.objects.filter(status='Pending').order_by('-created_at')

    return render(request, 'admin_dashboard.html', {
        'department_tables': department_tables,
        'total_presents': total_presents,
        'total_halves': total_halves,
        'total_absents': total_absents,
        'attendance_rate': attendance_rate,
        'pending_leaves': pending_leaves,
        'years': range(date.today().year - 2, date.today().year + 1),
        'months': range(1, 13),
        'selected_year': year,
        'selected_month': month,
        'num_days': num_days,
        'selected_department': int(department_id) if department_id else None,
        'departments': Department.objects.all()
    })