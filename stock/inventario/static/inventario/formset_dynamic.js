

console.log('Cargando formset_dynamic.js');

// Enlaza eventos para actualizar el precio unitario dinámicamente
function enlazarEventosFila(row) {
    const bienSelect = row.querySelector("select[name$='-bien']");
    const ordenSelect = row.querySelector("select[name$='-orden_de_compra']");
    const precioSpan = row.querySelector('.precio-unitario-cell');
    const precioInput = row.querySelector("input[name$='-precio_unitario']");

    function actualizarPrecio() {
        const bienId = bienSelect && bienSelect.value;
        const ordenId = ordenSelect && ordenSelect.value;
        if (bienId && ordenId) {
            fetch(`/inventario/api/orden_precio/${ordenId}/${bienId}/`)
                .then(resp => resp.json())
                .then(data => {
                    if (data.precio) {
                        if (precioSpan) precioSpan.textContent = data.precio;
                        if (precioInput) precioInput.value = data.precio;
                    } else {
                        if (precioSpan) precioSpan.textContent = '-';
                        if (precioInput) precioInput.value = '';
                    }
                })
                .catch(() => {
                    if (precioSpan) precioSpan.textContent = '-';
                    if (precioInput) precioInput.value = '';
                });
        } else {
            if (precioSpan) precioSpan.textContent = '-';
            if (precioInput) precioInput.value = '';
        }
    }
    if (bienSelect) bienSelect.addEventListener('change', actualizarPrecio);
    if (ordenSelect) ordenSelect.addEventListener('change', actualizarPrecio);
}

// Script para que cada fila permita seleccionar OC y bien, y autocompletar precio
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM cargado, buscando elementos...');
    
    // Verificar que existan los elementos necesarios
    const addBtn = document.getElementById('add-item');
    let formsetTable = document.querySelector('table.table tbody');
    let totalForms = document.getElementById('id_items-TOTAL_FORMS');
    
    console.log('Botón add-item:', addBtn);
    console.log('Tabla formset:', formsetTable);
    console.log('Total forms:', totalForms);
    
    if (!addBtn) {
        console.error('No se encontró el botón add-item');
        return;
    }
    
    // Botón para agregar nueva fila
    addBtn.addEventListener('click', function(e) {
        e.preventDefault();
        console.log('Botón agregar bien clickeado');
        
        if (!formsetTable) {
            formsetTable = document.querySelector('tbody');
            console.log('Tabla alternativa:', formsetTable);
        }
        
        if (!totalForms) {
            const allInputs = document.querySelectorAll('input[name*="TOTAL_FORMS"]');
            console.log('Inputs TOTAL_FORMS encontrados:', allInputs);
            if (allInputs.length > 0) {
                totalForms = allInputs[0];
            }
        }
        
        if (!formsetTable) {
            console.error('No se encontró la tabla');
            return;
        }
        
        if (!totalForms) {
            console.error('No se encontró el campo TOTAL_FORMS');
            return;
        }
        
        var formCount = parseInt(totalForms.value);
        console.log('Form count actual:', formCount);
        
        // Buscar la primera fila de item
        const rows = Array.from(formsetTable.querySelectorAll('.form-row'));
        console.log('Filas encontradas:', rows.length);
        
        if (rows.length === 0) {
            console.error('No se encontraron filas existentes');
            return;
        }
        

        // Usar el template vacío de Django para una fila nueva
        let emptyFormTemplate = document.getElementById('empty-form-template');
        if (emptyFormTemplate) {
            let html = emptyFormTemplate.innerHTML.replace(/__prefix__/g, formCount);
            const temp = document.createElement('tbody');
            temp.innerHTML = html;
            const newRow = temp.querySelector('tr');
            // Limpiar valores de los campos
            newRow.querySelectorAll('input, select, textarea').forEach(function(input) {
                if (input.type === 'text' || input.type === 'number' || input.type === 'hidden') input.value = '';
                if (input.tagName === 'SELECT') input.selectedIndex = 0;
            });
            // Insertar antes del botón Agregar bien si existe
            const addBtnRow = addBtn.closest('tr');
            if (addBtnRow) {
                formsetTable.insertBefore(newRow, addBtnRow);
            } else {
                formsetTable.appendChild(newRow);
            }
            enlazarEventosFila(newRow);
            if (window.jQuery) {
                var $row = window.jQuery(newRow);
                // Solo inicializar select2 en los nuevos selects
                $row.find("select[name$='-bien']").select2({
                    width: '100%',
                    theme: 'bootstrap-5',
                    placeholder: 'Seleccione un bien',
                    allowClear: true,
                    language: 'es'
                });
                $row.find("select[name$='-orden_de_compra']").select2({
                    width: '100%',
                    theme: 'bootstrap-5',
                    placeholder: 'Seleccione una orden',
                    allowClear: true,
                    language: 'es'
                });
                if (typeof setInputsToUpperCase === 'function') setInputsToUpperCase('form');
                window.jQuery(document).trigger('formset:added', [$row, 'items']);
            }
        } else {
            // Fallback: clonar la primera fila existente
            const firstRow = rows[0];
            const clonedRow = firstRow.cloneNode(true);
            // Limpiar valores y destruir select2 como antes
            clonedRow.querySelectorAll('input, select, textarea').forEach(function(input) {
                if (input.name) input.name = input.name.replace(/items-(\d+)-/, `items-${formCount}-`);
                if (input.id) input.id = input.id.replace(/items-(\d+)-/, `items-${formCount}-`);
                if (input.type === 'text' || input.type === 'number' || input.type === 'hidden') input.value = '';
                if (input.tagName === 'SELECT') {
                    if (window.jQuery && window.jQuery(input).hasClass('select2-hidden-accessible')) {
                        window.jQuery(input).select2('destroy');
                    }
                    input.selectedIndex = 0;
                }
            });
            clonedRow.querySelectorAll('label').forEach(function(label) {
                if (label.getAttribute('for')) label.setAttribute('for', label.getAttribute('for').replace(/items-(\d+)-/, `items-${formCount}-`));
            });
            const cell = clonedRow.querySelector('.precio-unitario-cell');
            if (cell) cell.textContent = '-';
            // Insertar antes del botón Agregar bien si existe
            const addBtnRow = addBtn.closest('tr');
            if (addBtnRow) {
                formsetTable.insertBefore(clonedRow, addBtnRow);
            } else {
                formsetTable.appendChild(clonedRow);
            }
            enlazarEventosFila(clonedRow);
            if (window.jQuery) {
                var $row = window.jQuery(clonedRow);
                $row.find("select[name$='-bien']").select2({
                    width: '100%',
                    theme: 'bootstrap-5',
                    placeholder: 'Seleccione un bien',
                    allowClear: true,
                    language: 'es'
                });
                $row.find("select[name$='-orden_de_compra']").select2({
                    width: '100%',
                    theme: 'bootstrap-5',
                    placeholder: 'Seleccione una orden',
                    allowClear: true,
                    language: 'es'
                });
                if (typeof setInputsToUpperCase === 'function') setInputsToUpperCase('form');
                window.jQuery(document).trigger('formset:added', [$row, 'items']);
            }
        }

        // Actualizar el contador de forms
        totalForms.value = formCount + 1;
        console.log('Nueva fila agregada, nuevo count:', formCount + 1);
        console.log('TOTAL_FORMS actualizado a:', totalForms.value);
        
        // Debug: listar todos los campos del formset
        const allFormInputs = formsetTable.querySelectorAll('input, select');
        console.log('Total de inputs en el formset:', allFormInputs.length);
        allFormInputs.forEach(function(input, index) {
            if (input.name) {
                console.log(`Input ${index}: name="${input.name}", value="${input.value}"`);
            }
        });
    });

    // Enlazar eventos a todas las filas existentes
    document.querySelectorAll('.form-row').forEach(function(row) {
        enlazarEventosFila(row);
    });
});
