import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inscripcion_project.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Profile, Course

# Limpiar datos existentes (opcional)
User.objects.filter(username__in=['admin', 'profesor1', 'estudiante1']).delete()
Course.objects.filter(code__in=['MAT101', 'PROG202']).delete()

# Crear admin
admin_user = User.objects.create_user('admin', 'admin@universidad.edu', 'admin123')
admin_user.first_name = 'Admin'
admin_user.last_name = 'Principal'
admin_user.save()
admin_user.profile.role = 'admin'
admin_user.profile.save()

# Crear profesor
professor = User.objects.create_user('profesor1', 'profesor1@universidad.edu', 'profesor123')
professor.first_name = 'Carlos'
professor.last_name = 'Gomez'
professor.save()
professor.profile.role = 'professor'
professor.profile.save()

# Crear estudiante
student = User.objects.create_user('estudiante1', 'estudiante1@universidad.edu', 'estudiante123')
student.first_name = 'Maria'
student.last_name = 'Lopez'
student.save()
student.profile.role = 'student'
student.profile.programa = 'Ingenieria de Sistemas'
student.profile.semestre = 5
student.profile.save()

# Crear cursos
Course.objects.create(
    code='MAT101',
    name='Calculo Diferencial',
    credits=4,
    professor=professor,
    schedule='Lunes y Miercoles 8:00-10:00',
    capacity=30,
    available_spots=30,
    description='Fundamentos del calculo diferencial y sus aplicaciones.'
)

Course.objects.create(
    code='PROG202',
    name='Programacion Avanzada',
    credits=3,
    professor=professor,
    schedule='Martes y Jueves 10:00-12:00',
    capacity=25,
    available_spots=25,
    description='Programacion orientada a objetos y estructuras de datos.'
)

print("✅ DATOS CREADOS EXITOSAMENTE!")
print("👤 USUARIOS:")
print("   admin / admin123")
print("   profesor1 / profesor123") 
print("   estudiante1 / estudiante123")
print("📚 CURSOS: MAT101, PROG202")