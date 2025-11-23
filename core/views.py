from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.core.mail import send_mail
from django.utils import timezone
from django.db.models import Q, Count
import csv

from .models import Profile, Course, Enrollment, Payment, Notification
from .forms import CustomUserCreationForm, CourseForm
from django.template.defaulttags import register

@register.filter
def mul(value, arg):
    """Multiplica value por arg"""
    return float(value) * float(arg)

def home(request):
    if request.user.is_authenticated:
        profile = getattr(request.user, 'profile', None)
        if profile:
            if profile.role == 'admin':
                return redirect('admin_panel')
        return redirect('course_list')
    return render(request, 'core/home.html')

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                # Guardar el usuario usando el método save() del formulario
                user = form.save()
                
                # Iniciar sesión automáticamente
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password1')
                user = authenticate(username=username, password=password)
                
                if user is not None:
                    login(request, user)
                    messages.success(request, '¡Registro exitoso! Bienvenido a la plataforma.')
                    return redirect('home')
                else:
                    messages.error(request, 'Error al iniciar sesión automáticamente. Por favor inicia sesión manualmente.')
                    return redirect('login')
                    
            except Exception as e:
                messages.error(request, f'Error durante el registro: {str(e)}')
                return render(request, 'core/register.html', {'form': form})
                
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'core/register.html', {'form': form})

@login_required
def course_list(request):
    query = request.GET.get('q', '')
    courses = Course.objects.filter(is_active=True)
    
    if query:
        courses = courses.filter(
            Q(code__icontains=query) | 
            Q(name__icontains=query) |
            Q(professor__first_name__icontains=query) |
            Q(professor__last_name__icontains=query)
        )
    
    context = {
        'courses': courses,
        'query': query,
    }
    return render(request, 'core/course_list.html', context)

@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id, is_active=True)
    is_enrolled = False
    enrollment = None
    
    if request.user.is_authenticated and hasattr(request.user, 'profile'):
        if request.user.profile.role == 'student':
            enrollment = Enrollment.objects.filter(
                student=request.user, 
                course=course
            ).first()
            is_enrolled = enrollment is not None
    
    context = {
        'course': course,
        'is_enrolled': is_enrolled,
        'enrollment': enrollment,
    }
    return render(request, 'core/course_detail.html', context)

@login_required
def enroll_course(request, course_id):
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'student':
        messages.error(request, 'Solo los estudiantes pueden inscribirse en cursos.')
        return redirect('course_list')
    
    course = get_object_or_404(Course, id=course_id, is_active=True)
    
    existing_enrollment = Enrollment.objects.filter(
        student=request.user, 
        course=course
    ).first()
    
    if existing_enrollment:
        messages.warning(request, 'Ya estás inscrito en este curso.')
        return redirect('course_detail', course_id=course_id)
    
    if course.available_spots <= 0:
        messages.error(request, 'No hay cupos disponibles para este curso.')
        return redirect('course_detail', course_id=course_id)
    
    enrollment = Enrollment.objects.create(
        student=request.user,
        course=course,
        status='pending'
    )
    
    course.available_spots -= 1
    course.save()
    
    Notification.objects.create(
        user=request.user,
        message=f'Te has inscrito exitosamente al curso {course.code} - {course.name}. Estado: Pendiente de pago.'
    )
    
    send_mail(
        'Inscripción a Curso - Plataforma Universitaria',
        f'Hola {request.user.first_name},\n\nTe has inscrito al curso {course.code} - {course.name}.\nEstado: Pendiente de pago.\n\nPor favor realiza el pago para confirmar tu inscripción.\n\nSaludos,\nPlataforma de Inscripción',
        'noreply@universidad.edu',
        [request.user.email],
        fail_silently=True,
    )
    
    messages.success(request, '¡Inscripción exitosa! Por favor realiza el pago para confirmar.')
    return redirect('my_enrollments')

@login_required
def my_enrollments(request):
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'student':
        messages.error(request, 'Solo los estudiantes pueden ver sus inscripciones.')
        return redirect('course_list')
    
    enrollments = Enrollment.objects.filter(student=request.user).select_related('course')
    
    context = {
        'enrollments': enrollments,
    }
    return render(request, 'core/my_enrollments.html', context)

@login_required
def cancel_enrollment(request, enrollment_id):
    enrollment = get_object_or_404(Enrollment, id=enrollment_id, student=request.user)
    
    if enrollment.status == 'cancelled':
        messages.warning(request, 'Esta inscripción ya estaba cancelada.')
        return redirect('my_enrollments')
    
    # Cambiar estado y liberar cupo
    enrollment.status = 'cancelled'
    enrollment.save()
    
    course = enrollment.course
    course.available_spots += 1
    course.save()
    
    # Crear notificación
    Notification.objects.create(
        user=request.user,
        message=f'Has cancelado tu inscripción al curso {course.code} - {course.name}.'
    )
    
    # Enviar email
    send_mail(
        'Cancelación de Inscripción - Plataforma Universitaria',
        f'Hola {request.user.first_name},\n\nHas cancelado tu inscripción al curso {course.code} - {course.name}.\n\nSaludos,\nPlataforma de Inscripción',
        'noreply@universidad.edu',
        [request.user.email],
        fail_silently=True,
    )
    
    messages.success(request, 'Inscripción cancelada exitosamente. Ahora puedes inscribirte de nuevo si lo deseas.')
    return redirect('course_list')  # Cambiado: redirigir a la lista de cursos en lugar de mis inscripciones

@login_required
def payment_page(request, enrollment_id):
    enrollment = get_object_or_404(Enrollment, id=enrollment_id, student=request.user)
    
    try:
        payment = enrollment.payment
    except Payment.DoesNotExist:
        payment = None
    
    context = {
        'enrollment': enrollment,
        'payment': payment,
    }
    return render(request, 'core/payment_page.html', context)

@login_required
def process_payment(request, enrollment_id):
    enrollment = get_object_or_404(Enrollment, id=enrollment_id, student=request.user)
    
    try:
        existing_payment = enrollment.payment
        if existing_payment.status == 'completed':
            messages.warning(request, 'El pago ya fue procesado anteriormente.')
            return redirect('my_enrollments')
    except Payment.DoesNotExist:
        existing_payment = None
    
    payment_method = request.POST.get('payment_method', 'pse')
    amount = enrollment.course.credits * 100000
    
    if existing_payment:
        payment = existing_payment
        payment.method = payment_method
    else:
        payment = Payment.objects.create(
            enrollment=enrollment,
            amount=amount,
            method=payment_method,
            status='completed',
            transaction_id=f"TXN{timezone.now().strftime('%Y%m%d%H%M%S')}"
        )
    
    enrollment.status = 'confirmed'
    enrollment.save()
    
    Notification.objects.create(
        user=request.user,
        message=f'Pago confirmado para el curso {enrollment.course.code} - {enrollment.course.name}. Inscripción confirmada.'
    )
    
    send_mail(
        'Confirmación de Pago - Plataforma Universitaria',
        f'Hola {request.user.first_name},\n\nTu pago por ${amount:,.0f} para el curso {enrollment.course.code} - {enrollment.course.name} ha sido confirmado.\n\nTu inscripción está ahora confirmada.\n\nSaludos,\nPlataforma de Inscripción',
        'noreply@universidad.edu',
        [request.user.email],
        fail_silently=True,
    )
    
    messages.success(request, '¡Pago procesado exitosamente! Tu inscripción ha sido confirmada.')
    return redirect('my_enrollments')

@login_required
def notifications(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    unread_count = notifications.filter(is_read=False).count()
    
    context = {
        'notifications': notifications,
        'unread_count': unread_count,
    }
    return render(request, 'core/notifications.html', context)

@login_required
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    return redirect('notifications')

def is_admin(user):
    return hasattr(user, 'profile') and user.profile.role == 'admin'

@login_required
@user_passes_test(is_admin)
def admin_panel(request):
    total_courses = Course.objects.count()
    total_students = Profile.objects.filter(role='student').count()
    total_professors = Profile.objects.filter(role='professor').count()
    total_enrollments = Enrollment.objects.count()
    
    recent_enrollments = Enrollment.objects.select_related('student', 'course').order_by('-created_at')[:5]
    
    context = {
        'total_courses': total_courses,
        'total_students': total_students,
        'total_professors': total_professors,
        'total_enrollments': total_enrollments,
        'recent_enrollments': recent_enrollments,
    }
    return render(request, 'core/admin_panel.html', context)

@login_required
@user_passes_test(is_admin)
def manage_courses(request):
    courses = Course.objects.all().select_related('professor')
    
    context = {
        'courses': courses,
    }
    return render(request, 'core/manage_courses.html', context)

@login_required
@user_passes_test(is_admin)
def add_course(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.available_spots = course.capacity
            course.save()
            
            messages.success(request, 'Curso creado exitosamente.')
            return redirect('manage_courses')
    else:
        form = CourseForm()
    
    context = {
        'form': form,
    }
    return render(request, 'core/course_form.html', context)

@login_required
@user_passes_test(is_admin)
def generate_reports(request):
    report_type = request.GET.get('type', 'enrollments')
    
    if report_type == 'enrollments':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="reporte_inscripciones.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Código Curso', 'Nombre Curso', 'Profesor', 'Inscripciones Confirmadas', 'Inscripciones Pendientes'])
        
        courses = Course.objects.annotate(
            confirmed_count=Count('enrollment', filter=Q(enrollment__status='confirmed')),
            pending_count=Count('enrollment', filter=Q(enrollment__status='pending'))
        )
        
        for course in courses:
            writer.writerow([
                course.code,
                course.name,
                f"{course.professor.first_name} {course.professor.last_name}",
                course.confirmed_count,
                course.pending_count
            ])
        
        return response
    
    return HttpResponse('Tipo de reporte no válido')
