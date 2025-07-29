
console.log('Cargando formset_dynamic.js');

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
                console.log('Usando input alternativo:', totalForms);
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
        
        const formCount = parseInt(totalForms.value);
        console.log('Form count actual:', formCount);
        
        // Buscar la primera fila de item
        const rows = Array.from(formsetTable.querySelectorAll('.form-row'));
        console.log('Filas encontradas:', rows.length);
        
        if (rows.length === 0) {
            console.error('No se encontraron filas existentes');
            return;
        }
        
        const firstRow = rows[0];
        const newRow = firstRow.cloneNode(true);
        console.log('Fila clonada exitosamente');

        // Actualizar todos los atributos name/id y limpiar valores
        newRow.querySelectorAll('input, select, textarea').forEach(function(input) {
            // Actualizar name e id para todos los elementos
            if (input.name) {
                const oldName = input.name;
                input.name = input.name.replace(/items-(\d+)-/, `items-${formCount}-`);
                console.log(`Actualizando name: ${oldName} -> ${input.name}`);
            }
            if (input.id) {
                const oldId = input.id;
                input.id = input.id.replace(/items-(\d+)-/, `items-${formCount}-`);
                console.log(`Actualizando id: ${oldId} -> ${input.id}`);
            }
            
            // Limpiar valores según el tipo de input
            if (input.type === 'text' || input.type === 'number' || input.type === 'hidden') {
                input.value = '';
            }
            if (input.tagName === 'SELECT') {
                input.selectedIndex = 0;
            }
        });

        // También actualizar los labels for attributes si existen
        newRow.querySelectorAll('label').forEach(function(label) {
            if (label.getAttribute('for')) {
                const oldFor = label.getAttribute('for');
                const newFor = oldFor.replace(/items-(\d+)-/, `items-${formCount}-`);
                label.setAttribute('for', newFor);
                console.log(`Actualizando label for: ${oldFor} -> ${newFor}`);
            }
        });

        // Limpiar celda de precio
        const cell = newRow.querySelector('.precio-unitario-cell');
        if (cell) cell.textContent = '-';

        // Insertar antes de la fila del botón
        const buttonRow = addBtn.closest('tr');
        formsetTable.insertBefore(newRow, buttonRow);

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

        // Enlazar eventos a la nueva fila
        enlazarEventosFila(newRow);
    });

    // Enlazar eventos a todas las filas existentes
    document.querySelectorAll('.form-row').forEach(function(row) {
        enlazarEventosFila(row);
    });
});

function enlazarEventosFila(row) {
    const ordenSelect = row.querySelector('select[name$="-orden_de_compra"]');
    const bienSelect = row.querySelector('select[name$="-bien"]');
    
    console.log('Enlazando eventos para fila:', row);
    console.log('Orden select encontrado:', ordenSelect);
    console.log('Bien select encontrado:', bienSelect);
    
    if (ordenSelect) {
        ordenSelect.addEventListener('change', function() {
            const ordenId = ordenSelect.value;
            console.log('Orden cambiada a:', ordenId);
            if (!ordenId) return;
            
            fetch(`/api/orden_bienes/${ordenId}/`)
                .then(resp => resp.json())
                .then(data => {
                    console.log('Bienes recibidos:', data.bienes);
                    // Actualizar opciones de bien
                    if (bienSelect) {
                        bienSelect.innerHTML = '<option value="">---------</option>';
                        data.bienes.forEach(function(bien) {
                            const opt = document.createElement('option');
                            opt.value = bien.id;
                            opt.textContent = bien.nombre;
                            bienSelect.appendChild(opt);
                        });
                        bienSelect.dispatchEvent(new Event('change'));
                    }
                })
                .catch(error => console.error('Error cargando bienes:', error));
        });
    }
    
    if (bienSelect) {
        bienSelect.addEventListener('change', function() {
            const ordenId = ordenSelect ? ordenSelect.value : '';
            const bienId = bienSelect.value;
            console.log('Bien cambiado:', bienId, 'para orden:', ordenId);
            if (!ordenId || !bienId) return;
            
            fetch(`/api/orden_precio/${ordenId}/${bienId}/`)
                .then(resp => resp.json())
                .then(data => {
                    console.log('Precio recibido:', data.precio);
                    const precioInput = row.querySelector('input[name$="-precio_unitario"]');
                    if (precioInput) {
                        precioInput.value = data.precio;
                        console.log('Precio actualizado en input hidden:', precioInput.value);
                    }
                    const precioCell = row.querySelector('.precio-unitario-cell');
                    if (precioCell) {
                        precioCell.textContent = data.precio || '-';
                        console.log('Precio mostrado en celda:', precioCell.textContent);
                    }
                })
                .catch(error => console.error('Error cargando precio:', error));
        });
    }
}
