#!/usr/bin/env python
import os
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockapp.settings')
django.setup()

from django.test import Client
import json

print("Iniciando test...")

# Crear cliente de prueba
client = Client()

print("Cliente creado")

# Hacer login
login_success = client.login(username='admin', password='admin123')
print('Login exitoso:', login_success)

# Probar la API de analytics
print("Haciendo request a /api/analytics/")
response = client.get('/api/analytics/')
print('Status code:', response.status_code)
print('Content type:', response.get('Content-Type'))

if response.status_code == 200:
    print("Response OK, intentando parsear JSON...")
    try:
        data = json.loads(response.content)
        print('Datos de analytics:')
        print('Stock por rubro:', len(data.get('stock_por_rubro', [])))
        print('Entregas por mes:', len(data.get('entregas_por_mes', [])))
        print('Servicios por estado:', len(data.get('servicios_por_estado', [])))
        print('Top bienes:', len(data.get('top_bienes', [])))
        print('Totales:', data.get('totales', {}))
    except json.JSONDecodeError as e:
        print('Error al decodificar JSON:', e)
        print('Contenido de la respuesta:', response.content.decode('utf-8')[:500])
else:
    print('Error en la respuesta:', response.status_code)
    print('Contenido:', response.content.decode('utf-8')[:500])