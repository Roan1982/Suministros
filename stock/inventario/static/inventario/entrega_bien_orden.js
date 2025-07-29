// Script para filtrar órdenes de compra según el bien seleccionado en cada fila del formset de entrega
// Requiere que el campo bien tenga la clase 'bien-select' y el campo orden de compra la clase 'orden-select'
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.form-row').forEach(function(row) {
        const bienSelect = row.querySelector('.bien-select');
        const ordenSelect = row.querySelector('.orden-select');
        if (bienSelect && ordenSelect) {
            bienSelect.addEventListener('change', function() {
                const bienId = bienSelect.value;
                // Limpiar opciones
                ordenSelect.innerHTML = '<option value="">---------</option>';
                if (!bienId) return;
                fetch(`/api/ordenes_con_stock_bien/${bienId}/`)
                    .then(resp => resp.json())
                    .then(data => {
                        data.ordenes.forEach(function(orden) {
                            const opt = document.createElement('option');
                            opt.value = orden.id;
                            opt.textContent = `${orden.numero} (Disponible: ${orden.disponible})`;
                            ordenSelect.appendChild(opt);
                        });
                    });
            });
        }
    });
});
