// Script para mostrar y actualizar el precio total en la edición de la orden de compra
// Este script debe ser incluido en orden_editar.html

document.addEventListener('DOMContentLoaded', function() {
    function updatePrecioTotal(row) {
        const cantidadInput = row.querySelector('input[name$="-cantidad"]');
        const precioInput = row.querySelector('input[name$="-precio_unitario"]');
        const totalCell = row.querySelector('.precio-total-cell');
        if (cantidadInput && precioInput && totalCell) {
            const cantidad = parseFloat(cantidadInput.value) || 0;
            const precio = parseFloat(precioInput.value) || 0;
            const total = cantidad * precio;
            totalCell.textContent = total.toFixed(2);
        }
    }

    document.querySelectorAll('tr').forEach(function(row) {
        const cantidadInput = row.querySelector('input[name$="-cantidad"]');
        const precioInput = row.querySelector('input[name$="-precio_unitario"]');
        if (cantidadInput && precioInput) {
            cantidadInput.addEventListener('input', function() {
                updatePrecioTotal(row);
            });
            precioInput.addEventListener('input', function() {
                updatePrecioTotal(row);
            });
            // Inicializar
            updatePrecioTotal(row);
        }
    });
});
