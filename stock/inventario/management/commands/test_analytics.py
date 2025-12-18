from django.core.management.base import BaseCommand
from django.test import Client
from django.contrib.auth import authenticate
import json

class Command(BaseCommand):
    help = 'Test analytics API'

    def handle(self, *args, **options):
        # Crear cliente de prueba
        client = Client()

        # Hacer login
        login_success = client.login(username='admin', password='admin123')
        self.stdout.write(f'Login exitoso: {login_success}')

        # Probar la API de analytics
        response = client.get('/api/analytics/')
        self.stdout.write(f'Status code: {response.status_code}')
        self.stdout.write(f'Content type: {response.get("Content-Type")}')

        if response.status_code == 200:
            data = json.loads(response.content)
            self.stdout.write('Datos de analytics:')
            self.stdout.write(f'Stock por rubro: {len(data.get("stock_por_rubro", []))}')
            self.stdout.write(f'Entregas por mes: {len(data.get("entregas_por_mes", []))}')
            self.stdout.write(f'Servicios por estado: {len(data.get("servicios_por_estado", []))}')
            self.stdout.write(f'Top bienes: {len(data.get("top_bienes", []))}')
        else:
            self.stdout.write(f'Error en la respuesta: {response.content.decode()}')