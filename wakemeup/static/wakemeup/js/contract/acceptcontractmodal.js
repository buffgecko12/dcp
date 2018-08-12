function update_acceptcontractform(type, partyuserid, contractid, preferredgoalid) {
	var myform =$("#acceptContractForm");
	var url = $(myform).attr("data-acceptcontract-url");
	var redirecturl = $(myform).attr("data-redirect-url");
	
	if(type == "new") {
		requesttype = "GET";
	}
	else {
		requesttype = "POST";

		// Hidden values
		var contractid = $(myform).find('input[name=contractid]').val()
		var partyuserid = $(myform).find('input[name=partyuserid]').val()
		var preferredgoalid = $(myform).find('input[name=preferredgoalid]').val()

		// User-provided values
		var idfullname = $(myform).find('input[name=idfullname]').val()
		var idnumber = $(myform).find('input[name=idnumber]').val()
		var idissuedate = $(myform).find('input[name=idissuedate]').val()
		var idissuelocation = $(myform).find('input[name=idissuelocation]').val()
	}

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
				csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value, // Pass CSRF token
			},
			success: function(data){
	            $("#mymodaldiv").html(data); // Update div with return HTML
	            if(data == "Contrato ha sido aceptado.") { // Successfully saved contract
		            setTimeout(
	            		function(){
			            	$('#acceptContractModal').modal('hide'); // Close after a few seconds
			            	location.href=redirecturl
//			            	window.location.reload(); // Reload parent page (only after submit)
		            	},
		            	2000
	            	)
	            }
	            document.getElementById('cancel').onclick = function() { // Add event listener on new modal form "cancel" field
	            	$('#acceptContractModal').modal('hide')
	            	return false
	            }
			}
		}
	);
}