// Script UNIFICADO para filtrar órdenes de compra según el bien seleccionado y mostrar stock
// Aplica select2 siempre y actualiza stock correctamente
function actualizarStockBienOrden(row) {
    const bienSelect = row.querySelector('.bien-select');
    const ordenSelect = row.querySelector('.orden-select');
    const stockCell = row.querySelector('.stock-cell');
    if (!bienSelect || !ordenSelect || !stockCell) return;
    const bienId = bienSelect.value;
    const ordenId = ordenSelect.value;
    if (!bienId || !ordenId) {
      stockCell.textContent = '-';
      return;
    }
    fetch(`/api/orden_bien_stock/${ordenId}/${bienId}/`)
      .then(resp => resp.json())
      .then(data => {
        if (data.status === 'ok') {
          stockCell.textContent = data.stock;
        } else {
          stockCell.textContent = '-';
        }
      })
      .catch(() => { stockCell.textContent = '-'; });
  }

function actualizarOrdenesDeCompra(row) {
    const bienSelect = row.querySelector('.bien-select');
    const ordenSelect = row.querySelector('.orden-select');
    if (!bienSelect || !ordenSelect) return;
    const bienId = bienSelect.value;
    console.log('[DEBUG] bienId seleccionado:', bienId);
    ordenSelect.innerHTML = '<option value="">---------</option>';
    if (!bienId) {
      if (window.jQuery && window.jQuery.fn.select2) {
        window.jQuery(ordenSelect).trigger('change.select2');
      }
      return;
    }
    fetch(`/api/ordenes_con_stock_bien/${bienId}/`)
      .then(resp => resp.json())
      .then(data => {
        console.log('[DEBUG] Respuesta de /api/ordenes_con_stock_bien/', bienId, data);
        if (data.ordenes && data.ordenes.length > 0) {
          data.ordenes.forEach(function(orden) {
            const opt = document.createElement('option');
            opt.value = orden.id;
            opt.textContent = `${orden.numero}`;
            // Guardar el disponible y el precio_unitario como atributos data
            opt.setAttribute('data-disponible', orden.disponible);
            if (orden.precio_unitario !== undefined) {
              opt.setAttribute('data-precio-unitario', orden.precio_unitario);
            }
            ordenSelect.appendChild(opt);
          });
          if (window.jQuery && window.jQuery.fn.select2) {
            window.jQuery(ordenSelect).trigger('change.select2');
          }
          console.log('[DEBUG] Opciones agregadas al select:', ordenSelect.innerHTML);
          // Si hay una opción seleccionada, mostrar stock y precio
          if (ordenSelect.value) {
            const selectedOption = ordenSelect.options[ordenSelect.selectedIndex];
            const stockCell = row.querySelector('.stock-cell');
            const precioCell = row.querySelector('.precio-unitario-cell');
            if (selectedOption && stockCell) {
              const disponible = selectedOption.getAttribute('data-disponible');
              stockCell.textContent = disponible !== null ? disponible : '-';
            }
            if (selectedOption && precioCell) {
              const precioUnitario = selectedOption.getAttribute('data-precio-unitario');
              precioCell.textContent = (precioUnitario !== null && precioUnitario !== undefined) ? precioUnitario : '-';
            }
          }
          // Si solo hay una opción válida, seleccionarla automáticamente y mostrar stock/precio (sin disparar evento)
          if (ordenSelect.options.length === 2) { // placeholder + una opción
            ordenSelect.selectedIndex = 1;
            const selectedOption = ordenSelect.options[1];
            const stockCell = row.querySelector('.stock-cell');
            const precioCell = row.querySelector('.precio-unitario-cell');
            if (selectedOption && stockCell) {
              const disponible = selectedOption.getAttribute('data-disponible');
              stockCell.textContent = disponible !== null ? disponible : '-';
            }
            if (selectedOption && precioCell) {
              const precioUnitario = selectedOption.getAttribute('data-precio-unitario');
              precioCell.textContent = (precioUnitario !== null && precioUnitario !== undefined) ? precioUnitario : '-';
            }
          }
        } else {
          if (window.jQuery && window.jQuery.fn.select2) {
            window.jQuery(ordenSelect).trigger('change.select2');
          }
          console.warn('[DEBUG] No se encontraron órdenes con stock para el bien:', bienId);
        }
      })
      .catch(err => {
        if (window.jQuery && window.jQuery.fn.select2) {
          window.jQuery(ordenSelect).trigger('change.select2');
        }
        console.error('[DEBUG] Error al consultar /api/ordenes_con_stock_bien/', bienId, err);
      });
  }

function aplicarSelect2(row) {
    if (window.jQuery && window.jQuery.fn.select2) {
      window.jQuery(row).find('.bien-select').select2({
        width: '100%',
        theme: 'bootstrap-5',
        placeholder: 'Seleccione un bien',
        allowClear: true,
        language: 'es'
      });
      window.jQuery(row).find('.orden-select').select2({
        width: '100%',
        theme: 'bootstrap-5',
        placeholder: 'Seleccione una orden',
        allowClear: true,
        language: 'es'
      });
    }
  }


function inicializarFilaEntregaBienOrden(row) {
  aplicarSelect2(row);
  const bienSelect = row.querySelector('.bien-select');
  const ordenSelect = row.querySelector('.orden-select');
  if (bienSelect) {
    bienSelect.addEventListener('change', function() {
      actualizarOrdenesDeCompra(row);
      if (ordenSelect) ordenSelect.value = '';
      const stockCell = row.querySelector('.stock-cell');
      const precioCell = row.querySelector('.precio-unitario-cell');
      const precioInput = row.querySelector('input[name$="-precio_unitario"]');
      if (stockCell) stockCell.textContent = '-';
      if (precioCell) precioCell.textContent = '-';
      if (precioInput) precioInput.value = '';
    });
    if (window.jQuery && window.jQuery.fn.select2) {
      window.jQuery(bienSelect).on('select2:select', function(e) {
        actualizarOrdenesDeCompra(row);
        if (ordenSelect) ordenSelect.value = '';
        const stockCell = row.querySelector('.stock-cell');
        const precioCell = row.querySelector('.precio-unitario-cell');
        const precioInput = row.querySelector('input[name$="-precio_unitario"]');
        if (stockCell) stockCell.textContent = '-';
        if (precioCell) precioCell.textContent = '-';
        if (precioInput) precioInput.value = '';
      });
    }
    if (bienSelect.value) {
      actualizarOrdenesDeCompra(row);
    }
  }
  if (ordenSelect) {
    function mostrarStockYPrecio() {
      const selectedOption = ordenSelect.options[ordenSelect.selectedIndex];
      const stockCell = row.querySelector('.stock-cell');
      const precioCell = row.querySelector('.precio-unitario-cell');
      const precioInput = row.querySelector('input[name$="-precio_unitario"]');
      
      if (selectedOption && stockCell) {
        const disponible = selectedOption.getAttribute('data-disponible');
        if (disponible !== null) {
          stockCell.textContent = disponible;
        } else {
          stockCell.textContent = '-';
        }
      }
      if (selectedOption && precioCell) {
        const precioUnitario = selectedOption.getAttribute('data-precio-unitario');
        if (precioUnitario !== null && precioUnitario !== undefined) {
          precioCell.textContent = precioUnitario;
          // También actualizar el campo hidden
          if (precioInput) {
            precioInput.value = precioUnitario;
          }
        } else {
          precioCell.textContent = '-';
          if (precioInput) {
            precioInput.value = '';
          }
        }
      }
    }
    ordenSelect.addEventListener('change', function() {
      mostrarStockYPrecio();
    });
    ordenSelect.addEventListener('select2:select', function() {
      mostrarStockYPrecio();
    });
    if (ordenSelect.value) {
      mostrarStockYPrecio();
    }
  }
}

document.addEventListener('DOMContentLoaded', function() {
  console.log('[DEBUG] DOMContentLoaded ejecutado');
  const filas = document.querySelectorAll('#items-table-body tr.form-row');
  console.log('[DEBUG] Filas form-row encontradas:', filas.length);
  filas.forEach(function(row) {
    inicializarFilaEntregaBienOrden(row);
  });

  // Para nuevas filas agregadas dinámicamente
  document.getElementById('items-table-body').addEventListener('DOMNodeInserted', function(e) {
    if (e.target && e.target.classList && e.target.classList.contains('form-row')) {
      inicializarFilaEntregaBienOrden(e.target);
    }
  });

// Exponer para uso externo (formset_dynamic.js)
window.actualizarFilaEntregaBienOrden = inicializarFilaEntregaBienOrden;
});
