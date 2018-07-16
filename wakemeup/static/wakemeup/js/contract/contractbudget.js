// BUDGET
// Initialize variables
var maxRewardValue = undefined;
var currentBudget = parseInt($("#id_initialbudget").val(),10); // Lookup initial values from hidden form fields
var numParticipants = parseInt($("#id_numparticipants").val(),10);

function get_budget_HTML(){

	var currentBudgetHTML = undefined
	if(currentBudget < 0) {
		currentBudgetHTML = '<span class="bg-warning">Presupuesto: $' + String(currentBudget) + '</span>'
	} else {
		currentBudgetHTML = 'Presupuesto: $' + currentBudget
	}
	
	return currentBudgetHTML;
}

// Update available budget	
function update_maxvalue() {
	var result = get_max_rewardValue();

	if(maxRewardValue === undefined || maxRewardValue != result) {
		var disabledFlag = undefined;
		var delta = (maxRewardValue - result);
		currentBudget = currentBudget + (delta * numParticipants);
		
        $("#id_availablebudget").html(get_budget_HTML());
		maxRewardValue = result; // Store new value
		
		if(currentBudget < 0) {
			disabledFlag = true;
		} else {
			disabledFlag = false;
		}

		// Update buttons
		document.getElementById("submit_cancel").disabled = disabledFlag;
		document.getElementById("submit_next").disabled = disabledFlag;
		document.getElementById("submit_previous").disabled = disabledFlag;
	}		
}

$("#id_e_rewardinfo").change(function () {update_maxvalue()});
$("#id_m_rewardinfo").change(function () {update_maxvalue()});
$("#id_d_rewardinfo").change(function () {update_maxvalue()});

function get_max_rewardValue() {
    var maxValue = 0; // Set minimum value in case there are no elements selected
	
    var sel_list = ['id_e_rewardinfo','id_m_rewardinfo','id_d_rewardinfo'] // Loop through all drop-downs

    for(j=0; j<sel_list.length; j++) {

    	elem = document.getElementById(sel_list[j]);
    	
	    // Loop through drop-down options
		for(i=0; i<elem.options.length;i++){

			// Only look at options that are selected
			if(elem.options[i].selected) {
				var rewardtext = elem.options[i].text; // Extract reward text
				var rewardindex = rewardtext.lastIndexOf(" - $"); // Find index of reward value (must be formatted like "Prize name - $1000")
				var rewardvalue = parseInt(rewardtext.substr(rewardindex + 4),10); // Extract reward value and convert to int

				// Store current reward value if it is greater than the current max value
				if(maxValue === undefined || maxValue < rewardvalue) {
					maxValue = rewardvalue
				}
			}
		}
    }
	return maxValue
}

function update_rewards(goalid, rewardid) {
	// Get values from the form
	var url = $("#goalsForm").attr("data-rewards-url");
    var contractId = $("#id_contractid").val();
    var goalId = $(goalid).val();
    
    $.ajax({                       				// initialize an AJAX request
      url: url,                    				// set the url of the request
      data: {
        'goalid': goalId,						// add variables to the GET parameters
        'contractid': contractId
      },
      success: function (data) {   				// "data" is the return of the "get students" view call
        $(rewardid).html(data);  				// replace the contents of the "partyuserinfo" field with the data
        $("#id_availablebudget").html(get_budget_HTML());	// Get and store initial values
        maxRewardValue = get_max_rewardValue();	
      }
    })
};

function update_all_rewards() {
	update_rewards(document.getElementById("id_e_goalid"), document.getElementById("id_e_rewardinfo"));
	update_rewards(document.getElementById("id_m_goalid"), document.getElementById("id_m_rewardinfo"));
	update_rewards(document.getElementById("id_d_goalid"), document.getElementById("id_d_rewardinfo"));
}
