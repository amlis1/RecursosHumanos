import os
import sys
import django
import random
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'RecursosHumanos.settings')
django.setup()

from Vacaciones.models import Departamento, Empleado, SolicitudPermiso, TurnoGuardia

print("Limpiando datos anteriores...")
Sustitucion = None
try:
    from Vacaciones.models import Sustitucion
    Sustitucion.objects.all().delete()
except:
    pass
TurnoGuardia.objects.all().delete()
SolicitudPermiso.objects.all().delete()
Empleado.objects.all().delete()
Departamento.objects.all().delete()

print("Creando departamentos...")
departamentos_data = [
    {"nombre": "Recursos Humanos", "descripcion": "Gestion del talento humano y bienestar laboral", "jefe_departamento": "Maria Fernandez"},
    {"nombre": "Tecnologia", "descripcion": "Desarrollo de software y soporte tecnico", "jefe_departamento": "Carlos Mendoza"},
    {"nombre": "Contabilidad", "descripcion": "Finanzas, contabilidad y auditoria interna", "jefe_departamento": "Ana Garcia"},
    {"nombre": "Marketing", "descripcion": "Estrategias de marketing y comunicacion", "jefe_departamento": "Luis Torres"},
    {"nombre": "Operaciones", "descripcion": "Logistica, cadena de suministro y produccion", "jefe_departamento": "Rosa Martinez"},
]

deptos = []
for d in departamentos_data:
    dept = Departamento.objects.create(**d)
    deptos.append(dept)
    print(f"  + {dept.nombre}")

print("Creando empleados...")
nombres_m = ["Juan","Pedro","Luis","Carlos","Miguel","Andres","Jose","Diego","Marco","Roberto","Fernando","Ricardo","Eduardo","Sergio","Raul","Oscar","Alberto","Rafael","Tomas","Javier"]
nombres_f = ["Maria","Ana","Rosa","Laura","Sofia","Elena","Lucia","Carmen","Teresa","Patricia","Claudia","Veronica","Sandra","Adriana","Daniela","Paola","Gloria","Monica","Isabel","Rocio"]
apellidos = ["Garcia","Rodriguez","Martinez","Lopez","Hernandez","Gonzalez","Perez","Sanchez","Ramirez","Torres","Flores","Rivera","Gomez","Diaz","Cruz","Morales","Reyes","Ortiz","Gutierrez","Vargas"]
cargos = ["Analista","Asistente","Gerente","Coordinador","Especialista","Tecnico","Supervisor","Director","Auxiliar","Jefe"]
estados = ["activo","activo","activo","activo","activo","activo","activo","activo","vacaciones","licencia"]

empleados_creados = []
for dept in deptos:
    for i in range(10):
        gen = random.choice(["M","F"])
        nom = random.choice(nombres_m if gen == "M" else nombres_f)
        ape = random.choice(apellidos) + " " + random.choice(apellidos)
        cedula = f"17{random.randint(10000000,99999999)}"
        email = f"{nom.lower()}.{ape.split()[0].lower()}{random.randint(1,99)}@empresa.com"
        tel = f"099{random.randint(1000000,9999999)}"
        fn = date(random.randint(1975,2000), random.randint(1,12), random.randint(1,28))
        fi = date(random.randint(2015,2024), random.randint(1,12), random.randint(1,28))
        salario = round(random.uniform(800, 3500), 2)
        cargo = random.choice(cargos)
        estado = random.choice(estados)
        dias_pend = random.randint(5, 30)
        dias_tom = random.randint(0, 25)

        emp = Empleado(
            cedula=cedula,
            nombres=nom,
            apellidos=ape,
            email=email,
            telefono=tel,
            fecha_nacimiento=fn,
            genero=gen,
            direccion=f"Av. {random.choice(['Libertador','Amazonas','6 de Octubre','America','Republica'])} {random.randint(1,2000)}",
            departamento=dept,
            cargo=cargo,
            fecha_ingreso=fi,
            salario=salario,
            dias_vacaciones_pendientes=dias_pend,
            dias_vacaciones_tomados=dias_tom,
            estado=estado,
        )
        emp.save()
        empleados_creados.append(emp)

print(f"  {len(empleados_creados)} empleados creados")

print("Creando solicitudes de permiso...")
tipos = ["vacaciones","personal","medico","luto","maternidad","otro"]
motivos = [
    "Vacaciones familiares programadas",
    "Cita medica de control",
    "Permiso personal por asuntos familiares",
    "Duelo familiar",
    "Licencia de maternidad",
    "Cita odontologica",
    "Permiso para tramites personales",
    "Reposo medico",
]
estados_perm = ["pendiente","aprobado","aprobado","aprobado","rechazado","pendiente","pendiente","aprobado"]

for emp in random.sample(empleados_creados, 25):
    tipo = random.choice(tipos)
    fi = date(2026, random.randint(1,12), random.randint(1,28))
    dias = random.randint(1, 15)
    ff = fi + timedelta(days=dias-1)
    estado = random.choice(estados_perm)
    SolicitudPermiso.objects.create(
        empleado=emp,
        tipo=tipo,
        motivo=random.choice(motivos),
        fecha_inicio=fi,
        fecha_fin=ff,
        dias_solicitados=dias,
        estado=estado,
    )

print("  25 permisos creados")

print("Creando turnos de guardia...")
turnos_tipo = ["manana","tarde","noche"]
for i in range(30):
    emp = random.choice(empleados_creados)
    fecha = date(2026, 7, random.randint(1,31))
    turno = random.choice(turnos_tipo)
    try:
        TurnoGuardia.objects.create(
            empleado=emp,
            fecha=fecha,
            turno=turno,
            horas=8,
            observaciones="Turno asignado automaticamente",
        )
    except:
        pass

print("  Turnos creados")

print("\n=== DATOS CREADOS EXITOSAMENTE ===")
print(f"  Departamentos: {Departamento.objects.count()}")
print(f"  Empleados: {Empleado.objects.count()}")
print(f"  Permisos: {SolicitudPermiso.objects.count()}")
print(f"  Turnos: {TurnoGuardia.objects.count()}")
