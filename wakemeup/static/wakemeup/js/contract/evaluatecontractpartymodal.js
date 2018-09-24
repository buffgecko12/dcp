function update_evaluatecontractpartyform(type, contractid, partyuserid) {

	var myform =$("#evaluateContractPartyForm");
	var url = $(myform).attr("data-evaluatecontractparty-url");
	var submitdelay = undefined
	
	// Modal - Show new
	if(type == "new") {
		requesttype = "GET";
		submitdelay = 0;
	}
	// Modal - Submit
	else {
		requesttype = "POST";
		submitdelay = 1500;
		
		// Hidden values
		var contractid = $(myform).find('input[name=contractid]').val();
		var partyuserid = $(myform).find('input[name=partyuserid]').val();

		// User-provided values
		var highperformers = $("select[name=highperformers]").val();
		var topperformer_group = $('input[name=topperformer_group]').val();
		var experiencerating_teacher = $('input[name$=experiencerating]:checked').val();

		// Disable buttons
		setTimeout( function() {
			$("#cancel").prop('disabled',true)
			$("#next").prop('disabled',true)
			$("#next").val('Enviando...')
		}
		,0)
	}

	setTimeout(function() {
		$.ajax(
			{
				type:requesttype,
				url:url,
				data: {
					// Hidden form fields
					contractid:contractid,
					partyuserid:partyuserid,
					
					// User-provided fields
					highperformers:highperformers,
					topperformer_group:topperformer_group,
					experiencerating_teacher:experiencerating_teacher,
					
					// CSRF token
					csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value,
				},
				success: function(data){
		            if(data == "success") {
		            	// Update modal with "success" message
			            $("#mymodaldiv").append('<b><i><div class="text-danger text-center">Evaluaci\u00F3n enviado.  Gracias!</div></i></b>');
			            setTimeout(
		            		function(){
				            	$('#evaluateContractPartyModal').modal('hide'); // Close after a few seconds
				            	location.reload()
			            	},
			            	2500
		            	)
		            } else {
		            	// Dispay new modal
			            $("#mymodaldiv").html(data);		            	
		            }
	
		            // MODAL - Submit listener
		            $("#next").on('click', function()  {
		    			update_evaluatecontractpartyform("submit")
		    			return false
		            })
	
		            // MODAL - Cancel listener
		            $("#cancel").on('click', function() {
		            	$('#evaluateContractPartyModal').modal('hide')
		            	return false
		            })
				}
			}
		);
	}
	,submitdelay)
}