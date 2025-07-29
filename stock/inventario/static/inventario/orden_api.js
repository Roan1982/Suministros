// Script para autocompletar bienes y precios según la orden seleccionada
document.addEventListener('DOMContentLoaded', function() {
    const ordenSelect = document.querySelector('select[name="orden_de_compra"]');
    if (!ordenSelect) return;
    ordenSelect.addEventListener('change', function() {
        fetch(`/api/orden_bienes/${ordenSelect.value}/`)
            .then(resp => resp.json())
            .then(data => {
                document.querySelectorAll('.form-row').forEach(function(row, idx) {
                    const bienSelect = row.querySelector('select[name$="-bien"]');
                    if (bienSelect) {
                        // Limpiar opciones
                        bienSelect.innerHTML = '';
                        data.bienes.forEach(function(bien) {
                            const opt = document.createElement('option');
                            opt.value = bien.id;
                            opt.textContent = bien.nombre;
                            bienSelect.appendChild(opt);
                        });
                        // Disparar cambio para actualizar precio
                        bienSelect.dispatchEvent(new Event('change'));
                    }
                });
            });
    });
    document.querySelectorAll('.form-row').forEach(function(row, idx) {
        const bienSelect = row.querySelector('select[name$="-bien"]');
        if (bienSelect) {
            bienSelect.addEventListener('change', function() {
                const ordenId = ordenSelect.value;
                const bienId = bienSelect.value;
                fetch(`/api/orden_precio/${ordenId}/${bienId}/`)
                    .then(resp => resp.json())
                    .then(data => {
                        const precioInput = row.querySelector('input[name$="-precio_unitario"]');
                        if (precioInput) {
                            precioInput.value = data.precio;
                        }
                        const precioCell = row.querySelector('.precio-unitario-cell');
                        if (precioCell) {
                            precioCell.textContent = data.precio || '-';
                        }
                    });
            });
        }
    });
});
