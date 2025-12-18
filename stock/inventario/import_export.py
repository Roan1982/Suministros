import pandas as pd
from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from .models import Bien, Rubro

def importar_bienes_excel(request):
    if request.method == 'POST' and request.FILES.get('excel_file'):
        excel_file = request.FILES['excel_file']

        try:
            df = pd.read_excel(excel_file)

            importados = 0
            actualizados = 0
            errores = []

            for index, row in df.iterrows():
                try:
                    # Validar campos obligatorios
                    nombre_bien = str(row.get('nombre', '')).strip()
                    if not nombre_bien:
                        errores.append(f"Fila {index+2}: Nombre del bien es obligatorio")
                        continue

                    # Buscar o crear rubro
                    rubro_nombre = str(row.get('rubro', '')).strip()
                    rubro = None
                    if rubro_nombre:
                        rubro, created = Rubro.objects.get_or_create(
                            nombre__iexact=rubro_nombre,
                            defaults={'nombre': rubro_nombre.upper()}
                        )

                    # Verificar si el bien ya existe
                    bien_existente = Bien.objects.filter(nombre__iexact=nombre_bien).first()

                    if bien_existente:
                        # Actualizar bien existente
                        bien_existente.rubro = rubro or bien_existente.rubro
                        bien_existente.catalogo = str(row.get('catalogo', '')).strip().upper() or bien_existente.catalogo
                        bien_existente.renglon = str(row.get('renglon', '')).strip() or bien_existente.renglon
                        bien_existente.save()
                        actualizados += 1
                    else:
                        # Crear nuevo bien
                        Bien.objects.create(
                            nombre=nombre_bien.upper(),
                            rubro=rubro,
                            catalogo=str(row.get('catalogo', '')).strip().upper(),
                            renglon=str(row.get('renglon', '')).strip(),
                        )
                        importados += 1

                except Exception as e:
                    errores.append(f"Fila {index+2}: {str(e)}")

            # Preparar mensaje de resultado
            mensaje = f'Importación completada. '
            if importados > 0:
                mensaje += f'{importados} bienes nuevos importados. '
            if actualizados > 0:
                mensaje += f'{actualizados} bienes actualizados. '
            if errores:
                mensaje += f'{len(errores)} errores encontrados.'

            if errores:
                messages.warning(request, mensaje)
                # Mostrar algunos errores
                for error in errores[:5]:
                    messages.error(request, error)
                if len(errores) > 5:
                    messages.error(request, f'... y {len(errores) - 5} errores más')
            else:
                messages.success(request, mensaje)

        except Exception as e:
            messages.error(request, f'Error al procesar el archivo Excel: {str(e)}')

    return redirect('bienes_list')

def exportar_bienes_excel(request):
    bienes = Bien.objects.select_related('rubro').all()
    
    data = []
    for bien in bienes:
        # Calcular stock
        comprado = bien.ordendecompraitem_set.aggregate(total=Sum('cantidad'))['total'] or 0
        entregado = bien.entregaitem_set.aggregate(total=Sum('cantidad'))['total'] or 0
        stock = comprado - entregado
        
        data.append({
            'Nombre': bien.nombre,
            'Rubro': bien.rubro.nombre if bien.rubro else '',
            'Catálogo': bien.catalogo,
            'Renglón': bien.renglon,
            'Stock': stock,
        })
    
    df = pd.DataFrame(data)
    
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=bienes.xlsx'
    df.to_excel(response, index=False)
    
    return response