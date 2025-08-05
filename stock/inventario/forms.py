from django import forms
from .models import Bien, Rubro, OrdenDeCompra, Entrega, EntregaItem


class ReportePersonalizadoForm(forms.Form):
    TIPO_REPORTE = (
        ("entregados", "Entregados"),
        ("comprados", "Comprados"),
    )
    tipo = forms.ChoiceField(choices=TIPO_REPORTE, required=True, label="Tipo de reporte", initial="entregados")
    bien = forms.ModelChoiceField(queryset=Bien.objects.all(), required=False, label="Bien")
    rubro = forms.ModelChoiceField(queryset=Rubro.objects.all(), required=False, label="Rubro")
    orden_de_compra = forms.ModelChoiceField(queryset=OrdenDeCompra.objects.all(), required=False, label="Orden de Compra")
    proveedor = forms.ModelChoiceField(
        queryset=OrdenDeCompra.objects.order_by('proveedor').values_list('proveedor', flat=True).distinct().exclude(proveedor=''),
        required=False,
        label="Proveedor"
    )
    fecha_inicio = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}), label="Fecha desde")
    fecha_fin = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}), label="Fecha hasta")
    area_persona = forms.ModelChoiceField(
        queryset=Entrega.objects.order_by('area_persona').values_list('area_persona', flat=True).distinct().exclude(area_persona=''),
        required=False,
        label="Área / Persona"
    )
    precio_unitario_min = forms.DecimalField(required=False, decimal_places=2, max_digits=12, label="Precio unitario desde")
    precio_unitario_max = forms.DecimalField(required=False, decimal_places=2, max_digits=12, label="Precio unitario hasta")
