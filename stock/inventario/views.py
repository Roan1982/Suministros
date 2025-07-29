from django.db.models import F, Sum
# API para AJAX: órdenes de compra con stock disponible para un bien
from django.http import JsonResponse

def api_ordenes_con_stock_bien(request, bien_id):
    # Buscar órdenes de compra con stock disponible para el bien
    # Stock disponible = cantidad comprada - cantidad entregada
    items = (
        OrdenDeCompraItem.objects
        .filter(bien_id=bien_id)
        .annotate(
            entregado=Sum('orden_de_compra__entrega_items__cantidad', filter=models.Q(orden_de_compra__entrega_items__bien_id=bien_id))
        )
    )
    ordenes = []
    for item in items:
        entregado = item.entregado or 0
        disponible = item.cantidad - entregado
        if disponible > 0:
            ordenes.append({
                'id': item.orden_de_compra.id,
                'numero': str(item.orden_de_compra),
                'disponible': disponible
            })
    return JsonResponse({'ordenes': ordenes})
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django import forms
from django.forms import inlineformset_factory
from .models import Rubro, Bien, OrdenDeCompra, OrdenDeCompraItem, Entrega, EntregaItem
from django.contrib import messages
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.urls import reverse

# Listado de órdenes de compra
@login_required
def ordenes_list(request):
    ordenes = OrdenDeCompra.objects.all().order_by('-fecha_inicio')
    return render(request, 'inventario/orden_list.html', {'ordenes': ordenes})

# Detalle de una orden de compra
@login_required
def orden_detalle(request, pk):
    orden = get_object_or_404(OrdenDeCompra, pk=pk)
    return render(request, 'inventario/orden_detalle.html', {'orden': orden})

# Edición de una orden de compra y sus ítems
@login_required
def orden_editar(request, pk):
    orden = get_object_or_404(OrdenDeCompra, pk=pk)
    OrdenItemFormSet = inlineformset_factory(OrdenDeCompra, OrdenDeCompraItem, form=OrdenDeCompraItemForm, extra=0, can_delete=True)
    if request.method == 'POST':
        form = OrdenDeCompraForm(request.POST, instance=orden)
        formset = OrdenItemFormSet(request.POST, instance=orden)
        print('POST data:', request.POST)
        print('Form valido:', form.is_valid())
        print('Formset valido:', formset.is_valid())
        print('Form errors:', form.errors)
        print('Formset errors:', formset.errors)
        print('Formset non_form_errors:', formset.non_form_errors())
        if form.is_valid() and formset.is_valid():
            orden = form.save()
            items = formset.save(commit=False)
            for item in items:
                item.orden_de_compra = orden
                item.save()
            formset.save_m2m()
            messages.success(request, 'Orden de compra actualizada correctamente.')
            return redirect('orden_detalle', pk=orden.id)
    else:
        form = OrdenDeCompraForm(instance=orden)
        formset = OrdenItemFormSet(instance=orden)
    return render(request, 'inventario/orden_editar.html', {'form': form, 'formset': formset, 'orden': orden})
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

# API para AJAX: bienes de la orden
@login_required
def api_orden_bienes(request, orden_id):
    bienes = OrdenDeCompraItem.objects.filter(orden_de_compra_id=orden_id)
    data = {'bienes': [
        {'id': item.bien.id, 'nombre': str(item.bien)} for item in bienes
    ]}
    return JsonResponse(data)

# API para AJAX: precio unitario de bien en orden
@login_required
def api_orden_precio(request, orden_id, bien_id):
    try:
        item = OrdenDeCompraItem.objects.get(orden_de_compra_id=orden_id, bien_id=bien_id)
        precio = str(item.precio_unitario)
    except OrdenDeCompraItem.DoesNotExist:
        precio = ''
    return JsonResponse({'precio': precio})
from django.contrib.auth.decorators import login_required
from django import forms
from .models import Rubro, Bien, OrdenDeCompra, OrdenDeCompraItem, Entrega, EntregaItem

class OrdenDeCompraItemForm(forms.ModelForm):
    renglon = forms.IntegerField(label='Renglón', min_value=1)

    class Meta:
        model = OrdenDeCompraItem
        fields = ['renglon', 'bien', 'cantidad', 'precio_unitario']

from django.contrib import messages
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.urls import reverse

class RubroForm(forms.ModelForm):
    class Meta:
        model = Rubro
        fields = ['nombre']

class BienForm(forms.ModelForm):
    class Meta:
        model = Bien
        fields = ['rubro', 'nombre', 'catalogo']

class OrdenDeCompraForm(forms.ModelForm):
    fecha_inicio = forms.DateField(
        label="Fecha de inicio",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        input_formats=['%Y-%m-%d', '%d/%m/%Y']
    )
    fecha_fin = forms.DateField(
        label="Fecha de finalización",
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        input_formats=['%Y-%m-%d', '%d/%m/%Y']
    )

    class Meta:
        model = OrdenDeCompra
        fields = ['numero', 'fecha_inicio', 'fecha_fin', 'proveedor']


class EntregaForm(forms.ModelForm):
    class Meta:
        model = Entrega
        fields = ['area_persona', 'observaciones', 'orden_de_compra']



class EntregaItemForm(forms.ModelForm):
    class Meta:
        model = EntregaItem
        fields = ['orden_de_compra', 'bien', 'cantidad', 'precio_unitario']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['precio_unitario'].widget = forms.HiddenInput()

@login_required
def dashboard(request):
    from django.db.models import Sum
    entregas = Entrega.objects.order_by('-fecha')[:10]
    bienes = Bien.objects.all()
    stock_data = []
    for bien in bienes:
        comprado = OrdenDeCompraItem.objects.filter(bien=bien).aggregate(total=Sum('cantidad'))['total'] or 0
        entregado = EntregaItem.objects.filter(bien=bien).aggregate(total=Sum('cantidad'))['total'] or 0
        stock_actual = comprado - entregado
        stock_data.append({'bien': bien, 'stock': stock_actual})
    return render(request, 'inventario/dashboard.html', {
        'entregas': entregas,
        'stock_data': stock_data
    })

@login_required
def agregar_rubro(request):
    if request.method == 'POST':
        form = RubroForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Rubro agregado correctamente.')
            return redirect('dashboard')
    else:
        form = RubroForm()
    return render(request, 'inventario/form.html', {'form': form, 'titulo': 'Agregar Rubro'})

@login_required
def agregar_bien(request):
    if request.method == 'POST':
        form = BienForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Bien agregado correctamente.')
            return redirect('dashboard')
    else:
        form = BienForm()
    return render(request, 'inventario/form.html', {'form': form, 'titulo': 'Agregar Bien'})



# Vista para crear orden de compra con ítems
from django import forms
from django.forms import inlineformset_factory

@login_required
def agregar_orden(request):
    OrdenItemFormSet = inlineformset_factory(OrdenDeCompra, OrdenDeCompraItem, form=OrdenDeCompraItemForm, extra=1, can_delete=True)
    if request.method == 'POST':
        form = OrdenDeCompraForm(request.POST)
        formset = OrdenItemFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            orden = form.save()
            items = formset.save(commit=False)
            for item in items:
                item.orden_de_compra = orden
                item.save()
            formset.save_m2m()
            messages.success(request, 'Orden de compra agregada correctamente.')
            return redirect('dashboard')
    else:
        form = OrdenDeCompraForm()
        formset = OrdenItemFormSet()
    return render(request, 'inventario/orden_form.html', {
        'form': form,
        'formset': formset,
        'titulo': 'Agregar Orden de Compra',
        'agregar_bien_url': 'agregar_bien',
    })

@login_required

@login_required
def crear_entrega(request):
    EntregaItemFormSet = forms.inlineformset_factory(
        Entrega, EntregaItem, form=EntregaItemForm, extra=1, can_delete=True
    )
    if request.method == 'POST':
        print("=== DEBUG BACKEND ===")
        print("POST data:", dict(request.POST))
        
        # Buscar el prefijo correcto
        for key in request.POST.keys():
            if 'TOTAL_FORMS' in key:
                prefix = key.replace('-TOTAL_FORMS', '')
                print(f"Prefijo detectado: '{prefix}'")
                break
        
        form = EntregaForm(request.POST)
        formset = EntregaItemFormSet(request.POST or None)
        
        print("Form válido:", form.is_valid())
        print("Formset válido:", formset.is_valid())
        if not formset.is_valid():
            print("Errores del formset:", formset.errors)
            print("Errores no form del formset:", formset.non_form_errors())
        
        if form.is_valid() and formset.is_valid():
            entrega = form.save()
            items = formset.save(commit=False)
            print("Items a guardar:", len(items))
            for i, item in enumerate(items):
                print(f"Item {i}: bien={item.bien}, cantidad={item.cantidad}, orden={item.orden_de_compra}")
                item.entrega = entrega
                # Obtener el precio_unitario de la orden de compra seleccionada para cada item
                if item.orden_de_compra:
                    try:
                        oc_item = OrdenDeCompraItem.objects.get(orden_de_compra=item.orden_de_compra, bien=item.bien)
                        item.precio_unitario = oc_item.precio_unitario
                        print(f"Precio encontrado para item {i}: {item.precio_unitario}")
                    except OrdenDeCompraItem.DoesNotExist:
                        item.precio_unitario = 0
                        print(f"Precio no encontrado para item {i}, usando 0")
                item.precio_total = item.cantidad * item.precio_unitario
                item.save()
                print(f"Item {i} guardado con precio_total: {item.precio_total}")
            formset.save_m2m()
            print("Items guardados exitosamente")
            messages.success(request, 'Entrega registrada y stock actualizado.')
            return redirect(reverse('remito_print', args=[entrega.id]))
    else:
        form = EntregaForm()
        formset = EntregaItemFormSet()
    return render(request, 'inventario/entrega_form.html', {'form': form, 'formset': formset})

@login_required
def remito_pdf(request, pk):
    entrega = get_object_or_404(Entrega, pk=pk)
    template = get_template('inventario/remito_pdf.html')
    html = template.render({'entrega': entrega})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="remito_{entrega.id}.pdf"'
    pisa.CreatePDF(html, dest=response)
    return response

@login_required
def remito_print(request, pk):
    entrega = get_object_or_404(Entrega, pk=pk)
    return render(request, 'inventario/remito_pdf.html', {'entrega': entrega, 'imprimir': True})
