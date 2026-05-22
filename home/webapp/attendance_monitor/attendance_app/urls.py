from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('set_password/', views.set_password_view, name='set_password'),
    path('mark_present/', views.mark_present, name='mark_present'),
    path('mark_logout/', views.mark_logout, name='mark_logout'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('approve_leave/<int:leave_id>/', views.approve_leave, name='approve_leave'),
    path('reject_leave/<int:leave_id>/', views.reject_leave, name='reject_leave'),
    path('employee_details/<int:user_id>/', views.employee_details, name='employee_details'),
    path('delete_employee/<int:user_id>/', views.delete_employee, name='delete_employee'),
    path('edit_employee/<int:user_id>/', views.edit_employee, name='edit_employee'),
    path('add_employee/', views.add_employee, name='add_employee'),
]
