from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User


class Departamento(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, default='')
    jefe_departamento = models.CharField(max_length=150, blank=True, default='')
    fecha_creacion = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'jefe_departamento': self.jefe_departamento,
            'fecha_creacion': self.fecha_creacion.strftime('%Y-%m-%d'),
        }


class Empleado(models.Model):
    ESTADO_CHOICES = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
        ('vacaciones', 'En Vacaciones'),
        ('licencia', 'En Licencia'),
    ]
    GENERO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
    ]

    cedula = models.CharField(max_length=15, unique=True)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20, blank=True, default='')
    fecha_nacimiento = models.DateField(null=True, blank=True)
    genero = models.CharField(max_length=1, choices=GENERO_CHOICES, blank=True, default='')
    direccion = models.TextField(blank=True, default='')
    departamento = models.ForeignKey(Departamento, on_delete=models.PROTECT, related_name='empleados')
    cargo = models.CharField(max_length=100, blank=True, default='')
    fecha_ingreso = models.DateField()
    salario = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    dias_vacaciones_pendientes = models.IntegerField(default=30)
    dias_vacaciones_tomados = models.IntegerField(default=0)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='activo')
    foto = models.ImageField(upload_to='empleados/', blank=True, null=True)
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='empleado')

    class Meta:
        ordering = ['apellidos', 'nombres']

    def __str__(self):
        return f'{self.apellidos} {self.nombres}'

    @property
    def nombre_completo(self):
        return f'{self.nombres} {self.apellidos}'

    def to_dict(self):
        return {
            'id': self.id,
            'cedula': self.cedula,
            'nombres': self.nombres,
            'apellidos': self.apellidos,
            'nombre_completo': self.nombre_completo,
            'email': self.email,
            'telefono': self.telefono,
            'fecha_nacimiento': self.fecha_nacimiento.strftime('%Y-%m-%d') if self.fecha_nacimiento else '',
            'genero': self.genero,
            'direccion': self.direccion,
            'departamento': self.departamento.nombre,
            'departamento_id': self.departamento.id,
            'cargo': self.cargo,
            'fecha_ingreso': self.fecha_ingreso.strftime('%Y-%m-%d'),
            'salario': float(self.salario),
            'dias_vacaciones_pendientes': self.dias_vacaciones_pendientes,
            'dias_vacaciones_tomados': self.dias_vacaciones_tomados,
            'estado': self.estado,
            'foto': self.foto.url if self.foto else '',
        }


class SolicitudPermiso(models.Model):
    TIPO_CHOICES = [
        ('vacaciones', 'Vacaciones'),
        ('personal', 'Permiso Personal'),
        ('medico', 'Permiso Médico'),
        ('luto', 'Luto'),
        ('maternidad', 'Maternidad/Paternidad'),
        ('otro', 'Otro'),
    ]
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
        ('cancelado', 'Cancelado'),
    ]

    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name='solicitudes')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    motivo = models.TextField()
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    dias_solicitados = models.IntegerField(validators=[MinValueValidator(1)])
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    aprobado_por = models.CharField(max_length=150, blank=True, default='')
    observaciones = models.TextField(blank=True, default='')
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_respuesta = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-fecha_solicitud']

    def __str__(self):
        return f'{self.empleado.nombre_completo} - {self.get_tipo_display()} ({self.get_estado_display()})'

    def to_dict(self):
        return {
            'id': self.id,
            'empleado_id': self.empleado.id,
            'empleado_nombre': self.empleado.nombre_completo,
            'departamento': self.empleado.departamento.nombre,
            'tipo': self.tipo,
            'tipo_display': self.get_tipo_display(),
            'motivo': self.motivo,
            'fecha_inicio': self.fecha_inicio.strftime('%Y-%m-%d'),
            'fecha_fin': self.fecha_fin.strftime('%Y-%m-%d'),
            'dias_solicitados': self.dias_solicitados,
            'estado': self.estado,
            'estado_display': self.get_estado_display(),
            'aprobado_por': self.aprobado_por,
            'observaciones': self.observaciones,
            'fecha_solicitud': self.fecha_solicitud.strftime('%Y-%m-%d %H:%M'),
        }


class TurnoGuardia(models.Model):
    TURNO_CHOICES = [
        ('manana', 'Mañana (06:00-14:00)'),
        ('tarde', 'Tarde (14:00-22:00)'),
        ('noche', 'Noche (22:00-06:00)'),
    ]

    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name='turnos')
    fecha = models.DateField()
    turno = models.CharField(max_length=10, choices=TURNO_CHOICES)
    horas = models.DecimalField(max_digits=4, decimal_places=2, default=8)
    observaciones = models.TextField(blank=True, default='')
    creado_por = models.CharField(max_length=150, blank=True, default='')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['fecha', 'turno']
        unique_together = ['empleado', 'fecha', 'turno']

    def __str__(self):
        return f'{self.empleado.nombre_completo} - {self.fecha} - {self.get_turno_display()}'

    def to_dict(self):
        return {
            'id': self.id,
            'empleado_id': self.empleado.id,
            'empleado_nombre': self.empleado.nombre_completo,
            'departamento': self.empleado.departamento.nombre,
            'fecha': self.fecha.strftime('%Y-%m-%d'),
            'turno': self.turno,
            'turno_display': self.get_turno_display(),
            'horas': float(self.horas),
            'observaciones': self.observaciones,
        }


class Sustitucion(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('aceptada', 'Aceptada'),
        ('rechazada', 'Rechazada'),
        ('completada', 'Completada'),
    ]

    turno_original = models.ForeignKey(TurnoGuardia, on_delete=models.CASCADE, related_name='sustituciones_originales')
    empleado_sustituto = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name='sustituciones_como_sustituto')
    motivo = models.TextField()
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_respuesta = models.DateTimeField(null=True, blank=True)
    observaciones = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['-fecha_solicitud']

    def __str__(self):
        return f'{self.turno_original.empleado.nombre_completo} → {self.empleado_sustituto.nombre_completo}'

    def to_dict(self):
        return {
            'id': self.id,
            'turno_original_id': self.turno_original.id,
            'empleado_original': self.turno_original.empleado.nombre_completo,
            'empleado_sustituto_id': self.empleado_sustituto.id,
            'empleado_sustituto_nombre': self.empleado_sustituto.nombre_completo,
            'fecha_turno': self.turno_original.fecha.strftime('%Y-%m-%d'),
            'turno_display': self.turno_original.get_turno_display(),
            'motivo': self.motivo,
            'estado': self.estado,
            'estado_display': self.get_estado_display(),
            'observaciones': self.observaciones,
        }
