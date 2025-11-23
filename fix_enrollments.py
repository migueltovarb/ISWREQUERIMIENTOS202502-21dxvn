import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inscripcion_project.settings')
django.setup()

from core.models import Enrollment

print("🔧 LIMPIANDO INSCRIPCIONES...")

# Contar antes
before = Enrollment.objects.count()
print(f"   Inscripciones antes: {before}")

# Eliminar todas
Enrollment.objects.all().delete()

# Contar después
after = Enrollment.objects.count()
print(f"   Inscripciones después: {after}")

print("✅ LISTO! Todas las inscripciones eliminadas.")
print("🎯 Ahora puedes inscribirte de nuevo normalmente.")