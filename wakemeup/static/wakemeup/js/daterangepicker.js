// http://www.daterangepicker.com/#examples
// DATEPICKER: Config
$(function() {
  moment.locale('es');
  $('.daterangeinputfieldempty').daterangepicker({
	  autoApply: true,
	  autoUpdateInput: false,
	  minYear: 2018,
	  maxYear: parseInt(moment().format('YYYY'),10),
      locale: {
          "applyLabel": "Aplicar",
          "cancelLabel": "Cancelar",
    	  }
  });

  // DATEPICKER: Set initial values to empty
  $('.daterangeinputfieldempty').on('apply.daterangepicker', function(ev, picker) {
      $(this).val(picker.startDate.format('DD/MM/YYYY') + ' - ' + picker.endDate.format('DD/MM/YYYY'));
  });

  $('.daterangeinputfieldempty').on('cancel.daterangepicker', function(ev, picker) {
      $(this).val('');
  });
});