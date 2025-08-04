import os
import django
import pandas as pd

# Configurar el entorno de Django

# Cambia 'stockapp.settings' si tu settings.py está en otro módulo
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stockapp.settings")
django.setup()

# Cambia 'inventario' si tu app se llama diferente
from inventario.models import Rubro, Bien, OrdenDeCompra, OrdenDeCompraItem

# Ruta del archivo Excel

archivo = "stock/almacenes.xlsx"  # Debe estar en la carpeta 'stock'
if not os.path.exists(archivo):
    raise FileNotFoundError(f"No se encontró el archivo {archivo} en {os.getcwd()}")
df = pd.read_excel(archivo)


import_errors = 0
importados = 0
for idx, row in df.iterrows():
    try:
        rubro_nombre = str(row["RUBRO"]).strip().upper()
        bien_nombre = str(row["BIEN"]).strip().upper()
        catalogo = str(row["CATALOGO"]).strip().upper() if not pd.isna(row["CATALOGO"]) else ""
        renglon_bien = str(row["RENGLÓN"]).strip()
        numero_oc = str(row["ORDEN DE COMPRA"]).strip().upper()
        cantidad = int(row["CANTIDAD COMPRADA"])
        precio_unitario = float(row["PRECIO UNITARIO"])

        # RUBRO
        rubro, _ = Rubro.objects.get_or_create(nombre=rubro_nombre)

        # BIEN
        bien, _ = Bien.objects.get_or_create(
            nombre=bien_nombre,
            defaults={
                "rubro": rubro,
                "catalogo": catalogo,
                "renglon": renglon_bien,
            }
        )
        if bien.rubro is None:
            bien.rubro = rubro
            bien.save()

        # ORDEN DE COMPRA
        orden, _ = OrdenDeCompra.objects.get_or_create(
            numero=numero_oc,
            defaults={
                "fecha_inicio": "2024-01-01",  # Ajustar si hace falta
                "proveedor": "DESCONOCIDO",    # Ajustar si hace falta
            }
        )

        # ITEM
        item, created = OrdenDeCompraItem.objects.get_or_create(
            orden_de_compra=orden,
            bien=bien,
            renglon=int(renglon_bien) if renglon_bien.isdigit() else 1,
            defaults={
                "cantidad": cantidad,
                "precio_unitario": precio_unitario,
                "precio_total": cantidad * precio_unitario,
            }
        )

        if not created:
            item.cantidad += cantidad
            item.precio_unitario = precio_unitario
            item.precio_total = item.cantidad * precio_unitario
            item.save()
        importados += 1
    except Exception as e:
        print(f"Error en fila {idx+2}: {e}")
        import_errors += 1

print(f"✅ Datos importados correctamente: {importados} filas. Errores: {import_errors}")
