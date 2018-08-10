var numParticipants = parseInt($("#id_numparticipants").val(),10);

//BUDGET: Update current budget	
function update_budget() {
	
	// Update budget display
	update_budget_display(get_current_budget())
}

//BUDGET: Get current budget	
function get_current_budget() {
	var totalBudget = 0
    var sel_list = ['e','m','d'] // Loop through all drop-downs

	// Calculate new budget (loop through all goals)
    for(j=0; j<sel_list.length; j++) {
    	var myGoalRewardInfo = document.getElementById('id_' + sel_list[j] + '_rewardinfo')
    	var myGoalMaxNumRewards = document.getElementById('id_' + sel_list[j] + '_maxnumrewards')

    	// Get current goal's max reward value
    	var goalMaxRewardValue = get_max_rewardValue(myGoalRewardInfo)
    	
    	// Get current goal's "max num reward" value
    	var goalMaxNumRewards = parseInt(myGoalMaxNumRewards.value,10)
    	var goalMaxNumRewards_Actual = ((Number.isInteger(goalMaxNumRewards)) ? goalMaxNumRewards : numParticipants); // Use specified max num rewards value if defined (otherwise, use number of participants)

    	// Calculate goal budget and update total budget
    	var goalBudget = goalMaxNumRewards_Actual * goalMaxRewardValue
    	
    	// Store goal budget as total budget (if larger than previous goal budget)
    	if(goalBudget > totalBudget) {
    		totalBudget = goalBudget
    	}
    }
	
	return totalBudget
}

// BUDGET: Get max reward value
function get_max_rewardValue(elem) {
    var maxValue = 0; // Set minimum value in case there are no elements selected
	
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
	return maxValue
}

// REWARDS: Update reward drop-down (used with Add Reward modal)
function update_rewards(goalid, rewardid) {
	// Get values from the form
	var url = $("#goalsForm").attr("data-rewards-url");
    var contractId = $("#id_contractid").val();
    var goalId = $(goalid).val();
    
    $.ajax({
      url: url,
      data: {
        'goalid': goalId,			// add variables to the GET parameters
        'contractid': contractId
      },
      success: function (data) {
        $(rewardid).html(data);
      }
    })
};

// REWARDS: Update all reward drop-downs
function update_all_rewards() {
	update_rewards(document.getElementById("id_e_goalid"), document.getElementById("id_e_rewardinfo"));
	update_rewards(document.getElementById("id_m_goalid"), document.getElementById("id_m_rewardinfo"));
	update_rewards(document.getElementById("id_d_goalid"), document.getElementById("id_d_rewardinfo"));
}