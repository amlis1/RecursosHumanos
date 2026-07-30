from django.contrib import admin
from .models import Departamento, Empleado, SolicitudPermiso, TurnoGuardia, Sustitucion

@admin.register(Departamento)
class DepartamentoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'jefe_departamento', 'fecha_creacion')
    search_fields = ('nombre',)

@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ('cedula', 'nombres', 'apellidos', 'departamento', 'cargo', 'estado')
    list_filter = ('departamento', 'estado')
    search_fields = ('cedula', 'nombres', 'apellidos')

@admin.register(SolicitudPermiso)
class SolicitudPermisoAdmin(admin.ModelAdmin):
    list_display = ('empleado', 'tipo', 'fecha_inicio', 'fecha_fin', 'dias_solicitados', 'estado')
    list_filter = ('estado', 'tipo')
    search_fields = ('empleado__nombres', 'empleado__apellidos')

@admin.register(TurnoGuardia)
class TurnoGuardiaAdmin(admin.ModelAdmin):
    list_display = ('empleado', 'fecha', 'turno', 'horas')
    list_filter = ('turno', 'fecha')

@admin.register(Sustitucion)
class SustitucionAdmin(admin.ModelAdmin):
    list_display = ('turno_original', 'empleado_sustituto', 'estado', 'fecha_solicitud')
    list_filter = ('estado',)
