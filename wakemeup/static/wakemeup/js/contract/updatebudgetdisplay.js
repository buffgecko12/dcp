// BUDGET: Parse out hidden variable values
var initialBudget = parseInt($("#id_initialbudget").val(),10); // Lookup initial values from hidden form fields
var initialContractValue = parseInt($("#id_initialcontractvalue").val(),10); // Lookup initial values from hidden form fields

// BUDGET: Format budget value for display
function update_budget_display(newContractValue = initialContractValue){
	var delta = initialContractValue - newContractValue	
	var newBudget = initialBudget + delta

	// Update budget display
	var currentBudgetHTML = undefined
	
	if(newBudget < 0) {
		currentBudgetHTML = '<span class="bg-warning">Presupuesto: $' + String(newBudget) + '</span>'
	} else {
		currentBudgetHTML = 'Presupuesto: $' + newBudget
	}
		
    $("#id_availablebudget").html(currentBudgetHTML);

    // Update buttons (negative budget = disabled)
	if(newBudget < 0) {
		disabledFlag = true;
	} else {
		disabledFlag = false;
	}

	document.getElementById("submit_cancel").disabled = disabledFlag;
	document.getElementById("submit_next").disabled = disabledFlag;
	
	try {
		document.getElementById("submit_previous").disabled = disabledFlag;
	}
	catch(error){}
}