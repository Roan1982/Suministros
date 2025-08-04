from django.db import models
from django.contrib.auth.models import User

class Rubro(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre

class OrdenDeCompra(models.Model):

    numero = models.CharField(max_length=50, unique=True)
    fecha_inicio = models.DateField(verbose_name="Fecha de inicio")
    fecha_fin = models.DateField(verbose_name="Fecha de finalización", null=True, blank=True)
    proveedor = models.CharField(max_length=100, blank=True)

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
