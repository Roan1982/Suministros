// Script para filtrar órdenes de compra según el bien seleccionado en cada fila del formset de entrega
// Requiere que el campo bien tenga la clase 'bien-select' y el campo orden de compra la clase 'orden-select'
document.addEventListener('DOMContentLoaded', function() {
    function attachBienChangeHandler(row) {
        const bienSelect = row.querySelector('.bien-select');
        const ordenSelect = row.querySelector('.orden-select');
        if (bienSelect && ordenSelect) {
            // Elementos para precio
            const precioInput = row.querySelector('input[type="hidden"][name$="-precio_unitario"]');
            const precioCell = row.querySelector('.precio-unitario-cell');

            // Actualiza el precio unitario en el input oculto y en la celda
            function actualizarPrecio() {
                const bienId = bienSelect.value;
                const ordenId = ordenSelect.value;
                if (bienId && ordenId) {
                    fetch(`/api/orden_precio/${ordenId}/${bienId}/`)
                        .then(resp => resp.json())
                        .then(data => {
                            if (precioInput) precioInput.value = data.precio;
                            if (precioCell) precioCell.textContent = data.precio;
                        });
                } else {
                    if (precioInput) precioInput.value = '';
                    if (precioCell) precioCell.textContent = '-';
                }
            }

            // Cuando cambia el bien, actualizar órdenes y limpiar precio
            bienSelect.addEventListener('change', function(e) {
                if (e.isTrusted) {
                    const bienId = bienSelect.value;
                    setTimeout(() => {
                        if (!bienSelect.value) {
                            console.warn('El valor del bien fue limpiado por otro script o acción.');
                        }
                    }, 100);
                    const selectedValue = ordenSelect.value;
                    ordenSelect.innerHTML = '<option value="">---------</option>';
                    if (!bienId) {
                        actualizarPrecio();
                        return;
                    }
                    fetch(`/api/ordenes_con_stock_bien/${bienId}/`)
                        .then(resp => resp.json())
                        .then(data => {
                            let found = false;
                            data.ordenes.forEach(function(orden) {
                                const opt = document.createElement('option');
                                opt.value = orden.id;
                                opt.textContent = `${orden.numero} (Disponible: ${orden.disponible})`;
                                if (orden.id == selectedValue) {
                                    opt.selected = true;
                                    found = true;
                                }
                                ordenSelect.appendChild(opt);
                            });
                            if (!found) {
                                ordenSelect.value = '';
                            }
                            actualizarPrecio();
                        });
                }
            });
            // Cuando cambia la orden, actualizar el precio
            ordenSelect.addEventListener('change', function(e) {
                actualizarPrecio();
            });
            // Inicializar precio al cargar
            actualizarPrecio();
        }
    }


    // Solo enlazar el evento, no modificar el select al cargar la página
    document.querySelectorAll('.form-row').forEach(function(row) {
        attachBienChangeHandler(row);
    });

    // Si hay botón para agregar ítems dinámicamente
    const addItemBtn = document.getElementById('add-item');
    if (addItemBtn) {
        addItemBtn.addEventListener('click', function() {
            setTimeout(function() {
                // Buscar la última fila agregada
                const rows = document.querySelectorAll('.form-row');
                const lastRow = rows[rows.length - 1];
                if (lastRow) {
                    attachBienChangeHandler(lastRow);
                }
            }, 100); // Esperar a que se agregue la fila
        });
    }
});
