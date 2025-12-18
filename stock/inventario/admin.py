from django.contrib import admin
from .models import Rubro, Bien, Servicio, OrdenDeCompra, OrdenDeCompraItem, Almacen, Entrega, EntregaItem, ServicioPago, AuditLog

admin.site.register(Rubro)
admin.site.register(Bien)
admin.site.register(Almacen)

@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ("nombre", "proveedor", "frecuencia", "costo_mensual", "estado", "fecha_inicio", "fecha_fin", "dias_para_vencimiento")
    list_filter = ("estado", "frecuencia", "rubro", "proveedor")
    search_fields = ("nombre", "proveedor", "descripcion")
    date_hierarchy = "fecha_inicio"
    readonly_fields = ("dias_para_vencimiento",)

    def dias_para_vencimiento(self, obj):
        return obj.dias_para_vencimiento()
    dias_para_vencimiento.short_description = "Días para vencimiento"


class EntregaItemInline(admin.TabularInline):
    model = EntregaItem
    extra = 1

@admin.register(Entrega)
class EntregaAdmin(admin.ModelAdmin):
    inlines = [EntregaItemInline]
    list_display = ("id", "fecha", "area_persona", "orden_de_compra")
    search_fields = ("area_persona", "orden_de_compra__numero")
    date_hierarchy = "fecha"

class OrdenDeCompraItemInline(admin.TabularInline):
    model = OrdenDeCompraItem
    extra = 1

@admin.register(OrdenDeCompra)
class OrdenDeCompraAdmin(admin.ModelAdmin):
    inlines = [OrdenDeCompraItemInline]
    list_display = ("numero", "fecha_inicio", "fecha_fin", "proveedor")
    search_fields = ("numero", "proveedor")
    date_hierarchy = "fecha_inicio"

admin.site.register(ServicioPago)
admin.site.register(AuditLog)
