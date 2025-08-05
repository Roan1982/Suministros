from django import forms
from .models import Bien, Rubro, OrdenDeCompra, Entrega, EntregaItem


class ReportePersonalizadoForm(forms.Form):
    TIPO_REPORTE = (
        ("entregados", "Entregados"),
        ("comprados", "Comprados"),
    )
    tipo = forms.ChoiceField(choices=TIPO_REPORTE, required=True, label="Tipo de reporte", initial="entregados")
    bien = forms.ModelChoiceField(
        queryset=Bien.objects.all(), required=False, label="Bien",
        widget=forms.Select(attrs={'class': 'form-control select2-dropdown', 'data-placeholder': 'Seleccione bien...'}),
    )
    rubro = forms.ModelChoiceField(
        queryset=Rubro.objects.all(), required=False, label="Rubro",
        widget=forms.Select(attrs={'class': 'form-control select2-dropdown', 'data-placeholder': 'Seleccione rubro...'}),
    )
    orden_de_compra = forms.ModelChoiceField(
        queryset=OrdenDeCompra.objects.all(), required=False, label="Orden de Compra",
        widget=forms.Select(attrs={'class': 'form-control select2-dropdown', 'data-placeholder': 'Seleccione orden...'}),
    )
    proveedor = forms.CharField(
        required=False,
        label="Proveedor",
        widget=forms.TextInput(attrs={
            'class': 'form-control select2-text',
            'data-placeholder': 'Buscar proveedor...',
            'autocomplete': 'off',
        }),
        error_messages={
            'invalid_choice': 'Seleccione un proveedor válido.',
            'invalid': 'Ingrese un texto válido para proveedor.'
        }
    )
    fecha_inicio = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}), label="Fecha desde")
    fecha_fin = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}), label="Fecha hasta")
    area_persona = forms.CharField(
        required=False,
        label="Área / Persona",
        widget=forms.TextInput(attrs={
            'class': 'form-control select2-text',
            'data-placeholder': 'Buscar área/persona...',
            'autocomplete': 'off',
        }),
        error_messages={
            'invalid': 'Ingrese un texto válido para área/persona.'
        }
    )
    precio_unitario_min = forms.DecimalField(required=False, decimal_places=2, max_digits=12, label="Precio unitario desde")
    precio_unitario_max = forms.DecimalField(required=False, decimal_places=2, max_digits=12, label="Precio unitario hasta")
