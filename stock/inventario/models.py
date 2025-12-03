from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils import timezone

class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('CREATE', 'Crear'),
        ('UPDATE', 'Actualizar'),
        ('DELETE', 'Eliminar'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Usuario")
    action = models.CharField(max_length=10, choices=ACTION_CHOICES, verbose_name="Acción")
    timestamp = models.DateTimeField(default=timezone.now, verbose_name="Fecha y hora")

    # Campos para el objeto afectado
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    # Información adicional
    object_repr = models.CharField(max_length=200, verbose_name="Representación del objeto")
    changes = models.JSONField(null=True, blank=True, verbose_name="Cambios realizados")

    class Meta:
        verbose_name = "Registro de Auditoría"
        verbose_name_plural = "Registros de Auditoría"
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user} - {self.action} - {self.object_repr} - {self.timestamp}"

class Rubro(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre

class OrdenDeCompra(models.Model):

    numero = models.CharField(max_length=50, unique=True)
    fecha_inicio = models.DateField(verbose_name="Fecha de inicio")
    fecha_fin = models.DateField(verbose_name="Fecha de finalización", null=True, blank=True)
    proveedor = models.CharField(max_length=100, blank=True)
    rubro = models.ForeignKey(Rubro, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Rubro principal")

    def save(self, *args, **kwargs):
        if self.numero:
            self.numero = self.numero.upper()
        if self.proveedor:
            self.proveedor = self.proveedor.upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"OC #{self.numero}"


# Relaciona una orden de compra con los bienes, cantidad, precio y proveedor
class OrdenDeCompraItem(models.Model):
    orden_de_compra = models.ForeignKey('OrdenDeCompra', related_name='items', on_delete=models.CASCADE)
    bien = models.ForeignKey('Bien', on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2)
    precio_total = models.DecimalField(max_digits=14, decimal_places=2)
    renglon = models.IntegerField(default=1)

    def save(self, *args, **kwargs):
        self.precio_total = self.cantidad * self.precio_unitario
        if hasattr(self, 'renglon') and isinstance(self.renglon, str):
            self.renglon = self.renglon.upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.bien} x {self.cantidad} (OC: {self.orden_de_compra})"

class Bien(models.Model):
    rubro = models.ForeignKey(Rubro, on_delete=models.SET_NULL, null=True)
    nombre = models.CharField(max_length=100)
    catalogo = models.CharField(max_length=100, blank=True)
    renglon = models.CharField(max_length=50, blank=True)
    imagen = models.BinaryField(null=True, blank=True, editable=True)  # Campo para almacenar la imagen como blob

    def save(self, *args, **kwargs):
        if self.nombre:
            self.nombre = self.nombre.upper()
        if self.catalogo:
            self.catalogo = self.catalogo.upper()
        if self.renglon:
            self.renglon = self.renglon.upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre

class Servicio(models.Model):
    FRECUENCIA_CHOICES = [
        ('SEMANAL', 'Semanal'),
        ('QUINCENAL', 'Quincenal'),
        ('MENSUAL', 'Mensual'),
    ]

    ESTADO_CHOICES = [
        ('ACTIVO', 'Activo'),
        ('POR_VENCER', 'Por vencer'),
        ('VENCIDO', 'Vencido'),
        ('SUSPENDIDO', 'Suspendido'),
    ]

    nombre = models.CharField(max_length=200, verbose_name="Nombre del servicio")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    proveedor = models.CharField(max_length=100, verbose_name="Proveedor")
    frecuencia = models.CharField(max_length=10, choices=FRECUENCIA_CHOICES, verbose_name="Frecuencia")
    costo_mensual = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Costo mensual")
    fecha_inicio = models.DateField(verbose_name="Fecha de inicio")
    fecha_fin = models.DateField(null=True, blank=True, verbose_name="Fecha de finalización")
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='ACTIVO', verbose_name="Estado")
    rubro = models.ForeignKey(Rubro, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Rubro")
    observaciones = models.TextField(blank=True, verbose_name="Observaciones")

    def save(self, *args, **kwargs):
        if self.nombre:
            self.nombre = self.nombre.upper()
        if self.proveedor:
            self.proveedor = self.proveedor.upper()
        if self.descripcion:
            self.descripcion = self.descripcion.upper()
        if self.observaciones:
            self.observaciones = self.observaciones.upper()
        super().save(*args, **kwargs)

    def calcular_proxima_renovacion(self):
        """Calcula la fecha de próxima renovación basada en la frecuencia"""
        from datetime import timedelta
        if self.frecuencia == 'SEMANAL':
            return self.fecha_inicio + timedelta(weeks=1)
        elif self.frecuencia == 'QUINCENAL':
            return self.fecha_inicio + timedelta(weeks=2)
        elif self.frecuencia == 'MENSUAL':
            from dateutil.relativedelta import relativedelta
            return self.fecha_inicio + relativedelta(months=1)
        return None

    def dias_para_vencimiento(self):
        """Calcula días restantes para vencimiento"""
        from datetime import date
        if self.fecha_fin:
            return (self.fecha_fin - date.today()).days
        return None

    def __str__(self):
        return f"{self.nombre} - {self.proveedor} ({self.get_frecuencia_display()})"

class Almacen(models.Model):
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200)
    responsable = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.nombre:
            self.nombre = self.nombre.upper()
        if self.direccion:
            self.direccion = self.direccion.upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre


class Entrega(models.Model):
    fecha = models.DateTimeField(auto_now_add=True)
    area_persona = models.CharField(max_length=100)
    observaciones = models.TextField(blank=True)
    orden_de_compra = models.ForeignKey(OrdenDeCompra, on_delete=models.SET_NULL, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.area_persona:
            self.area_persona = self.area_persona.upper()
        if self.observaciones:
            self.observaciones = self.observaciones.upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Remito #{self.id} - {self.fecha.date()} - {self.area_persona}"
    
    def total_entrega(self):
        total = 0
        for item in self.items.all():
            total += item.precio_total
        return total

class EntregaItem(models.Model):
    entrega = models.ForeignKey(Entrega, related_name='items', on_delete=models.CASCADE)
    orden_de_compra = models.ForeignKey(OrdenDeCompra, related_name='entrega_items', on_delete=models.SET_NULL, null=True, blank=True)
    bien = models.ForeignKey(Bien, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2)
    precio_total = models.DecimalField(max_digits=14, decimal_places=2)

    def save(self, *args, **kwargs):
        self.precio_total = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.bien} x {self.cantidad}"
