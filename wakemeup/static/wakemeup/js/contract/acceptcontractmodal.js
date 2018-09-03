function update_acceptcontractform(type, partyuserid, contractid, preferredgoalid) {
	var myform =$("#acceptContractForm");
	var url = $(myform).attr("data-acceptcontract-url");
	var redirecturl = $(myform).attr("data-redirect-url");
	
	var submitdelay = undefined
	
	// Modal - Show new
	if(type == "new") {
		requesttype = "GET";
		submitdelay = 0
	}
	// Modal - Submit
	else {
		requesttype = "POST";
		submitdelay = 1500
		
		// Hidden values
		var contractid = $(myform).find('input[name=contractid]').val()
		var partyuserid = $(myform).find('input[name=partyuserid]').val()
		var preferredgoalid = $(myform).find('input[name=preferredgoalid]').val()

		// User-provided values
		var idfullname = $(myform).find('input[name=idfullname]').val()
		var idnumber = $(myform).find('input[name=idnumber]').val()
		var idissuedate = $(myform).find('input[name=idissuedate]').val()
		var idissuelocation = $(myform).find('input[name=idissuelocation]').val()

		// Disable buttons
		setTimeout( function() {
			document.getElementById('next').disabled = true	
			document.getElementById('cancel').disabled = true	
			document.getElementById('next').value = 'Enviando...'	
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
					preferredgoalid:preferredgoalid,
					
					// User-provided fields
					idfullname:idfullname,
					idnumber:idnumber,
					idissuedate:idissuedate,
					idissuelocation:idissuelocation,
					
					// CSRF token
					csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value,
				},
				success: function(data){
		            if(data == "success") {
		            	// Update modal with "success" message
			            $("#mymodaldiv").append('<b><i><div class="text-danger text-center">Contrato ha sido aceptado</div></i></b>');
			            setTimeout(
		            		function(){
				            	$('#acceptContractModal').modal('hide'); // Close after a few seconds
			            	},
			            	2500
		            	)
		            } else {
		            	// Dispay new modal
			            $("#mymodaldiv").html(data);		            	
		            }
	
		            // MODAL - Submit listener
		            document.getElementById('next').onclick = function() {
		    			update_acceptcontractform("submit")
		    			return false
		            }
	
		            // MODAL - Cancel listener
		            document.getElementById('cancel').onclick = function() {
		            	$('#acceptContractModal').modal('hide')
		            	return false
		            }
				}
			}
		);
	}
	,submitdelay)
}