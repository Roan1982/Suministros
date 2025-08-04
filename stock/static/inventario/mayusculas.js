// Convierte a mayúsculas los campos de texto y select al escribir
function setInputsToUpperCase(formSelector) {
  document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector(formSelector);
    if (!form) return;
    form.querySelectorAll('input[type="text"], textarea, select').forEach(function(input) {
      input.addEventListener('input', function(e) {
        if (input.type === 'text' || input.tagName === 'TEXTAREA') {
          input.value = input.value.toUpperCase();
        } else if (input.tagName === 'SELECT') {
          // Opcional: si los options tienen texto en minúscula, puedes forzar el texto mostrado
          for (let i = 0; i < input.options.length; i++) {
            input.options[i].text = input.options[i].text.toUpperCase();
          }
        }
      });
    });
  });
}
// Para usar: setInputsToUpperCase('form');
