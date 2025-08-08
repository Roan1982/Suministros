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
          // Si hay una opción ya seleccionada, mostrar stock y precio
          if (ordenSelect.value) {
            console.log('[DEBUG] Hay una opción preseleccionada:', ordenSelect.value);
            mostrarStockYPrecio();
          }
          // Si solo hay una opción válida, seleccionarla automáticamente y mostrar stock/precio
          if (ordenSelect.options.length === 2) { // placeholder + una opción
            console.log('[DEBUG] Solo una orden disponible, seleccionando automáticamente');
            const valorOrden = ordenSelect.options[1].value;
            ordenSelect.selectedIndex = 1;
            
            // Actualizar select2 si está habilitado
            if (window.jQuery && window.jQuery.fn.select2) {
              window.jQuery(ordenSelect).val(valorOrden).trigger('change.select2');
              // Usar setTimeout para asegurar que select2 se haya actualizado
              setTimeout(function() {
                // Llamar directamente a mostrar stock y precio
                const selectedOption = ordenSelect.options[ordenSelect.selectedIndex];
                const stockCell = row.querySelector('.stock-cell');
                const precioCell = row.querySelector('.precio-unitario-cell');
                const precioInput = row.querySelector('input[name$="-precio_unitario"]');
                
                if (selectedOption) {
                  const disponible = selectedOption.getAttribute('data-disponible');
                  const precioUnitario = selectedOption.getAttribute('data-precio-unitario');
                  
                  if (stockCell) {
                    stockCell.textContent = disponible !== null && disponible !== undefined ? disponible : '-';
                  }
                  
                  if (precioCell) {
                    if (precioUnitario !== null && precioUnitario !== undefined && precioUnitario !== '') {
                      precioCell.textContent = precioUnitario;
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
              }, 100);
            } else {
              // Si no hay select2, llamar directamente
              const selectedOption = ordenSelect.options[ordenSelect.selectedIndex];
              const stockCell = row.querySelector('.stock-cell');
              const precioCell = row.querySelector('.precio-unitario-cell');
              const precioInput = row.querySelector('input[name$="-precio_unitario"]');
              
              if (selectedOption) {
                const disponible = selectedOption.getAttribute('data-disponible');
                const precioUnitario = selectedOption.getAttribute('data-precio-unitario');
                
                if (stockCell) {
                  stockCell.textContent = disponible !== null && disponible !== undefined ? disponible : '-';
                }
                
                if (precioCell) {
                  if (precioUnitario !== null && precioUnitario !== undefined && precioUnitario !== '') {
                    precioCell.textContent = precioUnitario;
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
  
  // Definir la función mostrarStockYPrecio al inicio
  function mostrarStockYPrecio() {
    const selectedOption = ordenSelect.options[ordenSelect.selectedIndex];
    const stockCell = row.querySelector('.stock-cell');
    const precioCell = row.querySelector('.precio-unitario-cell');
    const precioInput = row.querySelector('input[name$="-precio_unitario"]');
    
    console.log('[DEBUG] mostrarStockYPrecio - selectedOption:', selectedOption);
    console.log('[DEBUG] selectedOption value:', selectedOption ? selectedOption.value : 'null');
    
    if (selectedOption && selectedOption.value) {
      // Hay una orden seleccionada
      const disponible = selectedOption.getAttribute('data-disponible');
      const precioUnitario = selectedOption.getAttribute('data-precio-unitario');
      
      console.log('[DEBUG] disponible:', disponible);
      console.log('[DEBUG] precioUnitario:', precioUnitario);
      
      // Actualizar stock
      if (stockCell) {
        stockCell.textContent = disponible !== null && disponible !== undefined ? disponible : '-';
        // Validar cantidad después de actualizar stock
        setTimeout(validarCantidad, 10);
      }
      
      // Actualizar precio
      if (precioCell) {
        if (precioUnitario !== null && precioUnitario !== undefined && precioUnitario !== '') {
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
    } else {
      // No hay orden seleccionada - limpiar valores
      if (stockCell) {
        stockCell.textContent = '-';
      }
      if (precioCell) {
        precioCell.textContent = '-';
      }
      if (precioInput) {
        precioInput.value = '';
      }
    }
  }
  
  // Función para validar cantidad vs stock disponible
  function validarCantidad() {
    const cantidadInput = row.querySelector('input[name$="-cantidad"]');
    const stockCell = row.querySelector('.stock-cell');
    
    if (cantidadInput && stockCell) {
      const cantidad = parseInt(cantidadInput.value) || 0;
      const stockText = stockCell.textContent;
      const stockDisponible = parseInt(stockText) || 0;
      
      // Solo validar si hay stock disponible (no es '-')
      if (stockText !== '-' && stockDisponible > 0) {
        if (cantidad > stockDisponible) {
          cantidadInput.setCustomValidity(`La cantidad no puede ser mayor al stock disponible (${stockDisponible})`);
          cantidadInput.classList.add('is-invalid');
          
          // Mostrar mensaje de error
          let errorMsg = cantidadInput.parentNode.querySelector('.invalid-feedback');
          if (!errorMsg) {
            errorMsg = document.createElement('div');
            errorMsg.className = 'invalid-feedback';
            cantidadInput.parentNode.appendChild(errorMsg);
          }
          errorMsg.textContent = `Stock disponible: ${stockDisponible}`;
        } else {
          cantidadInput.setCustomValidity('');
          cantidadInput.classList.remove('is-invalid');
          
          // Remover mensaje de error
          const errorMsg = cantidadInput.parentNode.querySelector('.invalid-feedback');
          if (errorMsg) {
            errorMsg.remove();
          }
        }
      } else {
        // Si no hay stock información, limpiar validación
        cantidadInput.setCustomValidity('');
        cantidadInput.classList.remove('is-invalid');
        const errorMsg = cantidadInput.parentNode.querySelector('.invalid-feedback');
        if (errorMsg) {
          errorMsg.remove();
        }
      }
    }
  }
  
  if (bienSelect) {
    bienSelect.addEventListener('change', function() {
      console.log('[DEBUG] Bien select changed to:', bienSelect.value);
      actualizarOrdenesDeCompra(row);
      if (ordenSelect) {
        ordenSelect.value = '';
        if (window.jQuery && window.jQuery.fn.select2) {
          window.jQuery(ordenSelect).val('').trigger('change.select2');
        }
      }
      // Limpiar stock y precio
      const stockCell = row.querySelector('.stock-cell');
      const precioCell = row.querySelector('.precio-unitario-cell');
      const precioInput = row.querySelector('input[name$="-precio_unitario"]');
      if (stockCell) stockCell.textContent = '-';
      if (precioCell) precioCell.textContent = '-';
      if (precioInput) precioInput.value = '';
    });
    
    if (window.jQuery && window.jQuery.fn.select2) {
      window.jQuery(bienSelect).on('select2:select', function(e) {
        console.log('[DEBUG] Bien select2:select event, value:', bienSelect.value);
        actualizarOrdenesDeCompra(row);
        if (ordenSelect) {
          ordenSelect.value = '';
          window.jQuery(ordenSelect).val('').trigger('change.select2');
        }
        // Limpiar stock y precio
        const stockCell = row.querySelector('.stock-cell');
        const precioCell = row.querySelector('.precio-unitario-cell');
        const precioInput = row.querySelector('input[name$="-precio_unitario"]');
        if (stockCell) stockCell.textContent = '-';
        if (precioCell) precioCell.textContent = '-';
        if (precioInput) precioInput.value = '';
      });
      
      window.jQuery(bienSelect).on('select2:clear', function(e) {
        console.log('[DEBUG] Bien select2:clear event');
        if (ordenSelect) {
          ordenSelect.innerHTML = '<option value="">---------</option>';
          window.jQuery(ordenSelect).val('').trigger('change.select2');
        }
        // Limpiar stock y precio
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
    ordenSelect.addEventListener('change', function() {
      console.log('[DEBUG] Orden select changed to:', ordenSelect.value);
      mostrarStockYPrecio();
    });
    
    // Para Select2
    if (window.jQuery && window.jQuery.fn.select2) {
      window.jQuery(ordenSelect).on('select2:select', function() {
        console.log('[DEBUG] Select2 select event, value:', ordenSelect.value);
        mostrarStockYPrecio();
      });
      window.jQuery(ordenSelect).on('select2:clear', function() {
        console.log('[DEBUG] Select2 clear event');
        mostrarStockYPrecio();
      });
    }
    if (ordenSelect.value) {
      mostrarStockYPrecio();
    }
  }
  
  // Agregar validación de cantidad
  const cantidadInput = row.querySelector('input[name$="-cantidad"]');
  if (cantidadInput) {
    cantidadInput.addEventListener('input', validarCantidad);
    cantidadInput.addEventListener('change', validarCantidad);
  }
}

document.addEventListener('DOMContentLoaded', function() {
  console.log('[DEBUG] DOMContentLoaded ejecutado');
  const filas = document.querySelectorAll('#items-table-body tr.form-row');
  console.log('[DEBUG] Filas form-row encontradas:', filas.length);
  filas.forEach(function(row) {
    inicializarFilaEntregaBienOrden(row);
    // Agregar validación adicional para filas existentes que ya tienen datos
    const cantidadInput = row.querySelector('input[name$="-cantidad"]');
    if (cantidadInput && cantidadInput.value) {
      // Disparar validación después de un breve delay para asegurar que el stock se haya cargado
      setTimeout(() => {
        const event = new Event('input', { bubbles: true });
        cantidadInput.dispatchEvent(event);
      }, 500);
    }
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
