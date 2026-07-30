from django.test import TestCase, Client
from django.urls import reverse
from datetime import date
import json
from django.contrib.auth.models import User
from .models import Departamento, Empleado, SolicitudPermiso, TurnoGuardia, Sustitucion


class RRHHTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client.force_login(self.user)
        self.dept = Departamento.objects.create(
            nombre="Tecnologia",
            descripcion="Depto de TI",
            jefe_departamento="Carlos Jefe"
        )
        self.emp1 = Empleado.objects.create(
            cedula="1711111111",
            nombres="Juan",
            apellidos="Perez",
            email="juan.perez@empresa.com",
            departamento=self.dept,
            cargo="Desarrollador",
            fecha_ingreso=date(2022, 1, 1),
            salario=1500.00
        )
        self.emp2 = Empleado.objects.create(
            cedula="1722222222",
            nombres="Maria",
            apellidos="Gomez",
            email="maria.gomez@empresa.com",
            departamento=self.dept,
            cargo="Analista",
            fecha_ingreso=date(2023, 5, 10),
            salario=1800.00
        )
        self.permiso1 = SolicitudPermiso.objects.create(
            empleado=self.emp1,
            tipo="vacaciones",
            motivo="Vacaciones anuales",
            fecha_inicio=date(2026, 8, 1),
            fecha_fin=date(2026, 8, 10),
            dias_solicitados=10,
            estado="pendiente"
        )
        self.turno1 = TurnoGuardia.objects.create(
            empleado=self.emp1,
            fecha=date(2026, 8, 15),
            turno="manana",
            horas=8
        )
        self.turno2 = TurnoGuardia.objects.create(
            empleado=self.emp2,
            fecha=date(2026, 8, 15),
            turno="tarde",
            horas=8
        )

    def test_dashboard_view(self):
        response = self.client.get(reverse('Vacaciones:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dashboard")

    def test_api_calendar_events(self):
        response = self.client.get(reverse('Vacaciones:api_calendar_events'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('events', data)
        self.assertTrue(len(data['events']) >= 3)

    def test_permiso_aprobar_masivo(self):
        permiso2 = SolicitudPermiso.objects.create(
            empleado=self.emp2,
            tipo="personal",
            motivo="Asunto personal",
            fecha_inicio=date(2026, 8, 5),
            fecha_fin=date(2026, 8, 6),
            dias_solicitados=2,
            estado="pendiente"
        )
        url = reverse('Vacaciones:permiso_aprobar_masivo')
        payload = json.dumps({'ids': [self.permiso1.id, permiso2.id]})
        response = self.client.post(url, data=payload, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = response.json()
        self.assertTrue(res['success'])
        self.assertEqual(res['aprobados'], 2)
        self.permiso1.refresh_from_db()
        self.assertEqual(self.permiso1.estado, 'aprobado')

    def test_turno_intercambiar(self):
        url = reverse('Vacaciones:turno_intercambiar')
        payload = json.dumps({
            'turno_id_1': self.turno1.id,
            'turno_id_2': self.turno2.id,
            'motivo': 'Intercambio de prueba'
        })
        response = self.client.post(url, data=payload, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = response.json()
        self.assertTrue(res['success'])
        self.turno1.refresh_from_db()
        self.turno2.refresh_from_db()
        self.assertEqual(self.turno1.empleado, self.emp2)
        self.assertEqual(self.turno2.empleado, self.emp1)

    def test_api_ausentismo(self):
        response = self.client.get(reverse('Vacaciones:api_ausentismo_departamento'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('data', data)
