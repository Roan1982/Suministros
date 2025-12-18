from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from inventario.models import (
    Rubro, Bien, OrdenDeCompra, OrdenDeCompraItem,
    Servicio, ServicioPago, Almacen, Entrega, EntregaItem
)
from decimal import Decimal
from datetime import date, datetime, timedelta
import random

class Command(BaseCommand):
    help = 'Poblar la base de datos con datos ficticios para testing'

    def handle(self, *args, **options):
        self.stdout.write('Poblando base de datos con datos ficticios...')

        # Crear usuario admin si no existe
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write('Usuario admin creado')

        # Crear rubros
        rubros_data = [
            'MATERIALES DE CONSTRUCCIÓN',
            'HERRAMIENTAS',
            'EQUIPOS INFORMÁTICOS',
            'MUEBLES Y ENSERES',
            'MATERIALES DE LIMPIEZA',
            'SUMINISTROS DE OFICINA',
            'EQUIPOS DE SEGURIDAD',
            'MATERIALES ELÉCTRICOS',
            'FONTANERÍA',
            'PINTURAS Y ACABADOS'
        ]

        rubros = []
        for rubro_nombre in rubros_data:
            rubro, created = Rubro.objects.get_or_create(
                nombre=rubro_nombre,
                defaults={'nombre': rubro_nombre}
            )
            rubros.append(rubro)
            if created:
                self.stdout.write(f'Rubro creado: {rubro.nombre}')

        # Crear almacenes
        almacenes_data = [
            {'nombre': 'ALMACÉN CENTRAL', 'direccion': 'AV. PRINCIPAL 123'},
            {'nombre': 'ALMACÉN NORTE', 'direccion': 'CALLE NORTE 456'},
            {'nombre': 'ALMACÉN SUR', 'direccion': 'CALLE SUR 789'},
        ]

        almacenes = []
        for almacen_data in almacenes_data:
            almacen, created = Almacen.objects.get_or_create(
                nombre=almacen_data['nombre'],
                defaults={
                    'direccion': almacen_data['direccion'],
                    'responsable': admin_user
                }
            )
            almacenes.append(almacen)
            if created:
                self.stdout.write(f'Almacén creado: {almacen.nombre}')

        # Crear bienes
        bienes_data = [
            # Materiales de construcción
            {'nombre': 'CEMENTO PORTLAND', 'rubro': rubros[0], 'catalogo': 'MAT-001', 'renglon': '1'},
            {'nombre': 'ARENA FINA', 'rubro': rubros[0], 'catalogo': 'MAT-002', 'renglon': '2'},
            {'nombre': 'GRAVA', 'rubro': rubros[0], 'catalogo': 'MAT-003', 'renglon': '3'},
            {'nombre': 'LADRILLO COMÚN', 'rubro': rubros[0], 'catalogo': 'MAT-004', 'renglon': '4'},
            {'nombre': 'BLOCK 10X20X40', 'rubro': rubros[0], 'catalogo': 'MAT-005', 'renglon': '5'},

            # Herramientas
            {'nombre': 'MARTILLO', 'rubro': rubros[1], 'catalogo': 'HER-001', 'renglon': '1'},
            {'nombre': 'DESTORNILLADOR PLANO', 'rubro': rubros[1], 'catalogo': 'HER-002', 'renglon': '2'},
            {'nombre': 'DESTORNILLADOR PHILLIPS', 'rubro': rubros[1], 'catalogo': 'HER-003', 'renglon': '3'},
            {'nombre': 'ALICATE UNIVERSAL', 'rubro': rubros[1], 'catalogo': 'HER-004', 'renglon': '4'},
            {'nombre': 'CAJA DE HERRAMIENTAS', 'rubro': rubros[1], 'catalogo': 'HER-005', 'renglon': '5'},

            # Equipos informáticos
            {'nombre': 'MONITOR LED 24"', 'rubro': rubros[2], 'catalogo': 'INF-001', 'renglon': '1'},
            {'nombre': 'TECLADO MECÁNICO', 'rubro': rubros[2], 'catalogo': 'INF-002', 'renglon': '2'},
            {'nombre': 'MOUSE ÓPTICO', 'rubro': rubros[2], 'catalogo': 'INF-003', 'renglon': '3'},
            {'nombre': 'IMPRESORA LASER', 'rubro': rubros[2], 'catalogo': 'INF-004', 'renglon': '4'},
            {'nombre': 'DISCO DURO EXTERNO 1TB', 'rubro': rubros[2], 'catalogo': 'INF-005', 'renglon': '5'},

            # Muebles y enseres
            {'nombre': 'ESCRITORIO METÁLICO', 'rubro': rubros[3], 'catalogo': 'MUE-001', 'renglon': '1'},
            {'nombre': 'SILLA ERGONÓMICA', 'rubro': rubros[3], 'catalogo': 'MUE-002', 'renglon': '2'},
            {'nombre': 'ARCHIVADOR METÁLICO', 'rubro': rubros[3], 'catalogo': 'MUE-003', 'renglon': '3'},
            {'nombre': 'ESTANTE PARA LIBROS', 'rubro': rubros[3], 'catalogo': 'MUE-004', 'renglon': '4'},
            {'nombre': 'ALFOMBRA OFICINA', 'rubro': rubros[3], 'catalogo': 'MUE-005', 'renglon': '5'},

            # Materiales de limpieza
            {'nombre': 'JABÓN EN POLVO', 'rubro': rubros[4], 'catalogo': 'LIM-001', 'renglon': '1'},
            {'nombre': 'DESINFECTANTE', 'rubro': rubros[4], 'catalogo': 'LIM-002', 'renglon': '2'},
            {'nombre': 'PAPEL HIGIÉNICO', 'rubro': rubros[4], 'catalogo': 'LIM-003', 'renglon': '3'},
            {'nombre': 'ESCOBA', 'rubro': rubros[4], 'catalogo': 'LIM-004', 'renglon': '4'},
            {'nombre': 'TRAPO DE PISO', 'rubro': rubros[4], 'catalogo': 'LIM-005', 'renglon': '5'},
        ]

        bienes = []
        for bien_data in bienes_data:
            bien, created = Bien.objects.get_or_create(
                nombre=bien_data['nombre'],
                defaults={
                    'rubro': bien_data['rubro'],
                    'catalogo': bien_data['catalogo'],
                    'renglon': bien_data['renglon']
                }
            )
            bienes.append(bien)
            if created:
                self.stdout.write(f'Producto creado: {bien.nombre}')

        # Crear órdenes de compra
        proveedores = [
            'CONSTRUCTORA DEL NORTE S.A.',
            'SUMINISTROS INDUSTRIALES SRL',
            'TECNOLOGÍA AVANZADA S.A.',
            'MUEBLERÍA CENTRAL',
            'LIMPIEZA TOTAL S.R.L.',
            'ELECTRICIDAD Y FONTANERÍA',
            'SEGURIDAD INDUSTRIAL',
            'PINTURAS Y ACABADOS S.A.'
        ]

        ordenes = []
        for i in range(10):
            fecha_inicio = date.today() - timedelta(days=random.randint(30, 365))
            fecha_fin = fecha_inicio + timedelta(days=random.randint(30, 180))

            orden = OrdenDeCompra.objects.create(
                numero=f'OC-2025-{str(i+1).zfill(3)}',
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                proveedor=random.choice(proveedores),
                rubro=random.choice(rubros)
            )
            ordenes.append(orden)
            self.stdout.write(f'Orden de compra creada: {orden.numero}')

            # Crear items para cada orden
            num_items = random.randint(2, 5)
            selected_bienes = random.sample(bienes, num_items)

            for j, bien in enumerate(selected_bienes):
                precio_unitario = Decimal(str(random.uniform(10, 1000))).quantize(Decimal('0.01'))
                cantidad = random.randint(1, 50)

                OrdenDeCompraItem.objects.create(
                    orden_de_compra=orden,
                    bien=bien,
                    cantidad=cantidad,
                    precio_unitario=precio_unitario,
                    renglon=j+1
                )

        # Crear entregas (remitos)
        areas = [
            'DEPARTAMENTO TÉCNICO',
            'ADMINISTRACIÓN',
            'RECURSOS HUMANOS',
            'CONTABILIDAD',
            'SERVICIOS GENERALES',
            'MANTENIMIENTO',
            'SISTEMAS',
            'COMPRAS'
        ]

        entregas = []
        for i in range(15):
            fecha_entrega = datetime.now() - timedelta(days=random.randint(1, 90))
            orden_relacionada = random.choice(ordenes) if random.random() > 0.3 else None

            entrega = Entrega.objects.create(
                fecha=fecha_entrega,
                area_persona=random.choice(areas),
                observaciones=f'ENTREGA DE MATERIALES PARA {random.choice(["MANTENIMIENTO", "OFICINA", "PROYECTO", "REPOSICIÓN"])}',
                orden_de_compra=orden_relacionada
            )
            entregas.append(entrega)
            self.stdout.write(f'Remito creado: #{entrega.id}')

            # Crear items para cada entrega
            if orden_relacionada:
                # Usar items de la orden relacionada
                orden_items = list(orden_relacionada.items.all())
                if orden_items:
                    num_items = min(len(orden_items), random.randint(1, 3))
                    selected_items = random.sample(orden_items, num_items)

                    for orden_item in selected_items:
                        cantidad_entregada = random.randint(1, orden_item.cantidad)
                        EntregaItem.objects.create(
                            entrega=entrega,
                            orden_de_compra=orden_relacionada,
                            bien=orden_item.bien,
                            cantidad=cantidad_entregada,
                            precio_unitario=orden_item.precio_unitario
                        )
            else:
                # Crear items aleatorios
                num_items = random.randint(1, 4)
                selected_bienes = random.sample(bienes, num_items)

                for bien in selected_bienes:
                    cantidad_entregada = random.randint(1, 20)
                    precio_unitario = Decimal(str(random.uniform(5, 500))).quantize(Decimal('0.01'))

                    EntregaItem.objects.create(
                        entrega=entrega,
                        bien=bien,
                        cantidad=cantidad_entregada,
                        precio_unitario=precio_unitario
                    )

        # Crear servicios
        servicios_data = [
            {
                'nombre': 'MANTENIMIENTO DE EQUIPOS INFORMÁTICOS',
                'descripcion': 'SERVICIO DE MANTENIMIENTO PREVENTIVO Y CORRECTIVO DE COMPUTADORAS Y SERVIDORES',
                'proveedor': 'TECNOSISTEMAS S.A.',
                'frecuencia': 'MENSUAL',
                'costo_mensual': Decimal('2500.00'),
                'fecha_inicio': date.today() - timedelta(days=60),
                'fecha_fin': date.today() + timedelta(days=300),
                'rubro': rubros[2],
                'expediente_contratacion': 'EXP-2025-001'
            },
            {
                'nombre': 'LIMPIEZA DE INSTALACIONES',
                'descripcion': 'SERVICIO DE LIMPIEZA GENERAL DE OFICINAS Y ESPACIOS COMUNES',
                'proveedor': 'LIMPIEZA TOTAL S.R.L.',
                'frecuencia': 'SEMANAL',
                'costo_mensual': Decimal('1800.00'),
                'fecha_inicio': date.today() - timedelta(days=30),
                'fecha_fin': date.today() + timedelta(days=180),
                'rubro': rubros[4],
                'expediente_contratacion': 'EXP-2025-002'
            },
            {
                'nombre': 'SEGURIDAD PERIMETRAL',
                'descripcion': 'SERVICIO DE VIGILANCIA Y SEGURIDAD PERIMETRAL 24 HORAS',
                'proveedor': 'SEGURIDAD INTEGRAL S.A.',
                'frecuencia': 'MENSUAL',
                'costo_mensual': Decimal('4500.00'),
                'fecha_inicio': date.today() - timedelta(days=90),
                'fecha_fin': date.today() + timedelta(days=270),
                'rubro': rubros[6],
                'expediente_contratacion': 'EXP-2025-003'
            },
            {
                'nombre': 'MANTENIMIENTO ELÉCTRICO',
                'descripcion': 'SERVICIO DE MANTENIMIENTO PREVENTIVO DE INSTALACIONES ELÉCTRICAS',
                'proveedor': 'ELECTRICIDAD Y FONTANERÍA',
                'frecuencia': 'QUINCENAL',
                'costo_mensual': Decimal('1200.00'),
                'fecha_inicio': date.today() - timedelta(days=45),
                'fecha_fin': date.today() + timedelta(days=225),
                'rubro': rubros[7],
                'expediente_contratacion': 'EXP-2025-004'
            },
            {
                'nombre': 'SUMINISTRO DE AGUA MINERAL',
                'descripcion': 'SUMINISTRO SEMANAL DE AGUA MINERAL PARA OFICINAS',
                'proveedor': 'AGUAS PURAS S.A.',
                'frecuencia': 'SEMANAL',
                'costo_mensual': Decimal('800.00'),
                'fecha_inicio': date.today() - timedelta(days=15),
                'fecha_fin': date.today() + timedelta(days=345),
                'rubro': rubros[4],
                'expediente_contratacion': 'EXP-2025-005'
            }
        ]

        servicios = []
        for servicio_data in servicios_data:
            servicio = Servicio.objects.create(**servicio_data)
            servicios.append(servicio)
            self.stdout.write(f'Servicio creado: {servicio.nombre}')

            # Generar pagos para cada servicio
            servicio.generar_pagos_mensuales()

            # Marcar algunos pagos como pagados
            pagos = list(servicio.pagos.all())
            for pago in pagos[:len(pagos)//2]:  # Marcar la mitad como pagados
                pago.estado = 'PAGADO'
                pago.fecha_pago = pago.fecha_vencimiento
                pago.save()

        self.stdout.write(self.style.SUCCESS('Base de datos poblada exitosamente con datos ficticios!'))
        self.stdout.write(f'Rubros creados: {len(rubros)}')
        self.stdout.write(f'Productos creados: {len(bienes)}')
        self.stdout.write(f'Órdenes de compra creadas: {len(ordenes)}')
        self.stdout.write(f'Remitos creados: {len(entregas)}')
        self.stdout.write(f'Servicios creados: {len(servicios)}')
        self.stdout.write(f'Almacenes creados: {len(almacenes)}')
        self.stdout.write('')
        self.stdout.write('Usuario admin creado/actualizado:')
        self.stdout.write('  Username: admin')
        self.stdout.write('  Password: admin123')