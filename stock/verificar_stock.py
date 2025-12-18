#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockapp.settings')
django.setup()

from inventario.models import Rubro, Bien, OrdenDeCompraItem, EntregaItem
from django.db.models import Sum
from inventario.api import AnalyticsAPIView

print('=== VERIFICACIÓN DE STOCK POR RUBRO ===')

# Método correcto: calcular stock por rubro como en el reporte
rubros = Rubro.objects.all().order_by('nombre')
stock_por_rubro_correcto = {}

for rubro in rubros:
    bienes = Bien.objects.filter(rubro=rubro)
    total_stock_rubro = 0
    for bien in bienes:
        comprado = OrdenDeCompraItem.objects.filter(bien=bien).aggregate(total=Sum('cantidad'))['total'] or 0
        entregado = EntregaItem.objects.filter(bien=bien).aggregate(total=Sum('cantidad'))['total'] or 0
        stock = comprado - entregado
        if stock > 0:
            total_stock_rubro += stock
    if total_stock_rubro > 0:
        stock_por_rubro_correcto[rubro.nombre] = total_stock_rubro

print('Stock por rubro (método correcto):')
for rubro, stock in stock_por_rubro_correcto.items():
    print(f'  {rubro}: {stock}')

print()

# Método actual de la API
api_view = AnalyticsAPIView()
stock_api = api_view.get_stock_por_rubro()

print('Stock por rubro (API actual):')
for item in stock_api:
    rubro_nombre = item.get('rubro__nombre', 'N/A')
    total_stock = item.get('total_stock', 0)
    print(f'  {rubro_nombre}: {total_stock}')

print()

# Comparación
print('=== COMPARACIÓN ===')
all_rubros = set(list(stock_por_rubro_correcto.keys()) + [item.get('rubro__nombre', 'N/A') for item in stock_api])

for rubro in sorted(all_rubros):
    correcto = stock_por_rubro_correcto.get(rubro, 0)
    api_val = next((item.get('total_stock', 0) for item in stock_api if item.get('rubro__nombre') == rubro), 0)
    if correcto != api_val:
        print(f'DIFERENCIA en {rubro}: Correcto={correcto}, API={api_val}')
    else:
        print(f'IGUAL en {rubro}: {correcto}')