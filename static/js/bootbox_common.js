function bootbox_confirm(formid, message, submitdelay = 0) {
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
				// Submit form
				setTimeout(function() {
					form.submit();
				}, submitdelay) // Wait a little before sending the form

				// Disable buttons (use setTimeout so there's a delay between when the form is submitted and the buttons are disabled)
				setTimeout( function() {
					try {
						document.getElementById('submit_next').disabled = true
						document.getElementById('submit_cancel').className += " " + "disabled"
						document.getElementById('submit_previous').className += " " + "disabled"  // Leave this last, since it's not always present
					}
					catch {}
					
					// Update submit button text
					document.getElementById('submit_next').value = 'Enviando...'
				}
				,0)
			}
	    }
	});
}