from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from .models import Rubro, Bien, OrdenDeCompra, OrdenDeCompraItem, Entrega, EntregaItem, Servicio, ServicioPago, AuditLog
from django.db.models import Sum

class RubroModelTest(TestCase):
    def setUp(self):
        self.rubro = Rubro.objects.create(nombre="UTILIDADES")

    def test_rubro_creation(self):
        self.assertEqual(self.rubro.nombre, "UTILIDADES")
        self.assertEqual(str(self.rubro), "UTILIDADES")

class BienModelTest(TestCase):
    def setUp(self):
        self.rubro = Rubro.objects.create(nombre="UTILIDADES")
        self.bien = Bien.objects.create(
            nombre="LAPIZ HB",
            rubro=self.rubro,
            catalogo="CAT001",
            renglon="001"
        )

    def test_bien_creation(self):
        self.assertEqual(self.bien.nombre, "LAPIZ HB")
        self.assertEqual(self.bien.rubro, self.rubro)
        self.assertEqual(str(self.bien), "LAPIZ HB")

    def test_bien_save_uppercase(self):
        bien = Bien.objects.create(
            nombre="lápiz rojo",
            rubro=self.rubro
        )
        self.assertEqual(bien.nombre, "LÁPIZ ROJO")

class OrdenDeCompraTest(TestCase):
    def setUp(self):
        self.rubro = Rubro.objects.create(nombre="UTILIDADES")
        self.orden = OrdenDeCompra.objects.create(
            numero="OC001",
            fecha_inicio=timezone.now().date(),
            proveedor="PROVEEDOR S.A."
        )

    def test_orden_creation(self):
        self.assertEqual(self.orden.numero, "OC001")
        self.assertEqual(str(self.orden), "OC #OC001")

    def test_orden_save_uppercase(self):
        orden = OrdenDeCompra.objects.create(
            numero="oc002",
            fecha_inicio=timezone.now().date(),
            proveedor="proveedor s.a."
        )
        self.assertEqual(orden.numero, "OC002")
        self.assertEqual(orden.proveedor, "PROVEEDOR S.A.")

class ServicioTest(TestCase):
    def setUp(self):
        self.rubro = Rubro.objects.create(nombre="SERVICIOS")
        self.servicio = Servicio.objects.create(
            nombre="MANTENIMIENTO DE COMPUTADORAS",
            proveedor="TECH SOLUTIONS",
            frecuencia="MENSUAL",
            costo_mensual=Decimal("1500.00"),
            fecha_inicio=timezone.now().date()
        )

    def test_servicio_creation(self):
        self.assertEqual(self.servicio.nombre, "MANTENIMIENTO DE COMPUTADORAS")
        self.assertEqual(self.servicio.frecuencia, "MENSUAL")
        self.assertEqual(self.servicio.costo_mensual, Decimal("1500.00"))

    def test_servicio_estado_activo(self):
        # Servicio sin fecha fin debería ser ACTIVO
        self.assertEqual(self.servicio.estado_actual, "ACTIVO")

    def test_servicio_estado_vencido(self):
        # Servicio con fecha fin pasada
        fecha_pasada = timezone.now().date() - timezone.timedelta(days=30)
        self.servicio.fecha_fin = fecha_pasada
        self.servicio.save()
        self.assertEqual(self.servicio.estado_actual, "VENCIDO")

    def test_calcular_costo_total(self):
        # Servicio de 3 meses
        fecha_fin = self.servicio.fecha_inicio + timezone.timedelta(days=90)
        self.servicio.fecha_fin = fecha_fin
        self.servicio.save()
        costo_total = self.servicio.calcular_costo_total()
        self.assertEqual(costo_total, Decimal("4500.00"))  # 1500 * 3

class StockCalculationTest(TestCase):
    def setUp(self):
        self.rubro = Rubro.objects.create(nombre="UTILIDADES")
        self.bien = Bien.objects.create(
            nombre="LAPIZ HB",
            rubro=self.rubro
        )
        self.orden = OrdenDeCompra.objects.create(
            numero="OC001",
            fecha_inicio=timezone.now().date()
        )
        self.orden_item = OrdenDeCompraItem.objects.create(
            orden_de_compra=self.orden,
            bien=self.bien,
            cantidad=100,
            precio_unitario=Decimal("10.00")
        )

    def test_stock_sin_entregas(self):
        # Stock debería ser igual a la cantidad comprada
        stock = self.orden_item.cantidad
        self.assertEqual(stock, 100)

    def test_stock_con_entregas(self):
        # Crear entrega
        entrega = Entrega.objects.create(
            area_persona="DEPTO. INFORMATICA",
            orden_de_compra=self.orden
        )
        EntregaItem.objects.create(
            entrega=entrega,
            orden_de_compra=self.orden,
            bien=self.bien,
            cantidad=30,
            precio_unitario=Decimal("10.00")
        )
        
        # Stock debería ser 100 - 30 = 70
        entregado = EntregaItem.objects.filter(
            orden_de_compra=self.orden,
            bien=self.bien
        ).aggregate(total=Sum('cantidad'))['total'] or 0
        stock = self.orden_item.cantidad - entregado
        self.assertEqual(stock, 70)

class AuditLogTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.rubro = Rubro.objects.create(nombre="TEST")

    def test_audit_log_creation(self):
        # Crear un log de auditoría
        log = AuditLog.objects.create(
            user=self.user,
            action="CREATE",
            content_type_id=1,  # Asumiendo que Rubro es el primer ContentType
            object_id=self.rubro.id,
            object_repr=str(self.rubro),
            changes={"nombre": "TEST"}
        )
        self.assertEqual(log.action, "CREATE")
        self.assertEqual(log.user, self.user)
        self.assertEqual(log.object_repr, "TEST")

class ViewsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
        self.rubro = Rubro.objects.create(nombre="TEST")

    def test_dashboard_view(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'inventario/dashboard.html')

    def test_rubros_list_view(self):
        response = self.client.get('/rubros/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'inventario/rubros_list.html')

    def test_bienes_list_view(self):
        response = self.client.get('/bienes/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'inventario/bienes_list.html')
