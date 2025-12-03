
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum, F
from django.http import JsonResponse, HttpResponse
from django import forms
from django.forms import inlineformset_factory
from .models import Rubro, Bien, OrdenDeCompra, OrdenDeCompraItem, Entrega, EntregaItem
from django.contrib import messages
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.urls import reverse

@login_required
def api_orden_bien_stock(request, orden_id, bien_id):
    try:
        item = OrdenDeCompraItem.objects.get(orden_de_compra_id=orden_id, bien_id=bien_id)
    except OrdenDeCompraItem.DoesNotExist:
        return JsonResponse({'status': 'error', 'stock': 0})
    entregado = EntregaItem.objects.filter(orden_de_compra_id=orden_id, bien_id=bien_id).aggregate(total=Sum('cantidad'))['total'] or 0
    stock = item.cantidad - entregado
    return JsonResponse({'status': 'ok', 'orden_id': orden_id, 'bien_id': bien_id, 'stock': stock})

@login_required
def api_stock_bien(request, bien_id):
    try:
        bien = Bien.objects.get(pk=bien_id)
    except Bien.DoesNotExist:
        return JsonResponse({'status': 'error', 'stock': 0})
    comprado = OrdenDeCompraItem.objects.filter(bien_id=bien_id).aggregate(total=Sum('cantidad'))['total'] or 0
    entregado = EntregaItem.objects.filter(bien_id=bien_id).aggregate(total=Sum('cantidad'))['total'] or 0
    stock = comprado - entregado
    return JsonResponse({'status': 'ok', 'bien_id': bien_id, 'stock': stock})
@login_required
def rubros_list(request):
    q = request.GET.get('q', '').strip()
    rubros = Rubro.objects.all()
    if q:
        rubros = rubros.filter(nombre__icontains=q)
    rubros = rubros.order_by('nombre')
    return render(request, 'inventario/rubros_list.html', {'rubros': rubros, 'q': q})

# Vista para listar bienes
@login_required
def bienes_list(request):
    q = request.GET.get('q', '').strip()
    rubro_id = request.GET.get('rubro')
    from django.db.models import Sum, F
    # Calcular stock: sum(cantidad comprada) - sum(cantidad entregada)
    bienes = Bien.objects.select_related('rubro').all()
    bienes = bienes.annotate(
        comprado=Sum('ordendecompraitem__cantidad'),
        entregado=Sum('entregaitem__cantidad'),
    )
    
    bienes = bienes.annotate(stock=F('comprado') - F('entregado'))
    if q:
        bienes = bienes.filter(
            Q(nombre__icontains=q) |
            Q(catalogo__icontains=q) |
            Q(renglon__icontains=q)
        )
    if rubro_id:
        bienes = bienes.filter(rubro_id=rubro_id)
    bienes = bienes.order_by('nombre')
    rubros = Rubro.objects.all().order_by('nombre')
    # Paginación
    from django.core.paginator import Paginator, EmptyPage
    paginator = Paginator(bienes, 30)
    page_number = request.GET.get('page')
    try:
        page_number_int = int(page_number) if page_number else 1
    except (TypeError, ValueError):
        page_number_int = 1
    if page_number_int < 1:
        page_number_int = 1
    if page_number_int > paginator.num_pages and paginator.num_pages > 0:
        page_number_int = paginator.num_pages
    try:
        page_obj = paginator.page(page_number_int)
    except EmptyPage:
        page_obj = paginator.page(1)
    return render(request, 'inventario/bienes_list.html', {'page_obj': page_obj, 'q': q, 'rubros': rubros, 'rubro_id': rubro_id})
 
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

# API stub: ordenes con stock para un bien
@login_required
def api_ordenes_con_stock_bien(request, bien_id):
    from .models import OrdenDeCompraItem, OrdenDeCompra, EntregaItem
    from django.db.models import Sum, F
    # Buscar todas las ordenes de compra que tengan ese bien y stock disponible
    # Stock disponible = cantidad comprada - cantidad entregada
    # Primero, obtener todas las ordenes de compra con ese bien
    items = (
        OrdenDeCompraItem.objects
        .filter(bien_id=bien_id)
        .select_related('orden_de_compra')
    )
    ordenes = []
    for item in items:
        # Calcular entregado para esa orden y bien
        entregado = EntregaItem.objects.filter(orden_de_compra=item.orden_de_compra, bien_id=bien_id).aggregate(total=Sum('cantidad'))['total'] or 0
        disponible = item.cantidad - entregado
        if disponible > 0:
            ordenes.append({
                'id': item.orden_de_compra.id,
                'numero': f"OC #{item.orden_de_compra.numero}",
                'disponible': disponible,
                'precio_unitario': str(item.precio_unitario),
            })
    return JsonResponse({'status': 'ok', 'bien_id': bien_id, 'ordenes': ordenes})
from .models import Entrega, OrdenDeCompraItem
# Vista para listar remitos con paginador
from django.urls import reverse
from django.contrib import messages

# Importar Paginator y EmptyPage para paginación robusta
from django.core.paginator import Paginator, EmptyPage

@login_required
def remitos_list(request):
    q = request.GET.get('q', '').strip()
    remitos = Entrega.objects.all()
    if q:
        remitos = remitos.filter(
            Q(area_persona__icontains=q) |
            Q(observaciones__icontains=q)
        )
    remitos = remitos.order_by('-fecha')
    paginator = Paginator(remitos, 20)
    page_number = request.GET.get('page')
    try:
        page_number_int = int(page_number) if page_number else 1
    except (TypeError, ValueError):
        page_number_int = 1
    if page_number_int < 1:
        page_number_int = 1
    if page_number_int > paginator.num_pages and paginator.num_pages > 0:
        page_number_int = paginator.num_pages
    try:
        page_obj = paginator.page(page_number_int)
    except EmptyPage:
        page_obj = paginator.page(1)
    return render(request, 'inventario/remitos_list.html', {'page_obj': page_obj})

# Vista dashboard de reportes (cards)
@login_required
def reportes(request):
    return render(request, 'inventario/reportes.html')

# Vista de reporte personalizado con filtros y resultados
@login_required
def reporte_personalizado(request):
    from .forms import ReportePersonalizadoForm
    from .models import EntregaItem
    from django.db.models import Q
    import pandas as pd
    from django.http import HttpResponse
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet

    # Obtener valores únicos para proveedor y area_persona
    from .models import Entrega, OrdenDeCompra
    proveedores = list(OrdenDeCompra.objects.order_by().values_list('proveedor', flat=True).distinct())
    areas_persona = list(Entrega.objects.order_by().values_list('area_persona', flat=True).distinct())

    form = ReportePersonalizadoForm(request.GET or None)
    resultados = []
    tipo = form.cleaned_data.get('tipo') if form.is_valid() else 'entregados'
    if form.is_valid() and any(form.cleaned_data.values()):
        filtros = Q()
        cd = form.cleaned_data
        from datetime import datetime, time
        from django.utils.timezone import make_aware, is_naive, get_current_timezone
        tz = get_current_timezone()
        if tipo == 'entregados':
            if cd['bien']:
                filtros &= Q(bien=cd['bien'])
            if cd['rubro']:
                filtros &= Q(bien__rubro=cd['rubro'])
            if cd['orden_de_compra']:
                filtros &= Q(orden_de_compra=cd['orden_de_compra'])
            if cd['proveedor']:
                filtros &= Q(orden_de_compra__proveedor__icontains=cd['proveedor'])
            # Manejo correcto de fechas con zona horaria
            if cd['fecha_inicio']:
                dt_inicio = datetime.combine(cd['fecha_inicio'], time.min)
                if is_naive(dt_inicio):
                    dt_inicio = make_aware(dt_inicio, timezone=tz)
                filtros &= Q(entrega__fecha__gte=dt_inicio)
            if cd['fecha_fin']:
                dt_fin = datetime.combine(cd['fecha_fin'], time.max)
                if is_naive(dt_fin):
                    dt_fin = make_aware(dt_fin, timezone=tz)
                filtros &= Q(entrega__fecha__lte=dt_fin)
            if cd['area_persona']:
                filtros &= Q(entrega__area_persona__icontains=cd['area_persona'])
            if cd['precio_unitario_min'] is not None:
                filtros &= Q(precio_unitario__gte=cd['precio_unitario_min'])
            if cd['precio_unitario_max'] is not None:
                filtros &= Q(precio_unitario__lte=cd['precio_unitario_max'])
            qs = EntregaItem.objects.filter(filtros).select_related('bien', 'orden_de_compra', 'entrega', 'bien__rubro')
            from django.utils.timezone import is_aware
            for item in qs:
                fecha = item.entrega.fecha if item.entrega else ''
                fecha_str = ''
                hora_str = ''
                if fecha and hasattr(fecha, 'isoformat'):
                    # Convertir a string sin zona horaria
                    if is_aware(fecha):
                        fecha = fecha.astimezone(None).replace(tzinfo=None)
                    fecha_str = fecha.strftime('%Y-%m-%d')
                    hora_str = fecha.strftime('%H:%M:%S')
                resultados.append({
                    'bien': item.bien.nombre,
                    'rubro': item.bien.rubro.nombre if item.bien.rubro else '',
                    'orden': item.orden_de_compra.numero if item.orden_de_compra else '',
                    'proveedor': item.orden_de_compra.proveedor if item.orden_de_compra else '',
                    'fecha': fecha_str,
                    'hora': hora_str,
                    'area_persona': item.entrega.area_persona if item.entrega else '',
                    'precio_unitario': item.precio_unitario,
                    'cantidad': item.cantidad,
                    'precio_total': item.precio_total,
                })
        elif tipo == 'comprados':
            from .models import OrdenDeCompraItem
            if cd['bien']:
                filtros &= Q(bien=cd['bien'])
            if cd['rubro']:
                filtros &= Q(bien__rubro=cd['rubro'])
            if cd['orden_de_compra']:
                filtros &= Q(orden_de_compra=cd['orden_de_compra'])
            if cd['proveedor']:
                filtros &= Q(orden_de_compra__proveedor__icontains=cd['proveedor'])
            if cd['precio_unitario_min'] is not None:
                filtros &= Q(precio_unitario__gte=cd['precio_unitario_min'])
            if cd['precio_unitario_max'] is not None:
                filtros &= Q(precio_unitario__lte=cd['precio_unitario_max'])
            qs = OrdenDeCompraItem.objects.filter(filtros).select_related('bien', 'orden_de_compra', 'bien__rubro')
            for item in qs:
                resultados.append({
                    'bien': item.bien.nombre,
                    'rubro': item.bien.rubro.nombre if item.bien.rubro else '',
                    'orden': item.orden_de_compra.numero if item.orden_de_compra else '',
                    'proveedor': item.orden_de_compra.proveedor if item.orden_de_compra else '',
                    'precio_unitario': item.precio_unitario,
                    'cantidad': item.cantidad,
                    'precio_total': item.precio_total,
                })
        # Exportar si corresponde
        if request.GET.get('export') == 'excel':
            df = pd.DataFrame(resultados)
            response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename=personalizado.xlsx'
            df.to_excel(response, index=False)
            return response
        if request.GET.get('export') == 'pdf':
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename=personalizado.pdf'
            doc = SimpleDocTemplate(response, pagesize=letter)
            elements = []
            styles = getSampleStyleSheet()
            elements.append(Paragraph('Reporte personalizado', styles['Title']))
            elements.append(Spacer(1, 12))
            if resultados:
                # Encabezados legibles
                headers = [
                    'Bien', 'Rubro', 'Orden', 'Proveedor', 'Fecha', 'Hora', 'Área/Persona', 'Precio unitario', 'Cantidad', 'Precio total'
                ]
                table_data = [headers]
                for row in resultados:
                    table_data.append([
                        row.get('bien',''), row.get('rubro',''), row.get('orden',''), row.get('proveedor',''),
                        row.get('fecha',''), row.get('hora',''), row.get('area_persona',''), row.get('precio_unitario',''),
                        row.get('cantidad',''), row.get('precio_total','')
                    ])
                # Ajustar anchos de columna para que encuadre bien
                # Ajustar anchos para evitar superposición y centrar mejor
                col_widths = [70, 60, 40, 70, 55, 45, 70, 50, 40, 60]
                t = Table(table_data, repeatRows=1, colWidths=col_widths, hAlign='CENTER')
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), colors.grey),
                    ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0,0), (-1,0), 8),
                    ('BACKGROUND', (0,1), (-1,-1), colors.beige),
                    ('GRID', (0,0), (-1,-1), 1, colors.black),
                ]))
                elements.append(t)
            else:
                elements.append(Paragraph('No hay resultados para los filtros seleccionados.', styles['Normal']))
            doc.build(elements)
            return response

    # Paginación backend para resultados si hay datos
    page_obj = None
    if resultados:
        from django.core.paginator import Paginator, EmptyPage
        paginator = Paginator(resultados, 20)
        page_number = request.GET.get('page')
        try:
            page_number_int = int(page_number) if page_number else 1
        except (TypeError, ValueError):
            page_number_int = 1
        if page_number_int < 1:
            page_number_int = 1
        if page_number_int > paginator.num_pages and paginator.num_pages > 0:
            page_number_int = paginator.num_pages
        try:
            page_obj = paginator.page(page_number_int)
        except EmptyPage:
            page_obj = paginator.page(1)
    return render(request, 'inventario/reporte_personalizado.html', {
        'form': form,
        'page_obj': page_obj,
        'request': request,
        'proveedores': proveedores,
        'areas_persona': areas_persona,
    })


    # Paginación backend para resultados si hay datos
    page_obj = None
    if resultados:
        from django.core.paginator import Paginator, EmptyPage
        paginator = Paginator(resultados, 20)
        page_number = request.GET.get('page')
        try:
            page_number_int = int(page_number) if page_number else 1
        except (TypeError, ValueError):
            page_number_int = 1
        if page_number_int < 1:
            page_number_int = 1
        if page_number_int > paginator.num_pages and paginator.num_pages > 0:
            page_number_int = paginator.num_pages
        try:
            page_obj = paginator.page(page_number_int)
        except EmptyPage:
            page_obj = paginator.page(1)
    return render(request, 'inventario/reporte_personalizado.html', {'form': form, 'page_obj': page_obj, 'request': request})

# Alias para compatibilidad con urls.py

# Stubs de reportes (para evitar errores de import hasta implementar cada uno)
@login_required
def reporte_stock_rubro(request):
    from .models import Rubro, Bien, EntregaItem
    from django.db.models import Sum, F, DecimalField, ExpressionWrapper
    import pandas as pd
    from django.http import HttpResponse
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet

    rubros = Rubro.objects.all().order_by('nombre')
    data = []
    excel_rows = []
    for rubro in rubros:
        bienes = Bien.objects.filter(rubro=rubro)
        bienes_data = []
        for bien in bienes:
            comprado = OrdenDeCompraItem.objects.filter(bien=bien).aggregate(total=Sum('cantidad'))['total'] or 0
            entregado = EntregaItem.objects.filter(bien=bien).aggregate(
                total=Sum('cantidad'),
                total_pesos=Sum(ExpressionWrapper(F('cantidad') * F('precio_unitario'), output_field=DecimalField(max_digits=14, decimal_places=2)))
            )
            stock = comprado - (entregado['total'] or 0)
            # Calcular precio_unitario promedio ponderado
            from django.db.models import FloatField
            suma_precio_total = OrdenDeCompraItem.objects.filter(bien=bien).aggregate(
                suma=Sum(ExpressionWrapper(F('cantidad') * F('precio_unitario'), output_field=FloatField()))
            )['suma'] or 0
            cantidad_total = OrdenDeCompraItem.objects.filter(bien=bien).aggregate(total=Sum('cantidad'))['total'] or 0
            precio_unitario_prom = (suma_precio_total / cantidad_total) if cantidad_total else 0
            valor_stock = stock * precio_unitario_prom
            row = {
                'Rubro': rubro.nombre,
                'Bien': bien.nombre,
                'Stock': stock,
                'Valor_Stock': valor_stock,
                'Total Entregado': entregado['total'] or 0,
                'Valor Entregado ($)': float(entregado['total_pesos'] or 0),
            }
            bienes_data.append({
                'bien': bien,
                'stock': stock,
                'valor_stock': valor_stock,
                'entregado': entregado['total'] or 0,
                'valor': entregado['total_pesos'] or 0,
            })
            excel_rows.append(row)
        data.append({'rubro': rubro, 'bienes': bienes_data})

    if request.GET.get('export') == 'excel':
        df = pd.DataFrame(excel_rows)
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=stock_por_rubro.xlsx'
        df.to_excel(response, index=False)
        return response

    if request.GET.get('export') == 'pdf':
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename=stock_por_rubro.pdf'
        doc = SimpleDocTemplate(response, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        elements.append(Paragraph('Estado de Stock por Rubro', styles['Title']))
        elements.append(Spacer(1, 12))
        current_rubro = None
        for row in excel_rows:
            if row['Rubro'] != current_rubro:
                if current_rubro is not None:
                    elements.append(Spacer(1, 12))
                elements.append(Paragraph(f"Rubro: {row['Rubro']}", styles['Heading3']))
                table_data = [["Bien", "Stock", "Total Entregado", "Valor Entregado ($)"]]
                current_rubro = row['Rubro']
            table_data.append([row['Bien'], row['Stock'], row['Total Entregado'], f"{row['Valor Entregado ($)']:.2f}"])
            # Si es el último bien del rubro o el último row, renderizar la tabla
            next_row = excel_rows[excel_rows.index(row)+1] if excel_rows.index(row)+1 < len(excel_rows) else None
            if not next_row or next_row['Rubro'] != current_rubro:
                t = Table(table_data, repeatRows=1)
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), colors.grey),
                    ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0,0), (-1,0), 8),
                    ('BACKGROUND', (0,1), (-1,-1), colors.beige),
                    ('GRID', (0,0), (-1,-1), 1, colors.black),
                ]))
                elements.append(t)
        doc.build(elements)
        return response

    return render(request, 'inventario/reporte_stock_rubro.html', {'data': data})

@login_required
def reporte_stock_bien(request):
    from .models import Bien, EntregaItem, Rubro
    from django.db.models import Sum, F, DecimalField, ExpressionWrapper
    import pandas as pd
    from django.http import HttpResponse
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet

    bienes = Bien.objects.select_related('rubro').all().order_by('rubro__nombre', 'nombre')
    data = []
    excel_rows = []
    for bien in bienes:
        comprado = OrdenDeCompraItem.objects.filter(bien=bien).aggregate(total=Sum('cantidad'))['total'] or 0
        entregado = EntregaItem.objects.filter(bien=bien).aggregate(
            total=Sum('cantidad'),
            total_pesos=Sum(ExpressionWrapper(F('cantidad') * F('precio_unitario'), output_field=DecimalField(max_digits=14, decimal_places=2)))
        )
        stock = comprado - (entregado['total'] or 0)
        from django.db.models import FloatField
        suma_precio_total = OrdenDeCompraItem.objects.filter(bien=bien).aggregate(
            suma=Sum(ExpressionWrapper(F('cantidad') * F('precio_unitario'), output_field=FloatField()))
        )['suma'] or 0
        cantidad_total = OrdenDeCompraItem.objects.filter(bien=bien).aggregate(total=Sum('cantidad'))['total'] or 0
        precio_unitario_prom = (suma_precio_total / cantidad_total) if cantidad_total else 0
        valor_stock = stock * precio_unitario_prom
        row = {
            'Rubro': bien.rubro.nombre if bien.rubro else '',
            'Bien': bien.nombre,
            'Stock': stock,
            'Valor_Stock': valor_stock,
            'Total_Entregado': entregado['total'] or 0,
            'Valor_Entregado': float(entregado['total_pesos'] or 0),
        }
        data.append(row)
        excel_rows.append({
            'Rubro': bien.rubro.nombre if bien.rubro else '',
            'Bien': bien.nombre,
            'Stock': stock,
            'Valor en Stock ($)': valor_stock,
            'Total Entregado': entregado['total'] or 0,
            'Valor Entregado ($)': float(entregado['total_pesos'] or 0),
        })

    # Paginación unificada (debe estar antes de los bloques de exportación)
    paginator = Paginator(data, 20)
    page_number = request.GET.get('page')
    try:
        page_number_int = int(page_number) if page_number else 1
    except (TypeError, ValueError):
        page_number_int = 1
    if page_number_int < 1:
        page_number_int = 1
    if page_number_int > paginator.num_pages and paginator.num_pages > 0:
        page_number_int = paginator.num_pages
    try:
        page_obj = paginator.page(page_number_int)
    except EmptyPage:
        page_obj = paginator.page(1)

    if request.GET.get('export') == 'excel':
        df = pd.DataFrame(excel_rows)
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=stock_por_bien.xlsx'
        df.to_excel(response, index=False)
        return response

    if request.GET.get('export') == 'pdf':
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename=stock_por_bien.pdf'
        doc = SimpleDocTemplate(response, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        elements.append(Paragraph('Estado de Stock por Bien', styles['Title']))
        elements.append(Spacer(1, 12))
        table_data = [["Rubro", "Bien", "Stock", "Total Entregado", "Valor Entregado ($)"]]
        for row in excel_rows:
            table_data.append([row['Rubro'], row['Bien'], row['Stock'], row['Total Entregado'], f"{row['Valor Entregado ($)']:.2f}"])
        t = Table(table_data, repeatRows=1)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 8),
            ('BACKGROUND', (0,1), (-1,-1), colors.beige),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
        ]))
        elements.append(t)
        doc.build(elements)
        return response

    return render(request, 'inventario/reporte_stock_bien.html', {'page_obj': page_obj})

@login_required
def reporte_entregas_anio(request):
    from .models import Entrega, EntregaItem
    from django.db.models import Sum
    import pandas as pd
    from django.http import HttpResponse
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet
    from django.db.models.functions import ExtractYear

    # --- NUEVA IMPLEMENTACIÓN: Totales y detalle por año, rubro y bien ---
    from collections import defaultdict
    from django.db.models import F, DecimalField, ExpressionWrapper
    # --- NUEVA IMPLEMENTACIÓN: solapas por año y exportación filtrada ---
    anio_param = request.GET.get('anio')
    # Totales por año (para tabs)
    resumen = (
        EntregaItem.objects
        .annotate(anio=ExtractYear('entrega__fecha'), subtotal=F('cantidad') * F('precio_unitario'))
        .values('anio')
        .annotate(
            cantidad=Sum('cantidad'),
            total=Sum('subtotal', output_field=DecimalField(max_digits=20, decimal_places=2))
        )
        .order_by('anio')
    )
    totales = []
    for row in resumen:
        totales.append({
            'anio': row['anio'],
            'cantidad': row['cantidad'],
            'total': float(row['total'] or 0),
        })

    # Si hay año seleccionado, filtrar detalle solo para ese año
    if anio_param:
        try:
            anio_int = int(anio_param)
        except Exception:
            anio_int = None
    else:
        anio_int = None

    # Detalle por año, rubro y bien
    items_qs = EntregaItem.objects.select_related('bien__rubro').annotate(anio=ExtractYear('entrega__fecha'), subtotal=F('cantidad') * F('precio_unitario'))
    if anio_int:
        items_qs = items_qs.filter(anio=anio_int)
    items = (
        items_qs
        .values('anio', 'bien__rubro__nombre', 'bien__nombre')
        .annotate(
            cantidad=Sum('cantidad'),
            total=Sum('subtotal', output_field=DecimalField(max_digits=20, decimal_places=2))
        )
        .order_by('anio', 'bien__rubro__nombre', 'bien__nombre')
    )
    detalles_por_anio = defaultdict(list)
    for row in items:
        detalles_por_anio[row['anio']].append({
            'rubro': row['bien__rubro__nombre'],
            'bien': row['bien__nombre'],
            'cantidad': row['cantidad'],
            'total': float(row['total'] or 0),
        })
    detalles_por_anio_list = [
        {'anio': anio, 'detalle': detalles_por_anio[anio]}
        for anio in sorted(detalles_por_anio.keys())
    ]

    # Si hay año seleccionado, mostrar solo ese año en detalles_por_anio_list
    if anio_int:
        detalles_por_anio_list = [d for d in detalles_por_anio_list if d['anio'] == anio_int]

    data = {'totales': totales, 'detalles_por_anio': detalles_por_anio_list, 'anio_seleccionado': anio_int}

    if request.GET.get('export') == 'excel' and anio_int:
        import pandas as pd
        # Exportar solo el año seleccionado
        totales_sel = [t for t in totales if t['anio'] == anio_int]
        detalles_sel = [d for d in detalles_por_anio_list if d['anio'] == anio_int]
        with pd.ExcelWriter(f'entregas_{anio_int}.xlsx', engine='openpyxl') as writer:
            pd.DataFrame([{ 'Año': t['anio'], 'Cantidad de Entregas': t['cantidad'], 'Monto Total ($)': t['total']} for t in totales_sel]).to_excel(writer, sheet_name='Totales', index=False)
            for anio in detalles_sel:
                df = pd.DataFrame(anio['detalle'])
                df.rename(columns={'rubro': 'Rubro', 'bien': 'Bien', 'cantidad': 'Cantidad Entregada', 'total': 'Monto Total ($)'}, inplace=True)
                df.to_excel(writer, sheet_name=f"Detalle {anio['anio']}", index=False)
            writer.save()
            with open(f'entregas_{anio_int}.xlsx', 'rb') as f:
                response = HttpResponse(f.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                response['Content-Disposition'] = f'attachment; filename=entregas_{anio_int}.xlsx'
                return response

    if request.GET.get('export') == 'pdf' and anio_int:
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename=entregas_{anio_int}.pdf'
        doc = SimpleDocTemplate(response, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        elements.append(Paragraph(f'Entregas año {anio_int}', styles['Title']))
        elements.append(Spacer(1, 12))
        totales_sel = [t for t in totales if t['anio'] == anio_int]
        table_data = [["Año", "Cantidad de Entregas", "Monto Total ($)"]]
        for t in totales_sel:
            table_data.append([t['anio'], t['cantidad'], f"{t['total']:.2f}"])
        t = Table(table_data, repeatRows=1)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 8),
            ('BACKGROUND', (0,1), (-1,-1), colors.beige),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 24))
        for anio in detalles_por_anio_list:
            elements.append(Paragraph(f'Detalle por rubro y bien (año: {anio["anio"]})', styles['Heading3']))
            table_data2 = [["Rubro", "Bien", "Cantidad Entregada", "Monto Total ($)"]]
            for row in anio['detalle']:
                table_data2.append([row['rubro'], row['bien'], row['cantidad'], f"{row['total']:.2f}"])
            t2 = Table(table_data2, repeatRows=1)
            t2.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.grey),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0,0), (-1,0), 8),
                ('BACKGROUND', (0,1), (-1,-1), colors.beige),
                ('GRID', (0,0), (-1,-1), 1, colors.black),
            ]))
            elements.append(t2)
            elements.append(Spacer(1, 12))
        doc.build(elements)
        return response

    return render(request, 'inventario/reporte_entregas_anio.html', {'data': data})

@login_required
def reporte_entregas_area(request):
    from .models import Entrega
    from django.db.models import Sum
    import pandas as pd
    from django.http import HttpResponse
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet

    # Totales por área/persona
    from .models import EntregaItem
    from django.db.models.functions import ExtractYear
    totales_qs = Entrega.objects.values('area_persona').annotate(
        cantidad=Sum(1),
        total=Sum('items__precio_total')
    ).order_by('area_persona')
    totales = [
        {'area': row['area_persona'], 'cantidad': row['cantidad'], 'total': float(row['total'] or 0)}
        for row in totales_qs
    ]

    # Detalle por año, área/persona y bien
    detalle_qs = EntregaItem.objects.annotate(
        anio=ExtractYear('entrega__fecha')
    ).values('anio', 'entrega__area_persona', 'bien__nombre').annotate(
        cantidad=Sum('cantidad')
    ).order_by('anio', 'entrega__area_persona', 'bien__nombre')

    # Agrupar para el template: {anio: {detalle: [{area, bien, cantidad}]}}
    from collections import defaultdict
    detalles_por_anio = defaultdict(list)
    for row in detalle_qs:
        detalles_por_anio[row['anio']].append({
            'area': row['entrega__area_persona'],
            'bien': row['bien__nombre'],
            'cantidad': row['cantidad'],
        })
    detalles_por_anio = [
        {'anio': anio, 'detalle': detalles}
        for anio, detalles in sorted(detalles_por_anio.items())
    ]

    # Para exportar a Excel
    if request.GET.get('export') == 'excel':
        with pd.ExcelWriter('entregas_por_area_temp.xlsx', engine='openpyxl') as writer:
            df_totales = pd.DataFrame([{ 'Área / Persona': t['area'], 'Cantidad de Entregas': t['cantidad'], 'Monto Total ($)': t['total'] } for t in totales])
            df_detalle = pd.DataFrame([
                { 'Año': d['anio'], 'Área / Persona': d['area'], 'Bien': d['bien'], 'Cantidad Entregada': d['cantidad'] }
                for d in detalle_qs
            ])
            df_totales.to_excel(writer, sheet_name='Totales', index=False)
            df_detalle.to_excel(writer, sheet_name='Detalle', index=False)
            writer.save()
        with open('entregas_por_area_temp.xlsx', 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename=entregas_por_area.xlsx'
            return response

    # Para exportar a PDF
    if request.GET.get('export') == 'pdf':
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename=entregas_por_area.pdf'
        doc = SimpleDocTemplate(response, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        elements.append(Paragraph('Entregas por Área / Persona', styles['Title']))
        elements.append(Spacer(1, 12))
        # Totales
        elements.append(Paragraph('Totales por área/persona', styles['Heading2']))
        table_data = [["Área / Persona", "Cantidad de Entregas", "Monto Total ($)"]]
        for t in totales:
            table_data.append([t['area'], t['cantidad'], f"{t['total']:.2f}"])
        t1 = Table(table_data, repeatRows=1)
        t1.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 8),
            ('BACKGROUND', (0,1), (-1,-1), colors.beige),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
        ]))
        elements.append(t1)
        elements.append(Spacer(1, 18))
        # Detalle por año
        for anio in detalles_por_anio:
            elements.append(Paragraph(f"Año: {anio['anio']}", styles['Heading3']))
            table_data2 = [["Área / Persona", "Bien", "Cantidad Entregada"]]
            for d in anio['detalle']:
                table_data2.append([d['area'], d['bien'], d['cantidad']])
            t2 = Table(table_data2, repeatRows=1)
            t2.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.grey),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0,0), (-1,0), 8),
                ('BACKGROUND', (0,1), (-1,-1), colors.beige),
                ('GRID', (0,0), (-1,-1), 1, colors.black),
            ]))
            elements.append(t2)
            elements.append(Spacer(1, 12))
        doc.build(elements)
        return response

    return render(request, 'inventario/reporte_entregas_area.html', {'data': {'totales': totales, 'detalles_por_anio': detalles_por_anio}})

@login_required
def reporte_ranking_bienes(request):
    from .models import Bien, EntregaItem
    from django.db.models import Sum
    import pandas as pd
    from django.http import HttpResponse
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet

    ranking = EntregaItem.objects.values('bien__nombre').annotate(
        cantidad=Sum('cantidad'),
        valor=Sum('precio_total')
    ).order_by('-cantidad')

    data = []
    for row in ranking:
        data.append({
            'bien': row['bien__nombre'],
            'cantidad': row['cantidad'],
            'valor': float(row['valor'] or 0),
        })

    if request.GET.get('export') == 'excel':
        df = pd.DataFrame([{ 'Bien': d['bien'], 'Cantidad Entregada': d['cantidad'], 'Valor Total Entregado ($)': d['valor'] } for d in data])
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=ranking_bienes.xlsx'
        df.to_excel(response, index=False)
        return response

    if request.GET.get('export') == 'pdf':
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename=ranking_bienes.pdf'
        doc = SimpleDocTemplate(response, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        elements.append(Paragraph('Ranking de bienes más entregados', styles['Title']))
        elements.append(Spacer(1, 12))
        table_data = [["Bien", "Cantidad Entregada", "Valor Total Entregado ($)"]]
        for d in data:
            table_data.append([d['bien'], d['cantidad'], f"{d['valor']:.2f}"])
        t = Table(table_data, repeatRows=1)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 8),
            ('BACKGROUND', (0,1), (-1,-1), colors.beige),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
        ]))
        elements.append(t)
        doc.build(elements)
        return response

    return render(request, 'inventario/reporte_ranking_bienes.html', {'data': data})

@login_required
def reporte_ranking_proveedores(request):
    from .models import EntregaItem
    from django.db.models import Sum
    import pandas as pd
    from django.http import HttpResponse
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet

    # Agrupar por proveedor (campo de texto en OrdenDeCompra)
    ranking = EntregaItem.objects.values('orden_de_compra__proveedor').annotate(
        cantidad=Sum('cantidad'),
        valor=Sum('precio_total')
    ).order_by('-valor')

    data = []
    for row in ranking:
        data.append({
            'proveedor': row['orden_de_compra__proveedor'] or '(Sin proveedor)',
            'cantidad': row['cantidad'],
            'valor': float(row['valor'] or 0),
        })

    if request.GET.get('export') == 'excel':
        df = pd.DataFrame([{ 'Proveedor': d['proveedor'], 'Cantidad de Bienes Entregados': d['cantidad'], 'Valor Total Entregado ($)': d['valor'] } for d in data])
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=ranking_proveedores.xlsx'
        df.to_excel(response, index=False)
        return response

    if request.GET.get('export') == 'pdf':
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename=ranking_proveedores.pdf'
        doc = SimpleDocTemplate(response, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        elements.append(Paragraph('Ranking de proveedores', styles['Title']))
        elements.append(Spacer(1, 12))
        table_data = [["Proveedor", "Cantidad de Bienes Entregados", "Valor Total Entregado ($)"]]
        for d in data:
            table_data.append([d['proveedor'], d['cantidad'], f"{d['valor']:.2f}"])
        t = Table(table_data, repeatRows=1)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 8),
            ('BACKGROUND', (0,1), (-1,-1), colors.beige),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
        ]))
        elements.append(t)
        doc.build(elements)
        return response

    return render(request, 'inventario/reporte_ranking_proveedores.html', {'data': data})
from django.http import JsonResponse, HttpResponse
from django import forms
from django.forms import inlineformset_factory
from .models import Rubro, Bien, OrdenDeCompra, OrdenDeCompraItem, Entrega, EntregaItem
from django.contrib import messages
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.urls import reverse

@login_required
def ordenes_list(request):
    q = request.GET.get('q', '').strip()
    ordenes_qs = OrdenDeCompra.objects.all()
    if q:
        ordenes_qs = ordenes_qs.filter(
            Q(numero__icontains=q) |
            Q(proveedor__icontains=q)
        )
    ordenes_qs = ordenes_qs.order_by('-fecha_inicio')
    paginator = Paginator(ordenes_qs, 20)
    page_number = request.GET.get('page')
    try:
        page_number_int = int(page_number) if page_number else 1
    except (TypeError, ValueError):
        page_number_int = 1
    if page_number_int < 1:
        page_number_int = 1
    if page_number_int > paginator.num_pages and paginator.num_pages > 0:
        page_number_int = paginator.num_pages
    try:
        page_obj = paginator.page(page_number_int)
    except EmptyPage:
        page_obj = paginator.page(1)
    return render(request, 'inventario/orden_list.html', {'page_obj': page_obj, 'q': q})

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
    import sys
    if request.method == 'POST':
        form = OrdenDeCompraForm(request.POST, instance=orden)
        formset = OrdenItemFormSet(request.POST, instance=orden, prefix='items')
        print("=== DEBUG ORDEN EDITAR ===", file=sys.stderr)
        print("POST data:", dict(request.POST), file=sys.stderr)
        print("form.fecha_inicio value:", form['fecha_inicio'].value(), file=sys.stderr)
        print("form initial:", form.initial, file=sys.stderr)
        if not form.is_valid():
            print("Form errors:", form.errors, file=sys.stderr)
        if not formset.is_valid():
            print("Formset errors:", formset.errors, file=sys.stderr)
            print("Formset non_form_errors:", formset.non_form_errors(), file=sys.stderr)
        if form.is_valid() and formset.is_valid():
            orden = form.save()
            items = formset.save(commit=False)
            for item in items:
                item.orden_de_compra = orden
                item.save()
            # Procesar eliminados y relaciones many-to-many
            formset.save()  # Esto elimina los objetos marcados para borrar
            messages.success(request, 'Orden de compra actualizada correctamente.')
            return redirect('orden_detalle', pk=orden.id)
    else:
        form = OrdenDeCompraForm(instance=orden)
        formset = OrdenItemFormSet(instance=orden, prefix='items')
        print("=== DEBUG ORDEN EDITAR GET ===", file=sys.stderr)
        print("form.fecha_inicio initial:", form.initial.get('fecha_inicio'), file=sys.stderr)
        print("form.fecha_inicio value:", form['fecha_inicio'].value(), file=sys.stderr)
    return render(request, 'inventario/orden_form.html', {
        'form': form,
        'formset': formset,
        'orden': orden,
        'titulo': f'Editar Orden de Compra #{orden.numero}',
        'agregar_bien_url': 'agregar_bien',
    })
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
    renglon = forms.IntegerField(label='Renglón', min_value=1, widget=forms.NumberInput(attrs={'class': 'form-control'}))

    class Meta:
        model = OrdenDeCompraItem
        fields = ['renglon', 'bien', 'cantidad', 'precio_unitario']
        widgets = {
            'bien': forms.Select(attrs={
                'class': 'form-control select2-bien-orden',
                'data-placeholder': 'Seleccione un bien...'
            }),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'precio_unitario': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
        }

from django.contrib import messages
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.urls import reverse


class RubroForm(forms.ModelForm):
    class Meta:
        model = Rubro
        fields = ['nombre']

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre'].strip().upper()
        # Excluir la instancia actual al verificar duplicados (para ediciones)
        qs = Rubro.objects.filter(nombre__iexact=nombre)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Ya existe un rubro con ese nombre.')
        return nombre


class BienForm(forms.ModelForm):
    imagen = forms.FileField(
        required=False,
        label='Imagen del bien',
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'})
    )

    class Meta:
        model = Bien
        fields = ['rubro', 'nombre', 'catalogo', 'imagen']
        widgets = {
            'rubro': forms.Select(attrs={
                'class': 'form-control select2-dropdown',
                'data-placeholder': 'Seleccione un rubro...'
            }),
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'autocomplete': 'off',
                'placeholder': 'Nombre del bien'
            }),
            'catalogo': forms.TextInput(attrs={
                'class': 'form-control',
                'autocomplete': 'off',
                'placeholder': 'Catálogo (opcional)'
            }),
        }

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre'].strip()
        rubro = self.cleaned_data.get('rubro')
        if rubro:
            # Excluir la instancia actual al verificar duplicados (para ediciones)
            qs = Bien.objects.filter(nombre__iexact=nombre, rubro=rubro)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError('Ya existe un bien con ese nombre en este rubro.')
        return nombre


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
        widgets = {
            'numero': forms.TextInput(attrs={'class': 'form-control'}),
            'proveedor': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        import datetime
        instance = kwargs.get('instance', None)
        data = args[0] if args else None
        initial = kwargs.get('initial', {}) or {}
        # Si es edición y no hay data (GET), forzar initial como string yyyy-MM-dd
        if instance and instance.pk and not data:
            if instance.fecha_inicio:
                initial['fecha_inicio'] = instance.fecha_inicio.strftime('%Y-%m-%d')
            if instance.fecha_fin:
                initial['fecha_fin'] = instance.fecha_fin.strftime('%Y-%m-%d')
            kwargs['initial'] = initial
        super().__init__(*args, **kwargs)
        # Si initial viene en formato dd/mm/yyyy, convertir a yyyy-MM-dd
        for field in ['fecha_inicio', 'fecha_fin']:
            val = self.fields[field].initial
            if isinstance(val, (datetime.date, datetime.datetime)):
                self.fields[field].initial = val.strftime('%Y-%m-%d')
            elif isinstance(val, str) and '/' in val:
                try:
                    d = datetime.datetime.strptime(val, '%d/%m/%Y')
                    self.fields[field].initial = d.strftime('%Y-%m-%d')
                except Exception:
                    self.fields[field].initial = None

    def clean_numero(self):
        numero = self.cleaned_data['numero']
        # Excluir la instancia actual al verificar duplicados (para ediciones)
        qs = OrdenDeCompra.objects.filter(numero=numero)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Ya existe una orden de compra con ese número.')
        return numero


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
        self.fields['precio_unitario'].required = False
        self.fields['precio_unitario'].widget = forms.HiddenInput()
        
        # Filtrar bienes que tienen stock disponible (sin considerar uso en otras filas por ahora)
        bienes_con_stock = []
        for bien in Bien.objects.all():
            # Calcular stock total del bien
            comprado = OrdenDeCompraItem.objects.filter(bien=bien).aggregate(total=Sum('cantidad'))['total'] or 0
            entregado = EntregaItem.objects.filter(bien=bien).aggregate(total=Sum('cantidad'))['total'] or 0
            stock_disponible = comprado - entregado
            
            if stock_disponible > 0:
                bienes_con_stock.append(bien.id)
        
        # Aplicar el filtro al queryset del campo bien
        self.fields['bien'].queryset = Bien.objects.filter(id__in=bienes_con_stock)

@login_required
def dashboard(request):
    from django.db.models import Sum
    from datetime import date, timedelta
    # Órdenes de compra próximas a vencer y vencidas (fecha_fin dentro de los próximos 4 meses o ya vencidas)
    hoy = date.today()
    cuatro_meses = hoy + timedelta(days=120)
    ordenes_vencer = []
    from .models import OrdenDeCompra
    for oc in OrdenDeCompra.objects.exclude(fecha_fin=None):
        if oc.fecha_fin <= cuatro_meses:
            dias_restantes = (oc.fecha_fin - hoy).days
            ordenes_vencer.append({
                'oc': oc,
                'fecha_inicio': oc.fecha_inicio,
                'dias_restantes': dias_restantes
            })

    # Productos bajos de stock (stock <= 10)
    bienes = Bien.objects.all()
    bajos_stock = []
    for bien in bienes:
        comprado = OrdenDeCompraItem.objects.filter(bien=bien).aggregate(total=Sum('cantidad'))['total'] or 0
        entregado = EntregaItem.objects.filter(bien=bien).aggregate(total=Sum('cantidad'))['total'] or 0
        stock_actual = comprado - entregado
        if stock_actual <= 10:
            bajos_stock.append({'bien': bien, 'stock': stock_actual})

    bajos_stock = sorted(bajos_stock, key=lambda x: x['stock'])
    return render(request, 'inventario/dashboard.html', {
        'ordenes_vencer': ordenes_vencer,
        'bajos_stock': bajos_stock
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
    return render(request, 'inventario/agregar_rubro.html', {'form': form, 'titulo': 'Agregar Rubro'})

@login_required
def editar_rubro(request, pk):
    rubro = get_object_or_404(Rubro, pk=pk)
    if request.method == 'POST':
        form = RubroForm(request.POST, instance=rubro)
        if form.is_valid():
            form.save()
            messages.success(request, 'Rubro actualizado correctamente.')
            return redirect('rubros_list')
    else:
        form = RubroForm(instance=rubro)
    return render(request, 'inventario/agregar_rubro.html', {'form': form, 'titulo': 'Editar Rubro', 'editando': True, 'rubro': rubro})

@login_required
def agregar_bien(request):
    if request.method == 'POST':
        form = BienForm(request.POST, request.FILES)
        if form.is_valid():
            bien = form.save(commit=False)
            if 'imagen' in request.FILES:
                bien.imagen = request.FILES['imagen'].read()
            bien.save()
            messages.success(request, 'Bien agregado correctamente.')
            return redirect('dashboard')
    else:
        form = BienForm()
    return render(request, 'inventario/agregar_bien.html', {'form': form, 'titulo': 'Agregar Bien'})

@login_required
def editar_bien(request, pk):
    bien = get_object_or_404(Bien, pk=pk)
    if request.method == 'POST':
        form = BienForm(request.POST, request.FILES, instance=bien)
        if form.is_valid():
            bien = form.save(commit=False)
            if 'imagen' in request.FILES:
                bien.imagen = request.FILES['imagen'].read()
            bien.save()
            messages.success(request, 'Bien actualizado correctamente.')
            return redirect('bienes_list')
    else:
        form = BienForm(instance=bien)
    return render(request, 'inventario/agregar_bien.html', {'form': form, 'titulo': 'Editar Bien', 'editando': True, 'bien': bien})



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
        
        # Validaciones personalizadas adicionales
        validation_errors = False
        if form.is_valid() and formset.is_valid():
            # Validar que todos los ítems tengan orden de compra y stock antes de guardar
            for item_form in formset.forms:
                if item_form.cleaned_data and not item_form.cleaned_data.get('DELETE', False):
                    orden_de_compra = item_form.cleaned_data.get('orden_de_compra')
                    bien = item_form.cleaned_data.get('bien')
                    cantidad = item_form.cleaned_data.get('cantidad', 0)
                    
                    # Validar que todos los ítems tengan orden de compra
                    if bien and cantidad > 0:
                        if not orden_de_compra:
                            item_form.add_error('orden_de_compra', 
                                f'{bien.nombre} no tiene Stock o no se seleccionó una orden de compra.')
                                
                            validation_errors = True
                            print(f"Error de validación: Falta orden de compra para {bien.nombre}")
                        else:
                            # Si hay orden de compra, validar stock
                            # Obtener stock disponible
                            try:
                                oc_item = OrdenDeCompraItem.objects.get(orden_de_compra=orden_de_compra, bien=bien)
                                # Calcular stock disponible (comprado - ya entregado)
                                ya_entregado = EntregaItem.objects.filter(
                                    orden_de_compra=orden_de_compra, 
                                    bien=bien
                                ).aggregate(total=Sum('cantidad'))['total'] or 0
                                
                                stock_disponible = oc_item.cantidad - ya_entregado
                                
                                if cantidad > stock_disponible:
                                    # Agregar error al formulario
                                    item_form.add_error('cantidad', 
                                        f'La cantidad ({cantidad}) excede el stock disponible ({stock_disponible}) para {bien.nombre}')
                                    validation_errors = True
                                    print(f"Error de validación: Cantidad excede stock para {bien.nombre}")
                            except OrdenDeCompraItem.DoesNotExist:
                                item_form.add_error('orden_de_compra', 
                                    f'No se encontró la orden de compra para {bien.nombre}')
                                validation_errors = True
                                print(f"Error de validación: Orden de compra no encontrada para {bien.nombre}")
            
            print("Errores de validación encontrados:", validation_errors)
        
        if form.is_valid() and formset.is_valid() and not validation_errors:
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
                else:
                    # Si no hay orden de compra, usar precio 0 o el precio que ya viene del formulario
                    if item.precio_unitario is None:
                        item.precio_unitario = 0
                    print(f"Sin orden de compra para item {i}, usando precio {item.precio_unitario}")
                item.precio_total = item.cantidad * item.precio_unitario
                item.save()
                print(f"Item {i} guardado con precio_total: {item.precio_total}")
            formset.save_m2m()
            print("Items guardados exitosamente")
            messages.success(request, 'Entrega registrada y stock actualizado.')
            # AJAX support: if request is AJAX, return JSON with URLs
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                from django.urls import reverse
                from django.http import JsonResponse
                return JsonResponse({
                    'success': True,
                    'remito_print_url': reverse('remito_print', args=[entrega.id]),
                    'remitos_list_url': reverse('remitos_list'),
                })
            else:
                return redirect(reverse('remito_print', args=[entrega.id]))
        else:
            # Si hay errores de validación o el formulario es inválido
            print("No se puede guardar: errores de validación encontrados")
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                from django.http import JsonResponse
                errors = {
                    'form': form.errors,
                    'formset': formset.errors,
                    'non_form_errors': formset.non_form_errors(),
                }
                return JsonResponse({'success': False, 'errors': errors})
    else:
        form = EntregaForm()
        formset = EntregaItemFormSet()
    return render(request, 'inventario/entrega_form.html', {'form': form, 'formset': formset})

@login_required
def editar_entrega(request, pk):
    entrega = get_object_or_404(Entrega, pk=pk)
    EntregaItemFormSet = forms.inlineformset_factory(
        Entrega, EntregaItem, form=EntregaItemForm, extra=0, can_delete=True
    )
    
    if request.method == 'POST':
        print("=== DEBUG EDITAR ENTREGA ===")
        print("POST data:", dict(request.POST))
        
        form = EntregaForm(request.POST, instance=entrega)
        formset = EntregaItemFormSet(request.POST, instance=entrega)
        
        print("Form válido:", form.is_valid())
        print("Formset válido:", formset.is_valid())
        
        if not formset.is_valid():
            print("Errores del formset:", formset.errors)
            print("Errores no form del formset:", formset.non_form_errors())
        
        # Validaciones personalizadas adicionales para edición
        validation_errors = False
        if form.is_valid() and formset.is_valid():
            # Validar que todos los ítems tengan orden de compra y stock antes de guardar (para ediciones)
            for item_form in formset.forms:
                if item_form.cleaned_data and not item_form.cleaned_data.get('DELETE', False):
                    orden_de_compra = item_form.cleaned_data.get('orden_de_compra')
                    bien = item_form.cleaned_data.get('bien')
                    cantidad = item_form.cleaned_data.get('cantidad', 0)
                    
                    # Validar que todos los ítems tengan orden de compra
                    if bien and cantidad > 0:
                        if not orden_de_compra:
                            item_form.add_error('orden_de_compra', 
                                f'Debe seleccionar una orden de compra para {bien.nombre} o {bien.nombre} no tiene Stock')
                            validation_errors = True
                            print(f"Error de validación (editar): Falta orden de compra para {bien.nombre}")
                        else:
                            # Si hay orden de compra, validar stock
                            # Obtener stock disponible
                            try:
                                oc_item = OrdenDeCompraItem.objects.get(orden_de_compra=orden_de_compra, bien=bien)
                                # Calcular stock disponible (comprado - ya entregado, excluyendo este item si existe)
                                ya_entregado = EntregaItem.objects.filter(
                                    orden_de_compra=orden_de_compra, 
                                    bien=bien
                                ).exclude(
                                    pk=item_form.instance.pk if item_form.instance.pk else None
                                ).aggregate(total=Sum('cantidad'))['total'] or 0
                                
                                stock_disponible = oc_item.cantidad - ya_entregado
                                
                                if cantidad > stock_disponible:
                                    # Agregar error al formulario
                                    item_form.add_error('cantidad', 
                                        f'La cantidad ({cantidad}) excede el stock disponible ({stock_disponible}) para {bien.nombre}')
                                    validation_errors = True
                                    print(f"Error de validación (editar): Cantidad excede stock para {bien.nombre}")
                            except OrdenDeCompraItem.DoesNotExist:
                                item_form.add_error('orden_de_compra', 
                                    f'No se encontró la orden de compra para {bien.nombre}')
                                validation_errors = True
                                print(f"Error de validación (editar): Orden de compra no encontrada para {bien.nombre}")
            
            print("Errores de validación encontrados (editar):", validation_errors)
        
        if form.is_valid() and formset.is_valid() and not validation_errors:
                entrega = form.save()
                items = formset.save(commit=False)
                
                # Eliminar items marcados para borrar
                for obj in formset.deleted_objects:
                    obj.delete()
                
                print("Items a guardar/actualizar:", len(items))
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
                    else:
                        # Si no hay orden de compra, usar precio 0 o el precio que ya viene del formulario
                        if item.precio_unitario is None:
                            item.precio_unitario = 0
                        print(f"Sin orden de compra para item {i}, usando precio {item.precio_unitario}")
                    
                    item.precio_total = item.cantidad * item.precio_unitario
                    item.save()
                    print(f"Item {i} guardado con precio_total: {item.precio_total}")
                
                formset.save_m2m()
                print("Items actualizados exitosamente")
                messages.success(request, 'Remito actualizado correctamente.')
                
                # AJAX support: if request is AJAX, return JSON with URLs
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    from django.urls import reverse
                    from django.http import JsonResponse
                    return JsonResponse({
                        'success': True,
                        'remito_print_url': reverse('remito_print', args=[entrega.id]),
                        'remitos_list_url': reverse('remitos_list'),
                    })
                else:
                    return redirect(reverse('remito_print', args=[entrega.id]))
        else:
            # Si hay errores de validación o el formulario es inválido (editar)
            print("No se puede actualizar: errores de validación encontrados")
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                from django.http import JsonResponse
                errors = {
                    'form': form.errors,
                    'formset': formset.errors,
                    'non_form_errors': formset.non_form_errors(),
                }
                return JsonResponse({'success': False, 'errors': errors})
    else:
        form = EntregaForm(instance=entrega)
        formset = EntregaItemFormSet(instance=entrega)
    
    return render(request, 'inventario/entrega_form.html', {
        'form': form, 
        'formset': formset,
        'entrega': entrega,  # Para saber que estamos editando
        'titulo': f'Editar Remito #{entrega.id}'
    })

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
