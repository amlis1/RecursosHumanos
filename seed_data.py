import os, sys, django, random
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'RecursosHumanos.settings')
django.setup()

from Vacaciones.models import Departamento, Empleado, SolicitudPermiso, TurnoGuardia, Sustitucion
from django.contrib.auth.models import User

Departamento.objects.all().delete()
Empleado.objects.all().delete()
SolicitudPermiso.objects.all().delete()
TurnoGuardia.objects.all().delete()
Sustitucion.objects.all().delete()
User.objects.filter(is_superuser=False).delete()

print("=== 10 DEPARTAMENTOS ===")
deptos_data = [
    {"nombre": "Recursos Humanos", "descripcion": "Gestión del talento humano", "jefe_departamento": "María Fernández"},
    {"nombre": "Tecnología", "descripcion": "Desarrollo y soporte técnico", "jefe_departamento": "Carlos Mendoza"},
    {"nombre": "Contabilidad", "descripcion": "Finanzas y contabilidad", "jefe_departamento": "Ana García"},
    {"nombre": "Marketing", "descripcion": "Estrategias de marketing", "jefe_departamento": "Luis Torres"},
    {"nombre": "Operaciones", "descripcion": "Logística y producción", "jefe_departamento": "Rosa Martínez"},
    {"nombre": "Ventas", "descripcion": "Gestión comercial y ventas", "jefe_departamento": "Pedro Ramírez"},
    {"nombre": "Legal", "descripcion": "Asesoría jurídica", "jefe_departamento": "Diana López"},
    {"nombre": "Compras", "descripcion": "Adquisiciones y proveedores", "jefe_departamento": "Jorge Castillo"},
    {"nombre": "Investigación", "descripcion": "I+D e innovación", "jefe_departamento": "Sofía Herrera"},
    {"nombre": "Calidad", "descripcion": "Control de calidad y mejora continua", "jefe_departamento": "Mario Vargas"},
]
departamentos = [Departamento.objects.create(**d) for d in deptos_data]
for d in departamentos: print(f"  {d.nombre}")

print("\n=== 10 EMPLEADOS ===")
emp_data = [
    {"cedula": "1710000001", "nombres": "Juan", "apellidos": "Pérez García", "email": "juan.perez@empresa.com", "telefono": "0991000001", "fecha_nacimiento": date(1990, 5, 15), "genero": "M", "departamento": departamentos[0], "cargo": "Analista", "fecha_ingreso": date(2020, 3, 1), "salario": 1800, "dias_vacaciones_pendientes": 15, "dias_vacaciones_tomados": 15, "estado": "activo"},
    {"cedula": "1710000002", "nombres": "María", "apellidos": "López Sánchez", "email": "maria.lopez@empresa.com", "telefono": "0991000002", "fecha_nacimiento": date(1985, 8, 22), "genero": "F", "departamento": departamentos[0], "cargo": "Coordinadora", "fecha_ingreso": date(2018, 6, 15), "salario": 2500, "dias_vacaciones_pendientes": 22, "dias_vacaciones_tomados": 8, "estado": "activo"},
    {"cedula": "1710000003", "nombres": "Carlos", "apellidos": "Ramírez Torres", "email": "carlos.ramirez@empresa.com", "telefono": "0991000003", "fecha_nacimiento": date(1992, 11, 3), "genero": "M", "departamento": departamentos[1], "cargo": "Desarrollador", "fecha_ingreso": date(2021, 1, 10), "salario": 2200, "dias_vacaciones_pendientes": 20, "dias_vacaciones_tomados": 10, "estado": "activo"},
    {"cedula": "1710000004", "nombres": "Ana", "apellidos": "García Castro", "email": "ana.garcia@empresa.com", "telefono": "0991000004", "fecha_nacimiento": date(1995, 2, 18), "genero": "F", "departamento": departamentos[2], "cargo": "Asistente", "fecha_ingreso": date(2022, 4, 5), "salario": 1200, "dias_vacaciones_pendientes": 30, "dias_vacaciones_tomados": 0, "estado": "activo"},
    {"cedula": "1710000005", "nombres": "Pedro", "apellidos": "Martínez Ruiz", "email": "pedro.martinez@empresa.com", "telefono": "0991000005", "fecha_nacimiento": date(1988, 7, 25), "genero": "M", "departamento": departamentos[3], "cargo": "Especialista", "fecha_ingreso": date(2019, 9, 20), "salario": 2000, "dias_vacaciones_pendientes": 18, "dias_vacaciones_tomados": 12, "estado": "vacaciones"},
    {"cedula": "1710000006", "nombres": "Sofía", "apellidos": "Herrera Vargas", "email": "sofia.herrera@empresa.com", "telefono": "0991000006", "fecha_nacimiento": date(1993, 4, 12), "genero": "F", "departamento": departamentos[4], "cargo": "Supervisora", "fecha_ingreso": date(2020, 11, 1), "salario": 2300, "dias_vacaciones_pendientes": 10, "dias_vacaciones_tomados": 20, "estado": "activo"},
    {"cedula": "1710000007", "nombres": "Luis", "apellidos": "Torres Morales", "email": "luis.torres@empresa.com", "telefono": "0991000007", "fecha_nacimiento": date(1987, 12, 30), "genero": "M", "departamento": departamentos[5], "cargo": "Vendedor", "fecha_ingreso": date(2017, 5, 15), "salario": 1600, "dias_vacaciones_pendientes": 5, "dias_vacaciones_tomados": 25, "estado": "licencia"},
    {"cedula": "1710000008", "nombres": "Diana", "apellidos": "Castillo Rojas", "email": "diana.castillo@empresa.com", "telefono": "0991000008", "fecha_nacimiento": date(1991, 9, 8), "genero": "F", "departamento": departamentos[6], "cargo": "Abogada", "fecha_ingreso": date(2021, 8, 16), "salario": 2800, "dias_vacaciones_pendientes": 25, "dias_vacaciones_tomados": 5, "estado": "activo"},
    {"cedula": "1710000009", "nombres": "Jorge", "apellidos": "Mendoza Ortiz", "email": "jorge.mendoza@empresa.com", "telefono": "0991000009", "fecha_nacimiento": date(1984, 6, 14), "genero": "M", "departamento": departamentos[7], "cargo": "Jefe de Compras", "fecha_ingreso": date(2016, 2, 1), "salario": 3200, "dias_vacaciones_pendientes": 12, "dias_vacaciones_tomados": 18, "estado": "activo"},
    {"cedula": "1710000010", "nombres": "Laura", "apellidos": "Gutiérrez Flores", "email": "laura.gutierrez@empresa.com", "telefono": "0991000010", "fecha_nacimiento": date(1994, 3, 27), "genero": "F", "departamento": departamentos[8], "cargo": "Investigadora", "fecha_ingreso": date(2023, 1, 10), "salario": 2100, "dias_vacaciones_pendientes": 30, "dias_vacaciones_tomados": 0, "estado": "activo"},
]
empleados = [Empleado.objects.create(**e) for e in emp_data]
for e in empleados: print(f"  {e.nombres} {e.apellidos} - {e.departamento.nombre}")

print("\n=== 10 SOLICITUDES DE PERMISO ===")
permisos_data = [
    {"empleado": empleados[0], "tipo": "vacaciones", "motivo": "Vacaciones familiares programadas", "fecha_inicio": date(2026, 8, 1), "fecha_fin": date(2026, 8, 10), "dias_solicitados": 10, "estado": "aprobado"},
    {"empleado": empleados[1], "tipo": "personal", "motivo": "Trámites personales urgentes", "fecha_inicio": date(2026, 7, 15), "fecha_fin": date(2026, 7, 16), "dias_solicitados": 2, "estado": "aprobado"},
    {"empleado": empleados[2], "tipo": "medico", "motivo": "Cita médica especializada", "fecha_inicio": date(2026, 7, 20), "fecha_fin": date(2026, 7, 20), "dias_solicitados": 1, "estado": "pendiente"},
    {"empleado": empleados[3], "tipo": "vacaciones", "motivo": "Viaje al extranjero", "fecha_inicio": date(2026, 9, 5), "fecha_fin": date(2026, 9, 15), "dias_solicitados": 11, "estado": "pendiente"},
    {"empleado": empleados[4], "tipo": "luto", "motivo": "Fallecimiento de familiar", "fecha_inicio": date(2026, 6, 10), "fecha_fin": date(2026, 6, 13), "dias_solicitados": 3, "estado": "aprobado"},
    {"empleado": empleados[5], "tipo": "personal", "motivo": "Asuntos escolares", "fecha_inicio": date(2026, 8, 20), "fecha_fin": date(2026, 8, 21), "dias_solicitados": 2, "estado": "pendiente"},
    {"empleado": empleados[6], "tipo": "medico", "motivo": "Cirugía programada", "fecha_inicio": date(2026, 7, 28), "fecha_fin": date(2026, 8, 5), "dias_solicitados": 9, "estado": "aprobado"},
    {"empleado": empleados[7], "tipo": "maternidad", "motivo": "Licencia de maternidad", "fecha_inicio": date(2026, 10, 1), "fecha_fin": date(2026, 12, 31), "dias_solicitados": 92, "estado": "pendiente"},
    {"empleado": empleados[8], "tipo": "vacaciones", "motivo": "Descanso anual", "fecha_inicio": date(2026, 8, 15), "fecha_fin": date(2026, 8, 25), "dias_solicitados": 11, "estado": "rechazado"},
    {"empleado": empleados[9], "tipo": "otro", "motivo": "Capacitación externa", "fecha_inicio": date(2026, 7, 22), "fecha_fin": date(2026, 7, 26), "dias_solicitados": 5, "estado": "aprobado"},
]
permisos = [SolicitudPermiso.objects.create(**p) for p in permisos_data]
for p in permisos: print(f"  {p.empleado.nombres} {p.empleado.apellidos} - {p.get_tipo_display()} [{p.get_estado_display()}]")

print("\n=== 10 TURNOS DE GUARDIA ===")
turnos_data = [
    {"empleado": empleados[0], "fecha": date(2026, 7, 28), "turno": "manana", "horas": 8, "observaciones": "Turno regular"},
    {"empleado": empleados[1], "fecha": date(2026, 7, 28), "turno": "tarde", "horas": 8, "observaciones": "Turno regular"},
    {"empleado": empleados[2], "fecha": date(2026, 7, 28), "turno": "noche", "horas": 8, "observaciones": "Turno nocturno"},
    {"empleado": empleados[3], "fecha": date(2026, 7, 29), "turno": "manana", "horas": 8, "observaciones": "Turno regular"},
    {"empleado": empleados[4], "fecha": date(2026, 7, 29), "turno": "tarde", "horas": 8, "observaciones": "Turno regular"},
    {"empleado": empleados[5], "fecha": date(2026, 7, 29), "turno": "noche", "horas": 8, "observaciones": "Turno nocturno"},
    {"empleado": empleados[6], "fecha": date(2026, 7, 30), "turno": "manana", "horas": 8, "observaciones": "Turno regular"},
    {"empleado": empleados[7], "fecha": date(2026, 7, 30), "turno": "tarde", "horas": 8, "observaciones": "Turno regular"},
    {"empleado": empleados[8], "fecha": date(2026, 7, 30), "turno": "noche", "horas": 8, "observaciones": "Turno nocturno"},
    {"empleado": empleados[9], "fecha": date(2026, 7, 31), "turno": "manana", "horas": 8, "observaciones": "Turno de fin de mes"},
]
turnos = [TurnoGuardia.objects.create(**t) for t in turnos_data]
for t in turnos: print(f"  {t.empleado.nombres} {t.empleado.apellidos} - {t.fecha} - {t.get_turno_display()}")

print("\n=== 10 SUSTITUCIONES ===")
sust_data = [
    {"turno_original": turnos[0], "empleado_sustituto": empleados[9], "motivo": "Cambio por compromiso familiar", "estado": "aceptada", "observaciones": "Aprobado por RRHH"},
    {"turno_original": turnos[1], "empleado_sustituto": empleados[8], "motivo": "Necesidad médica del empleado original", "estado": "pendiente", "observaciones": "Pendiente de revisión"},
    {"turno_original": turnos[2], "empleado_sustituto": empleados[7], "motivo": "Intercambio voluntario", "estado": "completada", "observaciones": "Cambio realizado"},
    {"turno_original": turnos[3], "empleado_sustituto": empleados[6], "motivo": "Por capacitación programada", "estado": "aceptada", "observaciones": "Autorizado por jefe directo"},
    {"turno_original": turnos[4], "empleado_sustituto": empleados[5], "motivo": "Viaje imprevisto", "estado": "pendiente", "observaciones": "Requiere documentación"},
    {"turno_original": turnos[5], "empleado_sustituto": empleados[4], "motivo": "Razones personales", "estado": "rechazada", "observaciones": "Sin cobertura disponible"},
    {"turno_original": turnos[6], "empleado_sustituto": empleados[3], "motivo": "Emergencia familiar", "estado": "aceptada", "observaciones": "Aprobado con condiciones"},
    {"turno_original": turnos[7], "empleado_sustituto": empleados[2], "motivo": "Cambio de turno solicitado", "estado": "pendiente", "observaciones": "En espera de confirmación"},
    {"turno_original": turnos[8], "empleado_sustituto": empleados[1], "motivo": "Estudios nocturnos", "estado": "aceptada", "observaciones": "Cambio definitivo"},
    {"turno_original": turnos[9], "empleado_sustituto": empleados[0], "motivo": "Coordinación de horarios", "estado": "completada", "observaciones": "Sustitución exitosa"},
]
sustituciones = [Sustitucion.objects.create(**s) for s in sust_data]
for s in sustituciones: print(f"  {s.turno_original.empleado.nombres} → {s.empleado_sustituto.nombres} [{s.get_estado_display()}]")

print("\n=== 1 USUARIO ADMIN ===")
if not User.objects.filter(username="admin").exists():
    User.objects.create_superuser("admin", "admin@empresa.com", "admin123")
    print("  Usuario admin creado (admin / admin123)")
else:
    print("  Usuario admin ya existe")

print("\n=== VERIFICACIÓN FINAL ===")
print(f"  Departamentos: {Departamento.objects.count()}")
print(f"  Empleados: {Empleado.objects.count()}")
print(f"  Solicitudes: {SolicitudPermiso.objects.count()}")
print(f"  Turnos: {TurnoGuardia.objects.count()}")
print(f"  Sustituciones: {Sustitucion.objects.count()}")
print("\n✅ Datos inicializados correctamente en PostgreSQL")
