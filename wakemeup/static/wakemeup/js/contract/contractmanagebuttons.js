// Modify button confirm
$(".modify_confirm").click(function(event) {
	if(!confirm('Una vez activo, se puede modificar este contrato s\u00F3lo una vez.  \u00BFDesee iniciar la modificaci\u00F3n?')) {
		event.preventDefault();
		return false;
	} else {
		return true;
	}
});

// Cancel button confirm
$(".cancel_confirm").click(function(event) {
	if(!confirm('\u00BFEst\u00E1 seguro que desee eliminar este contrato?')) {
		event.preventDefault();
		return false;
	} else {
		return true;
	}
});