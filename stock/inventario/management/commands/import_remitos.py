from django.core.management.base import BaseCommand
from django.db import transaction
from inventario.models import Entrega, EntregaItem, OrdenDeCompra, Bien, OrdenDeCompraItem
from decimal import Decimal
import pandas as pd
from datetime import datetime

class Command(BaseCommand):
    help = 'Importar remitos desde archivo Excel'

    def add_arguments(self, parser):
        parser.add_argument('excel_file', type=str, help='Ruta al archivo Excel')

    def handle(self, *args, **options):
        excel_file = options['excel_file']

        try:
            # Determinar si es CSV o Excel basado en la extensión
            if excel_file.lower().endswith('.csv'):
                df = pd.read_csv(excel_file)
            else:
                df = pd.read_excel(excel_file, engine='openpyxl')
                
            self.stdout.write(f'Procesando archivo: {excel_file}')
            self.stdout.write(f'Filas encontradas: {len(df)}')

            importados = 0
            errores = []

            with transaction.atomic():
                for index, row in df.iterrows():
                    try:
                        # Extraer datos del Excel
                        dependencia = str(row.get('DEPENDENCIA', '')).strip().upper()
                        if not dependencia:
                            dependencia = 'SIN ESPECIFICAR'

                        fecha_entrega = row.get('FECHA DE ENTREGA')
                        if pd.isna(fecha_entrega):
                            fecha_entrega = datetime.now()
                        elif isinstance(fecha_entrega, str):
                            try:
                                fecha_entrega = datetime.strptime(fecha_entrega, '%Y-%m-%d')
                            except:
                                fecha_entrega = datetime.now()

                        numero_oc = str(row.get('ORDEN DE COMPRA', '')).strip().upper()

                        renglon_raw = str(row.get('RENGLÓN', '')).strip()
                        try:
                            renglon = int(float(renglon_raw)) if renglon_raw else 1
                        except:
                            renglon = 1

                        bien_nombre = str(row.get('BIEN', '')).strip().upper()
                        cantidad_raw = str(row.get('CANTIDAD ENTREGADA', '')).strip()

                        try:
                            cantidad = int(float(cantidad_raw)) if cantidad_raw else 1
                        except:
                            cantidad = 1

                        # Validar orden de compra
                        try:
                            orden_compra = OrdenDeCompra.objects.get(numero=numero_oc)
                        except OrdenDeCompra.DoesNotExist:
                            errores.append(f"Fila {index+2}: Orden de compra '{numero_oc}' no encontrada")
                            continue

                        # Validar bien
                        try:
                            bien = Bien.objects.get(nombre=bien_nombre)
                        except Bien.DoesNotExist:
                            errores.append(f"Fila {index+2}: Bien '{bien_nombre}' no encontrado")
                            continue

                        # Buscar precio en la orden de compra
                        try:
                            item_oc = OrdenDeCompraItem.objects.get(
                                orden_de_compra=orden_compra,
                                bien=bien,
                                renglon=renglon
                            )
                            precio_unitario = item_oc.precio_unitario
                        except OrdenDeCompraItem.DoesNotExist:
                            # Buscar cualquier item de la OC con este bien
                            try:
                                item_oc = OrdenDeCompraItem.objects.filter(
                                    orden_de_compra=orden_compra,
                                    bien=bien
                                ).first()
                                if item_oc:
                                    precio_unitario = item_oc.precio_unitario
                                else:
                                    precio_unitario = Decimal('1.00')
                            except:
                                precio_unitario = Decimal('1.00')

                        # Crear entrega (remito)
                        entrega = Entrega.objects.create(
                            fecha=fecha_entrega,
                            area_persona=dependencia,
                            observaciones=f'IMPORTADO DESDE EXCEL - {numero_oc}',
                            orden_de_compra=orden_compra
                        )

                        # Crear item de entrega
                        EntregaItem.objects.create(
                            entrega=entrega,
                            orden_de_compra=orden_compra,
                            bien=bien,
                            cantidad=cantidad,
                            precio_unitario=precio_unitario
                        )

                        importados += 1
                        self.stdout.write(f'Remito #{entrega.id} creado: {bien.nombre} x {cantidad}')

                    except Exception as e:
                        errores.append(f"Fila {index+2}: {str(e)}")

            # Mostrar resultados
            self.stdout.write(self.style.SUCCESS(f'\nImportación completada:'))
            self.stdout.write(f'Remitos importados: {importados}')

            if errores:
                self.stdout.write(self.style.WARNING(f'Errores encontrados: {len(errores)}'))
                for error in errores[:10]:  # Mostrar máximo 10 errores
                    self.stdout.write(f'  - {error}')
                if len(errores) > 10:
                    self.stdout.write(f'  ... y {len(errores) - 10} errores más')

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error al procesar el archivo: {str(e)}'))