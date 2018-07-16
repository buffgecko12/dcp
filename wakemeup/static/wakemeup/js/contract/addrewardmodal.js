// ADD REWARD MODAL
// Update reward form modal
function update_rewardform(type) {
	var url = $("#addRewardForm").attr("data-addreward-url");
	var form =$("#addRewardForm");

	// Lookup form field values
	var rewarddisplayname = $("#addRewardForm input[name=rewarddisplayname]").val();
	var rewarddescription = $("#addRewardForm textarea[name=rewarddescription]").val();
	var rewardvalue = $("#addRewardForm input[name=rewardvalue]").val();
	
	if(type == "new") {
		requesttype = "GET";
	} else {
		requesttype = "POST";
	}
	
	$.ajax(
		{
			type:requesttype,
			url:url,
			data: {
				rewarddisplayname:rewarddisplayname,
				rewarddescription:rewarddescription,
				rewardvalue:rewardvalue,
				csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value, // Pass CSRF token
			},
			success: function(data){
	            $("#mymodaldiv").html(data); // Update div with return HTML
	            if(data == "Premio guardado.") { // Successfully saved reward
		            setTimeout(
	            		function(){
			            	$('#addRewardModal').modal('hide'); // Close after a few seconds
		            	}, 
		            	2500
	            	)
	            }
	            document.getElementById('cancel').onclick = function() { // Add event listener on new modal form "cancel" field
	            	$('#addRewardModal').modal('hide')
	            	return false
	            }
			}
		}
	);
}