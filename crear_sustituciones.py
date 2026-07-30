import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'RecursosHumanos.settings')
django.setup()

from Vacaciones.models import TurnoGuardia, Empleado, Sustitucion
from datetime import datetime, timedelta
import random

turnos = list(TurnoGuardia.objects.select_related('empleado').all())
empleados = list(Empleado.objects.all())

if not turnos:
    print("No hay turnos. Creando turnos de prueba...")
    emp_sample = empleados[:10]
    base = datetime(2026, 7, 28).date()
    turnos_creados = []
    for i, emp in enumerate(emp_sample):
        for j, turno_tipo in enumerate(['manana', 'tarde', 'noche']):
            fecha = base + timedelta(days=i + j)
            t, _ = TurnoGuardia.objects.get_or_create(
                empleado=emp, fecha=fecha, turno=turno_tipo,
                defaults={'horas': 8, 'observaciones': f'Turno de prueba {turno_tipo}'}
            )
            turnos_creados.append(t)
    turnos = list(TurnoGuardia.objects.select_related('empleado').all())

motivos = [
    "Cambio de turno por compromiso familiar",
    "Necesidad médica del empleado original",
    "Intercambio por solicitud del empleado",
    "Cambio por motivos de estudio",
    "Sustitución por viaje programado",
    "Cambio de turno por capacitación",
    "Intercambio por razones personales",
    "Sustitución por emergencia familiar",
    "Cambio por coincidencia de horario laboral",
    "Intercambio por mejor distribución de carga",
]

observaciones_list = [
    "Aprobado por el jefe de departamento",
    "Pendiente de revisión",
    "Cambio temporal por una semana",
    "Coordinado entre ambos empleados",
    "Autorizado por recursos humanos",
    "Cambio definitivo",
    "Requiere seguimiento",
    "Sin observaciones adicionales",
    "Documentación adjunta",
    "Aprobado con condiciones",
]

estados = ['pendiente', 'pendiente', 'pendiente', 'aceptada', 'aceptada', 'completada', 'completada', 'rechazada', 'pendiente', 'completada']

sustituciones_creadas = 0
used_combos = set()

for i in range(10):
    turno = turnos[i % len(turnos)]
    sustitutos = [e for e in empleados if e.id != turno.empleado.id and (turno.id, e.id) not in used_combos]
    if not sustitutos:
        continue
    sustituto = random.choice(sustitutos)
    used_combos.add((turno.id, sustituto.id))
    
    estado = estados[i % len(estados)]
    
    sust, created = Sustitucion.objects.get_or_create(
        turno_original=turno,
        empleado_sustituto=sustituto,
        defaults={
            'motivo': motivos[i % len(motivos)],
            'estado': estado,
            'observaciones': observaciones_list[i % len(observaciones_list)],
        }
    )
    if created:
        sustituciones_creadas += 1
        print(f"  Creada sustitución {sust.id}: {turno.empleado.nombre_completo} -> {sustituto.nombre_completo} [{estado}]")
    else:
        print(f"  Ya existía: {turno.empleado.nombre_completo} -> {sustituto.nombre_completo}")

print(f"\nTotal sustituciones creadas: {sustituciones_creadas}")
print(f"Total sustituciones en BD: {Sustitucion.objects.count()}")
