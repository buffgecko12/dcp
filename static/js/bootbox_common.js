function bootbox_confirm(formid, message) {
	event.preventDefault();
	var form = document.getElementById(formid)

	bootbox.confirm({
	    message: message,
	    buttons: {
	        confirm: {
	            label: 'Enviar',
	            className: 'btn btn-primary'
	        },
	        cancel: {
	            label: 'Cancelar',
	            className: 'btn btn-secondary'
	        }
	    },
	    callback: function (result) {
			if (result) {
				form.submit();
			}
	    }
	});
}