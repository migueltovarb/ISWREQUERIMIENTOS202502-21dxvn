from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    path('courses/', views.course_list, name='course_list'),
    path('courses/<int:course_id>/', views.course_detail, name='course_detail'),
    path('courses/<int:course_id>/enroll/', views.enroll_course, name='enroll_course'),
    
    path('my-enrollments/', views.my_enrollments, name='my_enrollments'),
    path('enrollments/<int:enrollment_id>/cancel/', views.cancel_enrollment, name='cancel_enrollment'),
    
    path('payments/<int:enrollment_id>/', views.payment_page, name='payment_page'),
    path('payments/<int:enrollment_id>/process/', views.process_payment, name='process_payment'),
    
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/<int:notification_id>/mark-read/', views.mark_notification_read, name='mark_notification_read'),
    
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('admin-panel/courses/', views.manage_courses, name='manage_courses'),
    path('admin-panel/courses/add/', views.add_course, name='add_course'),
    path('admin-panel/reports/', views.generate_reports, name='generate_reports'),
]