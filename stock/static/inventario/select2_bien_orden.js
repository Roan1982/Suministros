// Aplica select2 a los campos 'bien' y 'orden_de_compra' en formularios dinámicos y estáticos
function aplicarSelect2BienOrden() {
  $(document).ready(function() {
    function activar() {
      $("select[name$='-bien'], select[name='bien']").select2({
        width: '100%',
        theme: 'bootstrap-5',
        placeholder: 'Seleccione un bien',
        allowClear: true,
        language: 'es'
      });
      $("select[name$='-orden_de_compra'], select[name='orden_de_compra']").select2({
        width: '100%',
        theme: 'bootstrap-5',
        placeholder: 'Seleccione una orden',
        allowClear: true,
        language: 'es'
      });
    }
    activar();
    // Para formularios dinámicos (formsets)
    $(document).on('formset:added', function(event, $row, formsetName) {
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
    });
  });
}
// Para usar: aplicarSelect2BienOrden();
