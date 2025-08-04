// Aplica select2 al campo 'bien' en formularios dinámicos y estáticos
function aplicarSelect2Bien() {
  $(document).ready(function() {
    function activar() {
      $("select[name$='-bien'], select[name='bien']").select2({
        width: '100%',
        theme: 'bootstrap-5',
        placeholder: 'Seleccione un bien',
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
    });
  });
}
// Para usar: aplicarSelect2Bien();
