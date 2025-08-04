import os
import django
import pandas as pd
from datetime import datetime

# Configurar Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stockapp.settings")
django.setup()

from inventario.models  import Entrega, EntregaItem, OrdenDeCompra, Bien, OrdenDeCompraItem  # Cambiar a tu app

# Cargar Excel
archivo = "stock/pedidos.xlsx"
df = pd.read_excel(archivo)

# Contador para número de pedido
numero_pedido_auto = 1

for idx, row in df.iterrows():
    try:
        nro_pedido = row.get("N° DE PEDIDO")
        if pd.isna(nro_pedido):
            nro_pedido = f"AUTO-{numero_pedido_auto}"
            numero_pedido_auto += 1

        dependencia = str(row["DEPENDENCIA"]).strip().upper() if pd.notna(row["DEPENDENCIA"]) else "PEDIDO ANTERIOR"
        fecha_entrega = row["FECHA DE ENTREGA"]
        if pd.isna(fecha_entrega):
            fecha_entrega = datetime(2025, 1, 1)

        numero_oc = str(row["ORDEN DE COMPRA"]).strip().upper()

        renglon_raw = str(row["RENGLÓN"]).strip()
        try:
            renglon = int(renglon_raw)
        except:
            renglon = 0

        bien_nombre = str(row["BIEN"]).strip().upper()
        cantidad_raw = str(row["CANTIDAD ENTREGADA"]).strip()
        try:
            cantidad = int(cantidad_raw)
        except:
            print(f"⚠️ Cantidad inválida en fila {idx+2}, se usará 1")
            cantidad = 1

        try:
            oc = OrdenDeCompra.objects.get(numero=numero_oc)
        except OrdenDeCompra.DoesNotExist:
            print(f"⚠️ OC '{numero_oc}' no encontrada en fila {idx+2}")
            continue

        try:
            bien = Bien.objects.get(nombre=bien_nombre)
        except Bien.DoesNotExist:
            print(f"⚠️ Bien '{bien_nombre}' no encontrado en fila {idx+2}")
            continue

        try:
            item_oc = OrdenDeCompraItem.objects.get(
                orden_de_compra=oc,
                bien=bien,
                renglon=renglon
            )
            precio_unitario = item_oc.precio_unitario
        except OrdenDeCompraItem.DoesNotExist:
            print(f"⚠️ Precio no encontrado para OC '{numero_oc}' - Bien '{bien_nombre}' (fila {idx+2}). Se usará $1.00")
            precio_unitario = 1.00

        entrega = Entrega.objects.create(
            fecha=fecha_entrega,
            area_persona=dependencia,
            observaciones=f"IMPORTACIÓN EXCEL - PEDIDO {nro_pedido}",
            orden_de_compra=oc
        )

        EntregaItem.objects.create(
            entrega=entrega,
            orden_de_compra=oc,
            bien=bien,
            cantidad=cantidad,
            precio_unitario=precio_unitario,
            precio_total=cantidad * precio_unitario
        )

        print(f"✅ Entrega creada (pedido {nro_pedido}) - Bien: {bien_nombre} - Cant: {cantidad}")

    except Exception as e:
        print(f"❌ Error en fila {idx+2}: {e}")

print("🎉 Carga de remitos finalizada.")