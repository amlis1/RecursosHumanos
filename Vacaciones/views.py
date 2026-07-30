from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout, authenticate, login as auth_login
from django.contrib.auth.models import User, Group
from django.contrib.auth.views import LoginView
from django.utils import timezone
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from functools import wraps
import json
from datetime import datetime, date, timedelta
from io import BytesIO
from django.db.models import Q, Count, Sum
from .models import Departamento, Empleado, SolicitudPermiso, TurnoGuardia, Sustitucion
import os
import base64
import resend

class CustomLoginView(LoginView):
    template_name = 'registration/login.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        self.request.session['show_welcome'] = True
        return response


@require_GET
def clear_welcome_flag(request):
    request.session.pop('show_welcome', None)
    return JsonResponse({'success': True})


def tutorial_pasos(request):
    es_admin = request.user.is_authenticated and (request.user.is_superuser or request.user.is_staff)
    pasos = []
    pasos.append({
        'element': '#navigation',
        'popover': {
            'title': 'Menú de navegación',
            'description': 'Aquí puedes acceder a todas las secciones del sistema.',
            'side': 'bottom',
            'align': 'start',
        }
    })
    if es_admin:
        pasos.append({
            'element': '#nav-dashboard a',
            'popover': {
                'title': 'Dashboard',
                'description': 'Resumen general con estadísticas de empleados, permisos y ausentismo.',
                'side': 'bottom',
                'align': 'start',
            }
        })
        pasos.append({
            'element': '#nav-empleados a',
            'popover': {
                'title': 'Empleados',
                'description': 'Gestiona todos los empleados: crear, editar y eliminar registros.',
                'side': 'bottom',
                'align': 'start',
            }
        })
        pasos.append({
            'element': '#nav-departamentos a',
            'popover': {
                'title': 'Departamentos',
                'description': 'Administra los departamentos de la organización.',
                'side': 'bottom',
                'align': 'start',
            }
        })
    pasos.append({
        'element': '#nav-permisos a',
        'popover': {
            'title': 'Permisos',
            'description': 'Solicita y gestiona permisos, vacaciones y licencias.',
            'side': 'bottom',
            'align': 'start',
        }
    })
    pasos.append({
        'element': '#nav-turnos a',
        'popover': {
            'title': 'Turnos',
            'description': 'Asigna y administra turnos de guardia.',
            'side': 'bottom',
            'align': 'start',
        }
    })
    pasos.append({
        'element': '#nav-sustituciones a',
        'popover': {
            'title': 'Sustituciones',
            'description': 'Gestiona sustituciones de turnos entre empleados.',
            'side': 'bottom',
            'align': 'start',
        }
    })
    pasos.append({
        'element': '#nav-calendario a',
        'popover': {
            'title': 'Calendario',
            'description': 'Visualiza todos los turnos y permisos en un calendario.',
            'side': 'bottom',
            'align': 'start',
        }
    })
    if es_admin:
        pasos.append({
            'element': '#nav-reportes a',
            'popover': {
                'title': 'Reportes',
                'description': 'Genera y exporta reportes en PDF, envíalos por correo.',
                'side': 'bottom',
                'align': 'start',
            }
        })
    pasos.append({
        'element': 'main',
        'popover': {
            'title': 'Contenido principal',
            'description': 'Aquí se muestra la información y los formularios de cada sección.',
            'side': 'top',
            'align': 'center',
        }
    })
    return JsonResponse({'pasos': pasos, 'total': len(pasos)})


def es_admin(user):
    return user.is_authenticated and (user.is_superuser or user.is_staff or user.groups.filter(name='Admin').exists())

def validar_cedula(cedula):
    if not cedula or len(cedula) != 10 or not cedula.isdigit():
        return False
    provincia = int(cedula[:2])
    if provincia < 1 or provincia > 24:
        return False
    digito_verificador = int(cedula[9])
    coeficientes = [2, 1, 2, 1, 2, 1, 2, 1, 2]
    suma = 0
    for i in range(9):
        digito = int(cedula[i]) * coeficientes[i]
        if digito > 9:
            digito -= 9
        suma += digito
    residuo = suma % 10
    return (10 - residuo) % 10 == digito_verificador

def es_empleado(user):
    return user.is_authenticated and user.groups.filter(name='Empleado').exists()

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not es_admin(request.user):
            return redirect('Vacaciones:index')
        return view_func(request, *args, **kwargs)
    return _wrapped

def empleado_o_admin_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not (es_admin(request.user) or es_empleado(request.user)):
            return redirect('Vacaciones:index')
        return view_func(request, *args, **kwargs)
    return _wrapped

try:
    from xhtml2pdf import pisa
except ImportError:
    pisa = None

from django.conf import settings
EMAIL_HOST_USER = settings.EMAIL_HOST_USER


# ─── Index & Auth ─────────────────────────────────────────────────────────────

def index(request):
    if request.user.is_authenticated:
        if es_admin(request.user):
            return redirect('Vacaciones:dashboard')
        return redirect('Vacaciones:permisos_lista')
    return render(request, 'index.html')


@csrf_exempt
def register(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
            username = data.get('username', '').strip()
            email = data.get('email', '').strip()
            password = data.get('password', '')
            password_confirm = data.get('password_confirm', '')
            rol = data.get('rol', 'empleado').strip().lower()

            nombres = data.get('nombres', '').strip()
            apellidos = data.get('apellidos', '').strip()
            cedula = data.get('cedula', '').strip()
            departamento_id = data.get('departamento_id')
            telefono = data.get('telefono', '').strip()
            fecha_nacimiento = data.get('fecha_nacimiento', '').strip()

            if not username or not email or not password:
                return JsonResponse({'success': False, 'error': 'Todos los campos son obligatorios'}, status=400)
            if password != password_confirm:
                return JsonResponse({'success': False, 'error': 'Las contraseñas no coinciden'}, status=400)
            if len(password) < 6:
                return JsonResponse({'success': False, 'error': 'La contraseña debe tener al menos 6 caracteres'}, status=400)
            if rol not in ('admin', 'empleado'):
                return JsonResponse({'success': False, 'error': 'Rol inválido'}, status=400)

            if User.objects.filter(username=username).exists():
                return JsonResponse({'success': False, 'error': 'El nombre de usuario ya existe'}, status=400)
            if User.objects.filter(email=email).exists():
                return JsonResponse({'success': False, 'error': 'El correo ya está registrado'}, status=400)

            if rol == 'empleado':
                if not nombres or not apellidos or not cedula or not departamento_id:
                    return JsonResponse({'success': False, 'error': 'Para registrarse como empleado, complete nombres, apellidos, cédula y departamento'}, status=400)
                if not validar_cedula(cedula):
                    return JsonResponse({'success': False, 'error': 'La cédula ingresada no es válida según el registro civil ecuatoriano'}, status=400)
                if Empleado.objects.filter(cedula=cedula).exists():
                    return JsonResponse({'success': False, 'error': 'Ya existe un empleado con esa cédula'}, status=400)

            user = User.objects.create_user(username=username, email=email, password=password)

            if rol == 'admin':
                user.is_staff = True
                user.save()
                admin_group = Group.objects.get_or_create(name='Admin')[0]
                user.groups.add(admin_group)
            else:
                empleado_group = Group.objects.get_or_create(name='Empleado')[0]
                user.groups.add(empleado_group)

                fn = None
                if fecha_nacimiento:
                    try:
                        fn = datetime.strptime(fecha_nacimiento, '%Y-%m-%d').date()
                    except ValueError:
                        pass

                depto = get_object_or_404(Departamento, id=departamento_id)
                empleado = Empleado.objects.create(
                    cedula=cedula,
                    nombres=nombres,
                    apellidos=apellidos,
                    email=email,
                    telefono=telefono,
                    fecha_nacimiento=fn,
                    departamento=depto,
                    cargo='',
                    fecha_ingreso=date.today(),
                    estado='activo',
                    user=user,
                )

            user_auth = authenticate(request, username=username, password=password)
            if user_auth:
                auth_login(request, user_auth)

            redirect_url = '/dashboard/' if rol == 'admin' else '/permisos/'
            return JsonResponse({'success': True, 'redirect': redirect_url})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return redirect('login')


@csrf_exempt
def custom_logout(request):
    if request.method == 'POST':
        auth_logout(request)
    return redirect('Vacaciones:index')


# ─── Dashboard ────────────────────────────────────────────────────────────────

@login_required(login_url='login')
@admin_required
def dashboard(request):
    total_empleados = Empleado.objects.count()
    total_departamentos = Departamento.objects.count()
    permisos_pendientes = SolicitudPermiso.objects.filter(estado='pendiente').count()
    total_ausencias = Empleado.objects.filter(estado__in=['vacaciones', 'licencia']).count()

    empleados_por_departamento = list(
        Departamento.objects.annotate(cantidad=Count('empleados'))
        .values('nombre', 'cantidad')
    )

    ausentismo_data = []
    for dept in Departamento.objects.all():
        total = dept.empleados.count()
        ausentes = dept.empleados.filter(estado__in=['vacaciones', 'licencia']).count()
        porcentaje = round((ausentes / total * 100), 1) if total > 0 else 0
        ausentismo_data.append({
            'nombre': dept.nombre,
            'porcentaje': porcentaje,
        })

    vacaciones_data = list(
        Empleado.objects.filter(estado='activo')
        .values('nombres', 'apellidos')
        .annotate(
            dias_vacaciones_pendientes=Sum('dias_vacaciones_pendientes'),
            dias_vacaciones_tomados=Sum('dias_vacaciones_tomados')
        )
    )

    context = {
        'total_empleados': total_empleados,
        'total_departamentos': total_departamentos,
        'permisos_pendientes': permisos_pendientes,
        'total_ausencias': total_ausencias,
        'empleados_por_departamento': json.dumps(empleados_por_departamento),
        'ausentismo_data': json.dumps(ausentismo_data),
        'vacaciones_data': json.dumps(vacaciones_data),
    }
    return render(request, 'Vacaciones/dashboard.html', context)


# ─── Empleados ────────────────────────────────────────────────────────────────

@login_required(login_url='login')
@admin_required
def empleados_lista(request):
    empleados_list = Empleado.objects.select_related('departamento').all()
    return render(request, 'Vacaciones/empleados.html', {'empleados_list': empleados_list})


@csrf_exempt
@login_required(login_url='login')
@admin_required
def empleado_crear(request):
    if request.method == 'POST':
        try:
            if request.content_type == 'application/json' or request.body.startswith(b'{'):
                data = json.loads(request.body)
            else:
                data = request.POST
        except Exception:
            return JsonResponse({'success': False, 'error': 'Datos inválidos'}, status=400)

        try:
            cedula = data.get('cedula', '').strip()
            nombres = data.get('nombres', '').strip()
            apellidos = data.get('apellidos', '').strip()
            email = data.get('email', '').strip()
            telefono = data.get('telefono', '').strip()
            fecha_nacimiento = data.get('fecha_nacimiento', '').strip()
            genero = data.get('genero', '').strip()
            direccion = data.get('direccion', '').strip()
            departamento_id = data.get('departamento_id')
            cargo = data.get('cargo', '').strip()
            fecha_ingreso = data.get('fecha_ingreso', '').strip()
            salario = data.get('salario', 0)
            estado = data.get('estado', 'activo').strip()

            if not cedula or not nombres or not apellidos or not email or not departamento_id or not fecha_ingreso:
                return JsonResponse({'success': False, 'error': 'Campos obligatorios incompletos'}, status=400)
            if not validar_cedula(cedula):
                return JsonResponse({'success': False, 'error': 'La cédula ingresada no es válida según el registro civil ecuatoriano'}, status=400)

            departamento = get_object_or_404(Departamento, id=departamento_id)

            fn = None
            if fecha_nacimiento:
                try:
                    fn = datetime.strptime(fecha_nacimiento, '%Y-%m-%d').date()
                except ValueError:
                    return JsonResponse({'success': False, 'error': 'Fecha de nacimiento inválida'}, status=400)

            fi = datetime.strptime(fecha_ingreso, '%Y-%m-%d').date()

            empleado = Empleado(
                cedula=cedula,
                nombres=nombres,
                apellidos=apellidos,
                email=email,
                telefono=telefono,
                fecha_nacimiento=fn,
                genero=genero,
                direccion=direccion,
                departamento=departamento,
                cargo=cargo,
                fecha_ingreso=fi,
                salario=salario,
                estado=estado,
            )
            empleado.save()
            return JsonResponse({'success': True, 'message': 'Empleado creado exitosamente', 'empleado': empleado.to_dict()})
        except ValueError as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    departamentos = Departamento.objects.all()
    return render(request, 'Vacaciones/empleado_crear.html', {'departamentos': departamentos})


@csrf_exempt
@login_required(login_url='login')
@admin_required
def empleado_editar(request, pk):
    empleado = get_object_or_404(Empleado, id=pk)

    if request.method == 'POST':
        try:
            if request.content_type == 'application/json' or request.body.startswith(b'{'):
                data = json.loads(request.body)
            else:
                data = request.POST
        except Exception:
            return JsonResponse({'success': False, 'error': 'Datos inválidos'}, status=400)

        try:
            new_cedula = data.get('cedula', '').strip() or empleado.cedula
            if new_cedula != empleado.cedula and not validar_cedula(new_cedula):
                return JsonResponse({'success': False, 'error': 'La cédula ingresada no es válida según el registro civil ecuatoriano'}, status=400)
            empleado.cedula = new_cedula
            empleado.nombres = data.get('nombres', empleado.nombres).strip()
            empleado.apellidos = data.get('apellidos', empleado.apellidos).strip()
            empleado.email = data.get('email', empleado.email).strip()
            empleado.telefono = data.get('telefono', empleado.telefono).strip()
            empleado.direccion = data.get('direccion', empleado.direccion).strip()
            empleado.cargo = data.get('cargo', empleado.cargo).strip()
            empleado.estado = data.get('estado', empleado.estado).strip()
            empleado.genero = data.get('genero', empleado.genero).strip()

            fn = data.get('fecha_nacimiento', '')
            if fn:
                try:
                    empleado.fecha_nacimiento = datetime.strptime(fn.strip(), '%Y-%m-%d').date()
                except ValueError:
                    return JsonResponse({'success': False, 'error': 'Fecha de nacimiento inválida'}, status=400)

            fi = data.get('fecha_ingreso', '')
            if fi:
                try:
                    empleado.fecha_ingreso = datetime.strptime(fi.strip(), '%Y-%m-%d').date()
                except ValueError:
                    return JsonResponse({'success': False, 'error': 'Fecha de ingreso inválida'}, status=400)

            dep_id = data.get('departamento_id')
            if dep_id:
                empleado.departamento = get_object_or_404(Departamento, id=dep_id)

            sal = data.get('salario')
            if sal is not None:
                empleado.salario = sal

            empleado.save()
            return JsonResponse({'success': True, 'message': 'Empleado actualizado', 'empleado': empleado.to_dict()})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    departamentos = Departamento.objects.all()
    return render(request, 'Vacaciones/empleado_editar.html', {'empleado': empleado, 'departamentos': departamentos})


@csrf_exempt
@login_required(login_url='login')
@admin_required
def empleado_eliminar(request, pk):
    if request.method == 'DELETE':
        empleado = get_object_or_404(Empleado, id=pk)
        empleado.delete()
        return JsonResponse({'success': True, 'message': 'Empleado eliminado'})
    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)


# ─── Departamentos ────────────────────────────────────────────────────────────

@login_required(login_url='login')
@admin_required
def departamentos_lista(request):
    departamentos_list = Departamento.objects.all()
    return render(request, 'Vacaciones/departamentos.html', {'departamentos_list': departamentos_list})


@csrf_exempt
@login_required(login_url='login')
@admin_required
def departamento_crear(request):
    if request.method == 'POST':
        try:
            if request.content_type == 'application/json' or request.body.startswith(b'{'):
                data = json.loads(request.body)
            else:
                data = request.POST
        except Exception:
            return JsonResponse({'success': False, 'error': 'Datos inválidos'}, status=400)

        nombre = data.get('nombre', '').strip()
        descripcion = data.get('descripcion', '').strip()
        jefe_departamento = data.get('jefe_departamento', '').strip()

        if not nombre:
            return JsonResponse({'success': False, 'error': 'El nombre es obligatorio'}, status=400)

        if Departamento.objects.filter(nombre=nombre).exists():
            return JsonResponse({'success': False, 'error': 'Ya existe un departamento con ese nombre'}, status=400)

        dept = Departamento.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            jefe_departamento=jefe_departamento,
        )
        return JsonResponse({'success': True, 'message': 'Departamento creado', 'departamento': dept.to_dict()})

    return render(request, 'Vacaciones/departamento_crear.html')


@csrf_exempt
@login_required(login_url='login')
@admin_required
def departamento_editar(request, pk):
    dept = get_object_or_404(Departamento, id=pk)

    if request.method == 'POST':
        try:
            if request.content_type == 'application/json' or request.body.startswith(b'{'):
                data = json.loads(request.body)
            else:
                data = request.POST
        except Exception:
            return JsonResponse({'success': False, 'error': 'Datos inválidos'}, status=400)

        nombre = data.get('nombre', '').strip()
        if not nombre:
            return JsonResponse({'success': False, 'error': 'El nombre es obligatorio'}, status=400)

        if Departamento.objects.filter(nombre=nombre).exclude(id=pk).exists():
            return JsonResponse({'success': False, 'error': 'Ya existe otro departamento con ese nombre'}, status=400)

        dept.nombre = nombre
        dept.descripcion = data.get('descripcion', dept.descripcion).strip()
        dept.jefe_departamento = data.get('jefe_departamento', dept.jefe_departamento).strip()
        dept.save()
        return JsonResponse({'success': True, 'message': 'Departamento actualizado', 'departamento': dept.to_dict()})

    return render(request, 'Vacaciones/departamento_editar.html', {'departamento': dept})


@csrf_exempt
@login_required(login_url='login')
@admin_required
def departamento_eliminar(request, pk):
    if request.method == 'DELETE':
        dept = get_object_or_404(Departamento, id=pk)
        if dept.empleados.exists():
            return JsonResponse({'success': False, 'error': 'No se puede eliminar: tiene empleados asignados'}, status=400)
        dept.delete()
        return JsonResponse({'success': True, 'message': 'Departamento eliminado'})
    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)


# ─── Permisos / Solicitudes ──────────────────────────────────────────────────

@login_required(login_url='login')
def permisos_lista(request):
    if es_admin(request.user):
        permisos_list = SolicitudPermiso.objects.select_related('empleado').all()
    else:
        emp = request.user.empleado if hasattr(request.user, 'empleado') else None
        permisos_list = SolicitudPermiso.objects.filter(empleado=emp).select_related('empleado').all() if emp else SolicitudPermiso.objects.none()
    return render(request, 'Vacaciones/permisos.html', {'permisos_list': permisos_list})


@csrf_exempt
@login_required(login_url='login')
def permiso_crear(request):
    if request.method == 'POST':
        try:
            if request.content_type == 'application/json' or request.body.startswith(b'{'):
                data = json.loads(request.body)
            else:
                data = request.POST
        except Exception:
            return JsonResponse({'success': False, 'error': 'Datos inválidos'}, status=400)

        try:
            if not es_admin(request.user):
                emp = request.user.empleado if hasattr(request.user, 'empleado') else None
                if not emp:
                    return JsonResponse({'success': False, 'error': 'No tienes un perfil de empleado vinculado'}, status=400)
                empleado_id = emp.id
            else:
                empleado_id = data.get('empleado_id')
            tipo = data.get('tipo', '').strip()
            motivo = data.get('motivo', '').strip()
            fecha_inicio = data.get('fecha_inicio', '').strip()
            fecha_fin = data.get('fecha_fin', '').strip()
            dias_solicitados = data.get('dias_solicitados')
            observaciones = data.get('observaciones', '').strip()

            if not empleado_id or not tipo or not motivo or not fecha_inicio or not fecha_fin or not dias_solicitados:
                return JsonResponse({'success': False, 'error': 'Campos obligatorios incompletos'}, status=400)

            empleado = get_object_or_404(Empleado, id=empleado_id)
            fi = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            ff = datetime.strptime(fecha_fin, '%Y-%m-%d').date()

            tomorrow = date.today() + timedelta(days=1)
            if fi < tomorrow:
                return JsonResponse({'success': False, 'error': 'La fecha de inicio debe ser a partir de mañana'}, status=400)
            if ff < tomorrow:
                return JsonResponse({'success': False, 'error': 'La fecha fin debe ser a partir de mañana'}, status=400)

            if ff < fi:
                return JsonResponse({'success': False, 'error': 'La fecha fin no puede ser anterior a la fecha inicio'}, status=400)

            permiso = SolicitudPermiso(
                empleado=empleado,
                tipo=tipo,
                motivo=motivo,
                fecha_inicio=fi,
                fecha_fin=ff,
                dias_solicitados=int(dias_solicitados),
                observaciones=observaciones,
            )
            permiso.save()
            return JsonResponse({'success': True, 'message': 'Permiso creado', 'permiso': permiso.to_dict()})
        except ValueError as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    emp = request.user.empleado if hasattr(request.user, 'empleado') else None
    empleados = Empleado.objects.all() if es_admin(request.user) else [emp] if emp else []
    tipo_choices = SolicitudPermiso.TIPO_CHOICES
    return render(request, 'Vacaciones/permiso_crear.html', {
        'empleados': empleados,
        'tipo_choices': tipo_choices,
        'es_admin': es_admin(request.user),
        'mi_empleado': emp,
    })


@csrf_exempt
@login_required(login_url='login')
def permiso_editar(request, pk):
    permiso = get_object_or_404(SolicitudPermiso, id=pk)

    if request.method == 'POST':
        try:
            if request.content_type == 'application/json' or request.body.startswith(b'{'):
                data = json.loads(request.body)
            else:
                data = request.POST
        except Exception:
            return JsonResponse({'success': False, 'error': 'Datos inválidos'}, status=400)

        try:
            if permiso.estado != 'pendiente':
                return JsonResponse({'success': False, 'error': 'Solo se pueden editar permisos pendientes'}, status=400)

            empleado_id = data.get('empleado_id')
            if empleado_id:
                permiso.empleado = get_object_or_404(Empleado, id=empleado_id)

            permiso.tipo = data.get('tipo', permiso.tipo).strip()
            permiso.motivo = data.get('motivo', permiso.motivo).strip()
            permiso.observaciones = data.get('observaciones', permiso.observaciones).strip()

            fi = data.get('fecha_inicio')
            if fi:
                permiso.fecha_inicio = datetime.strptime(fi.strip(), '%Y-%m-%d').date()

            ff = data.get('fecha_fin')
            if ff:
                permiso.fecha_fin = datetime.strptime(ff.strip(), '%Y-%m-%d').date()

            dias = data.get('dias_solicitados')
            if dias is not None:
                permiso.dias_solicitados = int(dias)

            tomorrow = date.today() + timedelta(days=1)
            if permiso.fecha_inicio < tomorrow:
                return JsonResponse({'success': False, 'error': 'La fecha de inicio debe ser a partir de mañana'}, status=400)
            if permiso.fecha_fin < tomorrow:
                return JsonResponse({'success': False, 'error': 'La fecha fin debe ser a partir de mañana'}, status=400)

            if permiso.fecha_fin < permiso.fecha_inicio:
                return JsonResponse({'success': False, 'error': 'La fecha fin no puede ser anterior a la fecha inicio'}, status=400)

            permiso.save()
            return JsonResponse({'success': True, 'message': 'Permiso actualizado', 'permiso': permiso.to_dict()})
        except ValueError as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    if es_admin(request.user):
        empleados = Empleado.objects.all()
    else:
        emp = request.user.empleado if hasattr(request.user, 'empleado') else None
        empleados = [emp] if emp else []
    tipo_choices = SolicitudPermiso.TIPO_CHOICES
    return render(request, 'Vacaciones/permiso_editar.html', {'permiso': permiso, 'empleados': empleados, 'tipo_choices': tipo_choices})


@csrf_exempt
@login_required(login_url='login')
def permiso_eliminar(request, pk):
    if request.method == 'DELETE':
        permiso = get_object_or_404(SolicitudPermiso, id=pk)
        permiso.delete()
        return JsonResponse({'success': True, 'message': 'Permiso eliminado'})
    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)


@csrf_exempt
@login_required(login_url='login')
def permiso_aprobar(request, pk):
    if request.method == 'POST':
        permiso = get_object_or_404(SolicitudPermiso, id=pk)

        if permiso.estado != 'pendiente':
            return JsonResponse({'success': False, 'error': 'Este permiso ya fue procesado'}, status=400)

        permiso.estado = 'aprobado'
        permiso.fecha_respuesta = timezone.now()
        permiso.save()

        if permiso.tipo == 'vacaciones':
            emp = permiso.empleado
            emp.dias_vacaciones_pendientes = max(0, emp.dias_vacaciones_pendientes - permiso.dias_solicitados)
            emp.dias_vacaciones_tomados += permiso.dias_solicitados
            emp.save()

        return JsonResponse({'success': True, 'message': 'Permiso aprobado', 'permiso': permiso.to_dict()})

    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)


@csrf_exempt
@login_required(login_url='login')
def permiso_rechazar(request, pk):
    if request.method == 'POST':
        permiso = get_object_or_404(SolicitudPermiso, id=pk)

        if permiso.estado != 'pendiente':
            return JsonResponse({'success': False, 'error': 'Este permiso ya fue procesado'}, status=400)

        try:
            data = json.loads(request.body)
            observaciones = data.get('observaciones', '').strip()
        except json.JSONDecodeError:
            observaciones = ''

        if observaciones:
            permiso.observaciones = observaciones

        permiso.estado = 'rechazado'
        permiso.fecha_respuesta = timezone.now()
        permiso.save()

        return JsonResponse({'success': True, 'message': 'Permiso rechazado', 'permiso': permiso.to_dict()})

    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)


@csrf_exempt
@login_required(login_url='login')
def permiso_aprobar_masivo(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'JSON inválido'}, status=400)

        ids = data.get('ids', [])
        if not ids:
            return JsonResponse({'success': False, 'error': 'No se proporcionaron IDs'}, status=400)

        aprobados = 0
        errores = []

        for permiso_id in ids:
            try:
                permiso = SolicitudPermiso.objects.get(id=permiso_id)
                if permiso.estado != 'pendiente':
                    errores.append(f'Permiso {permiso_id}: ya fue procesado')
                    continue

                permiso.estado = 'aprobado'
                permiso.fecha_respuesta = timezone.now()
                permiso.save()

                if permiso.tipo == 'vacaciones':
                    emp = permiso.empleado
                    emp.dias_vacaciones_pendientes = max(0, emp.dias_vacaciones_pendientes - permiso.dias_solicitados)
                    emp.dias_vacaciones_tomados += permiso.dias_solicitados
                    emp.save()

                aprobados += 1
            except SolicitudPermiso.DoesNotExist:
                errores.append(f'Permiso {permiso_id}: no encontrado')

        return JsonResponse({
            'success': True,
            'message': f'{aprobados} permiso(s) aprobado(s)',
            'aprobados': aprobados,
            'errores': errores,
        })

    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)


# ─── Turnos de Guardia ───────────────────────────────────────────────────────

@login_required(login_url='login')
def turnos_lista(request):
    if es_admin(request.user):
        turnos_list = TurnoGuardia.objects.select_related('empleado').all()
    else:
        emp = request.user.empleado if hasattr(request.user, 'empleado') else None
        turnos_list = TurnoGuardia.objects.filter(empleado=emp).select_related('empleado').all() if emp else TurnoGuardia.objects.none()
    return render(request, 'Vacaciones/turnos.html', {'turnos_list': turnos_list})


@csrf_exempt
@login_required(login_url='login')
def turno_crear(request):
    if not es_admin(request.user):
        return redirect('Vacaciones:turnos_lista')
    if request.method == 'POST':
        try:
            if request.content_type == 'application/json' or request.body.startswith(b'{'):
                data = json.loads(request.body)
            else:
                data = request.POST
        except Exception:
            return JsonResponse({'success': False, 'error': 'Datos inválidos'}, status=400)

        try:
            empleado_id = data.get('empleado_id')
            fecha_str = data.get('fecha', '').strip()
            turno = data.get('turno', '').strip()
            horas = data.get('horas', 8)
            observaciones = data.get('observaciones', '').strip()
            creado_por = data.get('creado_por', '').strip()

            if not empleado_id or not fecha_str or not turno:
                return JsonResponse({'success': False, 'error': 'Campos obligatorios incompletos'}, status=400)

            empleado = get_object_or_404(Empleado, id=empleado_id)
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()

            if fecha < date.today():
                return JsonResponse({'success': False, 'error': 'La fecha del turno debe ser a partir de hoy'}, status=400)

            if TurnoGuardia.objects.filter(empleado=empleado, fecha=fecha, turno=turno).exists():
                return JsonResponse({'success': False, 'error': 'Este empleado ya tiene un turno asignado en esa fecha y horario'}, status=400)

            if SolicitudPermiso.objects.filter(
                empleado=empleado, estado='aprobado',
                fecha_inicio__lte=fecha, fecha_fin__gte=fecha
            ).exists():
                return JsonResponse({'success': False, 'error': 'El empleado tiene un permiso aprobado que cubre esta fecha'}, status=400)

            turno_obj = TurnoGuardia(
                empleado=empleado,
                fecha=fecha,
                turno=turno,
                horas=horas,
                observaciones=observaciones,
                creado_por=creado_por,
            )
            turno_obj.save()
            return JsonResponse({'success': True, 'message': 'Turno creado', 'turno': turno_obj.to_dict()})
        except ValueError as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    empleados = Empleado.objects.all()
    turno_choices = TurnoGuardia.TURNO_CHOICES
    return render(request, 'Vacaciones/turno_crear.html', {'empleados': empleados, 'turno_choices': turno_choices})


@csrf_exempt
@login_required(login_url='login')
def turno_editar(request, pk):
    turno = get_object_or_404(TurnoGuardia, id=pk)

    if request.method == 'POST':
        try:
            if request.content_type == 'application/json' or request.body.startswith(b'{'):
                data = json.loads(request.body)
            else:
                data = request.POST
        except Exception:
            return JsonResponse({'success': False, 'error': 'Datos inválidos'}, status=400)

        try:
            empleado_id = data.get('empleado_id')
            if empleado_id:
                turno.empleado = get_object_or_404(Empleado, id=empleado_id)

            fecha_str = data.get('fecha')
            if fecha_str:
                turno.fecha = datetime.strptime(fecha_str.strip(), '%Y-%m-%d').date()
                if turno.fecha < date.today():
                    return JsonResponse({'success': False, 'error': 'La fecha del turno debe ser a partir de hoy'}, status=400)

            new_turno = data.get('turno')
            if new_turno:
                turno.turno = new_turno.strip()

            horas = data.get('horas')
            if horas is not None:
                turno.horas = horas

            turno.observaciones = data.get('observaciones', turno.observaciones).strip()
            turno.creado_por = data.get('creado_por', turno.creado_por).strip()

            conflict = TurnoGuardia.objects.filter(
                empleado=turno.empleado, fecha=turno.fecha, turno=turno.turno
            ).exclude(id=pk)

            if conflict.exists():
                return JsonResponse({'success': False, 'error': 'Conflicto: el empleado ya tiene ese turno en esa fecha'}, status=400)

            if SolicitudPermiso.objects.filter(
                empleado=turno.empleado, estado='aprobado',
                fecha_inicio__lte=turno.fecha, fecha_fin__gte=turno.fecha
            ).exists():
                return JsonResponse({'success': False, 'error': 'El empleado tiene un permiso aprobado que cubre esta fecha'}, status=400)

            turno.save()
            return JsonResponse({'success': True, 'message': 'Turno actualizado', 'turno': turno.to_dict()})
        except ValueError as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    if es_admin(request.user):
        empleados = Empleado.objects.all()
    else:
        emp = request.user.empleado if hasattr(request.user, 'empleado') else None
        empleados = [emp] if emp else []
    turno_choices = TurnoGuardia.TURNO_CHOICES
    return render(request, 'Vacaciones/turno_editar.html', {'turno': turno, 'empleados': empleados, 'turno_choices': turno_choices})


@csrf_exempt
@login_required(login_url='login')
def turno_eliminar(request, pk):
    if request.method == 'DELETE':
        turno = get_object_or_404(TurnoGuardia, id=pk)
        turno.delete()
        return JsonResponse({'success': True, 'message': 'Turno eliminado'})
    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)


@csrf_exempt
@login_required(login_url='login')
def turno_intercambiar(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'JSON inválido'}, status=400)

        try:
            turno_id_1 = data.get('turno_id_1')
            turno_id_2 = data.get('turno_id_2')
            motivo = data.get('motivo', 'Intercambio de turno').strip()

            if not turno_id_1 or not turno_id_2:
                return JsonResponse({'success': False, 'error': 'Se requieren dos turnos para intercambiar'}, status=400)

            if turno_id_1 == turno_id_2:
                return JsonResponse({'success': False, 'error': 'No se puede intercambiar un turno consigo mismo'}, status=400)

            t1 = get_object_or_404(TurnoGuardia, id=turno_id_1)
            t2 = get_object_or_404(TurnoGuardia, id=turno_id_2)

            emp1 = t1.empleado
            emp2 = t2.empleado

            t1.empleado = emp2
            t2.empleado = emp1
            t1.save()
            t2.save()

            Sustitucion.objects.create(
                turno_original=t1,
                empleado_sustituto=emp1,
                motivo=motivo,
                estado='completada',
            )

            return JsonResponse({
                'success': True,
                'message': 'Turnos intercambiados exitosamente',
                'turno_1': t1.to_dict(),
                'turno_2': t2.to_dict(),
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)


# ─── Sustituciones ────────────────────────────────────────────────────────────

@login_required(login_url='login')
def sustituciones_lista(request):
    if es_admin(request.user):
        sustituciones_list = Sustitucion.objects.select_related('turno_original__empleado', 'empleado_sustituto').all()
    else:
        emp = request.user.empleado if hasattr(request.user, 'empleado') else None
        if emp:
            sustituciones_list = Sustitucion.objects.filter(
                Q(turno_original__empleado=emp) | Q(empleado_sustituto=emp)
            ).select_related('turno_original__empleado', 'empleado_sustituto').all()
        else:
            sustituciones_list = Sustitucion.objects.none()
    return render(request, 'Vacaciones/sustituciones.html', {'sustituciones_list': sustituciones_list})


@csrf_exempt
@login_required(login_url='login')
def sustitucion_crear(request):
    if not es_admin(request.user):
        return redirect('Vacaciones:sustituciones_lista')
    if request.method == 'POST':
        try:
            if request.content_type == 'application/json' or request.body.startswith(b'{'):
                data = json.loads(request.body)
            else:
                data = request.POST
        except Exception:
            return JsonResponse({'success': False, 'error': 'Datos inválidos'}, status=400)

        try:
            turno_id = data.get('turno_original_id')
            empleado_sustituto_id = data.get('empleado_sustituto_id')
            motivo = data.get('motivo', '').strip()
            observaciones = data.get('observaciones', '').strip()

            if not turno_id or not empleado_sustituto_id or not motivo:
                return JsonResponse({'success': False, 'error': 'Campos obligatorios incompletos'}, status=400)

            turno = get_object_or_404(TurnoGuardia, id=turno_id)
            sustituto = get_object_or_404(Empleado, id=empleado_sustituto_id)

            sust = Sustitucion(
                turno_original=turno,
                empleado_sustituto=sustituto,
                motivo=motivo,
                observaciones=observaciones,
            )
            sust.save()
            return JsonResponse({'success': True, 'message': 'Sustitución creada', 'sustitucion': sust.to_dict()})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    turnos = TurnoGuardia.objects.select_related('empleado').all()
    empleados = Empleado.objects.all()
    return render(request, 'Vacaciones/sustitucion_crear.html', {'turnos': turnos, 'empleados': empleados})


@csrf_exempt
@login_required(login_url='login')
def sustitucion_editar(request, pk):
    sust = get_object_or_404(Sustitucion, id=pk)

    if request.method == 'POST':
        try:
            if request.content_type == 'application/json' or request.body.startswith(b'{'):
                data = json.loads(request.body)
            else:
                data = request.POST
        except Exception:
            return JsonResponse({'success': False, 'error': 'Datos inválidos'}, status=400)

        try:
            if sust.estado not in ('pendiente',):
                return JsonResponse({'success': False, 'error': 'Solo se pueden editar sustituciones pendientes'}, status=400)

            turno_id = data.get('turno_original_id')
            if turno_id:
                sust.turno_original = get_object_or_404(TurnoGuardia, id=turno_id)

            sustituto_id = data.get('empleado_sustituto_id')
            if sustituto_id:
                sust.empleado_sustituto = get_object_or_404(Empleado, id=sustituto_id)

            sust.motivo = data.get('motivo', sust.motivo).strip()
            sust.observaciones = data.get('observaciones', sust.observaciones).strip()

            sust.save()
            return JsonResponse({'success': True, 'message': 'Sustitución actualizada', 'sustitucion': sust.to_dict()})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    if es_admin(request.user):
        turnos = TurnoGuardia.objects.select_related('empleado').all()
        empleados = Empleado.objects.all()
    else:
        emp = request.user.empleado if hasattr(request.user, 'empleado') else None
        turnos = TurnoGuardia.objects.filter(empleado=emp).select_related('empleado').all() if emp else TurnoGuardia.objects.none()
        empleados = [emp] if emp else []
    return render(request, 'Vacaciones/sustitucion_editar.html', {'sustitucion': sust, 'turnos': turnos, 'empleados': empleados})


@csrf_exempt
@login_required(login_url='login')
def sustitucion_eliminar(request, pk):
    if request.method == 'DELETE':
        sust = get_object_or_404(Sustitucion, id=pk)
        sust.delete()
        return JsonResponse({'success': True, 'message': 'Sustitución eliminada'})
    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)


@csrf_exempt
@login_required(login_url='login')
def sustitucion_aceptar(request, pk):
    if request.method == 'POST':
        sust = get_object_or_404(Sustitucion, id=pk)

        if sust.estado != 'pendiente':
            return JsonResponse({'success': False, 'error': 'Esta sustitución ya fue procesada'}, status=400)

        turno = sust.turno_original
        original_emp = turno.empleado
        sustituto_emp = sust.empleado_sustituto

        turno.empleado = sustituto_emp
        turno.save()

        sust.estado = 'aceptada'
        sust.fecha_respuesta = timezone.now()
        sust.save()

        return JsonResponse({
            'success': True,
            'message': 'Sustitución aceptada y turno reasignado',
            'sustitucion': sust.to_dict(),
        })

    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)


@csrf_exempt
@login_required(login_url='login')
def sustitucion_rechazar(request, pk):
    if request.method == 'POST':
        sust = get_object_or_404(Sustitucion, id=pk)

        if sust.estado != 'pendiente':
            return JsonResponse({'success': False, 'error': 'Esta sustitución ya fue procesada'}, status=400)

        try:
            data = json.loads(request.body)
            observaciones = data.get('observaciones', '').strip()
        except json.JSONDecodeError:
            observaciones = ''

        if observaciones:
            sust.observaciones = observaciones

        sust.estado = 'rechazada'
        sust.fecha_respuesta = timezone.now()
        sust.save()

        return JsonResponse({'success': True, 'message': 'Sustitución rechazada', 'sustitucion': sust.to_dict()})

    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)


# ─── Calendario & Reportes ───────────────────────────────────────────────────

@login_required(login_url='login')
def calendario(request):
    return render(request, 'Vacaciones/calendario.html')


@login_required(login_url='login')
@admin_required
def reportes(request):
    return render(request, 'Vacaciones/reportes.html')


@login_required(login_url='login')
@admin_required
def reporte_pdf(request):
    ausentismo_data = []
    for dept in Departamento.objects.all():
        total = dept.empleados.count()
        ausentes = dept.empleados.filter(estado__in=['vacaciones', 'licencia']).count()
        porcentaje = round((ausentes / total * 100), 1) if total > 0 else 0
        ausentismo_data.append({
            'departamento': dept.nombre,
            'total_empleados': total,
            'ausentes': ausentes,
            'porcentaje': porcentaje,
        })

    vacaciones_data = list(
        Empleado.objects.filter(estado='activo')
        .order_by('apellidos')
        .values('nombres', 'apellidos', 'dias_vacaciones_pendientes', 'dias_vacaciones_tomados')
    )

    total_empleados = Empleado.objects.count()
    total_departamentos = Departamento.objects.count()
    total_ausentes = sum(d['ausentes'] for d in ausentismo_data)
    promedio_ausentismo = round((total_ausentes / total_empleados * 100), 2) if total_empleados > 0 else 0

    html = render_to_string('Vacaciones/reporte_pdf.html', {
        'ausentismo_data': ausentismo_data,
        'vacaciones_data': vacaciones_data,
        'total_empleados': total_empleados,
        'total_departamentos': total_departamentos,
        'promedio_ausentismo': promedio_ausentismo,
        'fecha': timezone.now().strftime('%d/%m/%Y %H:%M'),
    })

    if pisa is None:
        return HttpResponse('xhtml2pdf no está instalado', status=500)

    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode('UTF-8')), result, encoding='UTF-8')
    if pdf.err:
        return HttpResponse('Error generando PDF', status=500)

    response = HttpResponse(result.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_rrhh.pdf"'
    response['Content-Transfer-Encoding'] = 'binary'
    return response

@csrf_exempt
@login_required(login_url='login')
@admin_required
def enviar_reporte(request):
    if request.method != 'POST':
        return JsonResponse(
            {'success': False, 'error': 'Método no permitido'},
            status=405
        )

    try:
        data = json.loads(request.body)
        email_destino = data.get('email', '').strip()
    except json.JSONDecodeError:
        return JsonResponse(
            {'success': False, 'error': 'JSON inválido'},
            status=400
        )

    if not email_destino:
        return JsonResponse(
            {'success': False, 'error': 'Correo electrónico requerido'},
            status=400
        )

    resend_api_key = os.environ.get('RESEND_API_KEY', '').strip()

    if not resend_api_key:
        return JsonResponse(
            {
                'success': False,
                'error': 'La variable RESEND_API_KEY no está configurada'
            },
            status=500
        )

    ausentismo_data = []

    for dept in Departamento.objects.all():
        total = dept.empleados.count()

        ausentes = dept.empleados.filter(
            estado__in=['vacaciones', 'licencia']
        ).count()

        porcentaje = (
            round((ausentes / total * 100), 1)
            if total > 0 else 0
        )

        ausentismo_data.append({
            'departamento': dept.nombre,
            'total_empleados': total,
            'ausentes': ausentes,
            'porcentaje': porcentaje,
        })

    vacaciones_data = list(
        Empleado.objects.filter(estado='activo')
        .order_by('apellidos')
        .values(
            'nombres',
            'apellidos',
            'dias_vacaciones_pendientes',
            'dias_vacaciones_tomados'
        )
    )

    total_empleados = Empleado.objects.count()
    total_departamentos = Departamento.objects.count()
    total_ausentes = sum(
        dato['ausentes']
        for dato in ausentismo_data
    )

    promedio_ausentismo = (
        round((total_ausentes / total_empleados * 100), 2)
        if total_empleados > 0 else 0
    )

    html = render_to_string(
        'Vacaciones/reporte_pdf.html',
        {
            'ausentismo_data': ausentismo_data,
            'vacaciones_data': vacaciones_data,
            'total_empleados': total_empleados,
            'total_departamentos': total_departamentos,
            'promedio_ausentismo': promedio_ausentismo,
            'fecha': timezone.now().strftime('%d/%m/%Y %H:%M'),
        }
    )

    if pisa is None:
        return JsonResponse(
            {
                'success': False,
                'error': 'xhtml2pdf no está instalado'
            },
            status=500
        )

    resultado_pdf = BytesIO()

    pdf = pisa.pisaDocument(
        BytesIO(html.encode('UTF-8')),
        resultado_pdf,
        encoding='UTF-8'
    )

    if pdf.err:
        return JsonResponse(
            {
                'success': False,
                'error': 'Error generando PDF'
            },
            status=500
        )

    try:
        resend.api_key = resend_api_key

        pdf_base64 = base64.b64encode(
            resultado_pdf.getvalue()
        ).decode('utf-8')

        respuesta = resend.Emails.send({
            'from': os.environ.get(
                'RESEND_FROM_EMAIL',
                'Sistema RRHH <onboarding@resend.dev>'
            ),
            'to': [email_destino],
            'subject': 'REPORTE EXPORTADO',
            'html': """
                <h2>Reporte de Recursos Humanos</h2>
                <p>
                    Adjunto se encuentra el reporte exportado
                    del sistema de Recursos Humanos.
                </p>
            """,
            'attachments': [
                {
                    'filename': 'reporte_rrhh.pdf',
                    'content': pdf_base64,
                }
            ],
        })

        if not respuesta:
            raise Exception('Resend no devolvió una respuesta válida')

    except Exception as error:
        return JsonResponse(
            {
                'success': False,
                'error': f'Error al enviar correo: {str(error)}'
            },
            status=500
        )

    return JsonResponse({
        'success': True,
        'message': 'Reporte enviado exitosamente'
    })

# ─── API Endpoints ────────────────────────────────────────────────────────────

@login_required(login_url='login')
@csrf_exempt
def api_calendar_events(request):
    events = []

    if es_admin(request.user):
        turnos = TurnoGuardia.objects.select_related('empleado').all()
    else:
        emp = request.user.empleado if hasattr(request.user, 'empleado') else None
        turnos = TurnoGuardia.objects.filter(empleado=emp).select_related('empleado').all() if emp else TurnoGuardia.objects.none()
    for t in turnos:
        colors = {'manana': '#28a745', 'tarde': '#ffc107', 'noche': '#6f42c1'}
        events.append({
            'id': f'turno-{t.id}',
            'title': f'{t.empleado.nombre_completo} - {t.get_turno_display()}',
            'start': t.fecha.strftime('%Y-%m-%d'),
            'end': t.fecha.strftime('%Y-%m-%d'),
            'color': colors.get(t.turno, '#17a2b8'),
            'type': 'turno',
        })

    if es_admin(request.user):
        permisos = SolicitudPermiso.objects.select_related('empleado').all()
    else:
        emp = request.user.empleado if hasattr(request.user, 'empleado') else None
        permisos = SolicitudPermiso.objects.filter(empleado=emp).select_related('empleado').all() if emp else SolicitudPermiso.objects.none()
    for p in permisos:
        color_map = {'aprobado': '#28a745', 'pendiente': '#ffc107', 'rechazado': '#dc3545', 'cancelado': '#6c757d'}
        events.append({
            'id': f'permiso-{p.id}',
            'title': f'{p.empleado.nombre_completo} - {p.get_tipo_display()}',
            'start': p.fecha_inicio.strftime('%Y-%m-%d'),
            'end': p.fecha_fin.strftime('%Y-%m-%d'),
            'color': color_map.get(p.estado, '#17a2b8'),
            'type': 'permiso',
        })

    return JsonResponse({'events': events})


@csrf_exempt
def api_departamentos(request):
    departamentos = Departamento.objects.all()
    return JsonResponse({'departamentos': [d.to_dict() for d in departamentos]})


@login_required(login_url='login')
@csrf_exempt
def api_empleados(request):
    if es_admin(request.user):
        departamento_id = request.GET.get('departamento_id')
        empleados = Empleado.objects.select_related('departamento').all()
        if departamento_id:
            empleados = empleados.filter(departamento_id=departamento_id)
        return JsonResponse({'empleados': [e.to_dict() for e in empleados]})
    else:
        emp = request.user.empleado if hasattr(request.user, 'empleado') else None
        if emp:
            return JsonResponse({'empleados': [emp.to_dict()]})
        return JsonResponse({'empleados': []})


@login_required(login_url='login')
@csrf_exempt
def api_ausentismo_departamento(request):
    data = []
    for dept in Departamento.objects.all():
        total = dept.empleados.count()
        ausentes = dept.empleados.filter(estado__in=['vacaciones', 'licencia']).count()
        porcentaje = round((ausentes / total * 100), 1) if total > 0 else 0
        data.append({
            'departamento': dept.nombre,
            'total_empleados': total,
            'ausentes': ausentes,
            'porcentaje': porcentaje,
        })
    return JsonResponse({'data': data})


@login_required(login_url='login')
@csrf_exempt
def api_vacaciones_pendientes(request):
    data = list(
        Empleado.objects.filter(estado='activo')
        .order_by('apellidos')
        .values('id', 'nombres', 'apellidos', 'dias_vacaciones_pendientes', 'dias_vacaciones_tomados')
    )
    return JsonResponse({'data': data})


@login_required(login_url='login')
@csrf_exempt
def api_empleado_detail(request, pk):
    empleado = get_object_or_404(Empleado, id=pk)
    return JsonResponse({'empleado': empleado.to_dict()})
