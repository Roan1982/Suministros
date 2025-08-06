from .models import Rubro, Bien
# Vista para listar rubros
from django.contrib.auth.decorators import login_required
from django.db.models import Q
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
    bienes = Bien.objects.select_related('rubro').all()
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
    # TODO: Implementar lógica real
    return JsonResponse({'status': 'ok', 'bien_id': bien_id, 'ordenes': []})
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
            row = {
                'Rubro': rubro.nombre,
                'Bien': bien.nombre,
                'Stock': stock,
                'Total Entregado': entregado['total'] or 0,
                'Valor Entregado ($)': float(entregado['total_pesos'] or 0),
            }
            bienes_data.append({
                'bien': bien,
                'stock': stock,
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
        row = {
            'Rubro': bien.rubro.nombre if bien.rubro else '',
            'Bien': bien.nombre,
            'Stock': stock,
            'Total_Entregado': entregado['total'] or 0,
            'Valor_Entregado': float(entregado['total_pesos'] or 0),
        }
        data.append(row)
        excel_rows.append({
            'Rubro': bien.rubro.nombre if bien.rubro else '',
            'Bien': bien.nombre,
            'Stock': stock,
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

    entregas = Entrega.objects.annotate(anio=ExtractYear('fecha'))
    resumen = entregas.values('anio').annotate(
        cantidad=Sum(1),
        total=Sum('items__precio_total')
    ).order_by('anio')

    totales = []
    excel_rows = []
    for row in resumen:
        totales.append({
            'anio': row['anio'],
            'cantidad': row['cantidad'],
            'total': float(row['total'] or 0),
        })
        excel_rows.append({
            'Año': row['anio'],
            'Cantidad de Entregas': row['cantidad'],
            'Monto Total ($)': float(row['total'] or 0),
        })

    # Detalle por rubro y bien del último año
    ultimo_anio = max([r['anio'] for r in totales if r['anio'] is not None], default=None)
    detalle = []
    if ultimo_anio:
        from .models import Bien, Rubro
        items = EntregaItem.objects.filter(entrega__fecha__year=ultimo_anio)
        bienes = Bien.objects.select_related('rubro').all()
        for bien in bienes:
            cantidad = items.filter(bien=bien).aggregate(total=Sum('cantidad'))['total'] or 0
            total = items.filter(bien=bien).aggregate(suma=Sum('precio_total'))['suma'] or 0
            if cantidad > 0:
                detalle.append({
                    'rubro': bien.rubro.nombre if bien.rubro else '',
                    'bien': bien.nombre,
                    'cantidad': cantidad,
                    'total': float(total),
                })

    data = {'totales': totales, 'detalle': detalle, 'ultimo_anio': ultimo_anio}

    if request.GET.get('export') == 'excel':
        # Exportar ambos: totales y detalle
        with pd.ExcelWriter('entregas_por_anio.xlsx', engine='openpyxl') as writer:
            pd.DataFrame(excel_rows).to_excel(writer, sheet_name='Totales por año', index=False)
            pd.DataFrame(detalle).to_excel(writer, sheet_name='Detalle último año', index=False)
            writer.save()
            with open('entregas_por_anio.xlsx', 'rb') as f:
                response = HttpResponse(f.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                response['Content-Disposition'] = 'attachment; filename=entregas_por_anio.xlsx'
                return response

    if request.GET.get('export') == 'pdf':
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename=entregas_por_anio.pdf'
        doc = SimpleDocTemplate(response, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        elements.append(Paragraph('Entregas por Año', styles['Title']))
        elements.append(Spacer(1, 12))
        table_data = [["Año", "Cantidad de Entregas", "Monto Total ($)"]]
        for row in excel_rows:
            table_data.append([row['Año'], row['Cantidad de Entregas'], f"{row['Monto Total ($)']:.2f}"])
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
        elements.append(Paragraph(f'Detalle por rubro y bien (último año: {ultimo_anio})', styles['Heading3']))
        table_data2 = [["Rubro", "Bien", "Cantidad Entregada", "Monto Total ($)"]]
        for row in detalle:
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
    resumen = Entrega.objects.values('area_persona').annotate(
        cantidad=Sum(1),
        total=Sum('items__precio_total')
    ).order_by('area_persona')

    totales = []
    for row in resumen:
        totales.append({
            'area': row['area_persona'],
            'cantidad': row['cantidad'],
            'total': float(row['total'] or 0),
        })

    # Detalle de bienes entregados por área/persona
    detalle_qs = EntregaItem.objects.values('entrega__area_persona', 'bien__nombre').annotate(
        cantidad=Sum('cantidad')
    ).order_by('entrega__area_persona', 'bien__nombre')

    detalle = []
    for row in detalle_qs:
        detalle.append({
            'area': row['entrega__area_persona'],
            'bien': row['bien__nombre'],
            'cantidad': row['cantidad'],
        })

    # Para exportar a Excel
    if request.GET.get('export') == 'excel':
        # Dos hojas: Totales y Detalle
        with pd.ExcelWriter('entregas_por_area_temp.xlsx', engine='openpyxl') as writer:
            df_totales = pd.DataFrame([{ 'Área / Persona': t['area'], 'Cantidad de Entregas': t['cantidad'], 'Monto Total ($)': t['total'] } for t in totales])
            df_detalle = pd.DataFrame([{ 'Área / Persona': d['area'], 'Bien': d['bien'], 'Cantidad Entregada': d['cantidad'] } for d in detalle])
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
        # Detalle
        elements.append(Paragraph('Detalle de bienes entregados', styles['Heading2']))
        table_data2 = [["Área / Persona", "Bien", "Cantidad Entregada"]]
        for d in detalle:
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
        doc.build(elements)
        return response

    return render(request, 'inventario/reporte_entregas_area.html', {'data': {'totales': totales, 'detalle': detalle}})

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

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre'].strip()
        if Rubro.objects.filter(nombre__iexact=nombre).exists():
            raise forms.ValidationError('Ya existe un rubro con ese nombre.')
        return nombre


class BienForm(forms.ModelForm):
    class Meta:
        model = Bien
        fields = ['rubro', 'nombre', 'catalogo']
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
        if rubro and Bien.objects.filter(nombre__iexact=nombre, rubro=rubro).exists():
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

    def clean_numero(self):
        numero = self.cleaned_data['numero']
        if OrdenDeCompra.objects.filter(numero=numero).exists():
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
        self.fields['precio_unitario'].widget = forms.HiddenInput()

@login_required
def dashboard(request):
    from django.db.models import Sum
    from datetime import date, timedelta
    # Órdenes de compra próximas a vencer (fecha_fin dentro de los próximos 4 meses)
    hoy = date.today()
    cuatro_meses = hoy + timedelta(days=120)
    ordenes_vencer = []
    from .models import OrdenDeCompra
    for oc in OrdenDeCompra.objects.exclude(fecha_fin=None):
        if hoy <= oc.fecha_fin <= cuatro_meses:
            ordenes_vencer.append(oc)

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
def agregar_bien(request):
    if request.method == 'POST':
        form = BienForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Bien agregado correctamente.')
            return redirect('dashboard')
    else:
        form = BienForm()
    return render(request, 'inventario/agregar_bien.html', {'form': form, 'titulo': 'Agregar Bien'})



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
