from django.contrib import admin
from .models import Rubro, Bien, OrdenDeCompra, OrdenDeCompraItem, Almacen, Entrega, EntregaItem

admin.site.register(Rubro)
admin.site.register(Bien)
admin.site.register(Almacen)


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
