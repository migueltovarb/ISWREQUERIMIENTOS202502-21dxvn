import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inscripcion_project.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Enrollment

print("=== DIAGNÓSTICO DE INSCRIPCIONES ===")

# Ver usuarios
users = User.objects.all()
print("\n📋 USUARIOS:")
for user in users:
    print(f"   - {user.username} ({user.email})")

# Ver inscripciones
enrollments = Enrollment.objects.all()
print(f"\n🎓 INSCRIPCIONES TOTALES: {enrollments.count()}")

print("\n📚 DETALLE DE INSCRIPCIONES:")
for e in enrollments:
    print(f"   - {e.student.username} en {e.course.code}: {e.status}")

# Ver inscripciones de estudiante1
print("\n🔍 INSCRIPCIONES DE estudiante1:")
try:
    user = User.objects.get(username='estudiante1')
    user_enrollments = Enrollment.objects.filter(student=user)
    if user_enrollments:
        for e in user_enrollments:
            print(f"   - Curso: {e.course.code}, Estado: {e.status}")
    else:
        print("   No tiene inscripciones")
except User.DoesNotExist:
    print("   Usuario no encontrado")

print("\n💡 SOLUCIÓN: Si hay inscripciones problemáticas, ejecuta: python fix_enrollments.py")