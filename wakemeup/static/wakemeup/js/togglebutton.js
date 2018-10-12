// Wrapper function with timeout
function toggleButtonTimeout(buttoninfo, toggletype, timeout) {
	
	// Default timeout intervals
	if(!timeout) {
		if(toggletype == "enable") {
			timeout = 15000
		}
		else if (toggletype == "disable") {
			timeout = 0
		}
	}
	
	// Toggle buttons
	setTimeout( function() {
		toggleButton(buttoninfo, toggletype)
	},
	timeout)
}

// Toggle buttons
function toggleButton(buttoninfo, toggletype) {
	for (i=0; i < buttoninfo.length; i++) {
		
		// Extract button info
		var buttonname = buttoninfo[i].name
		var buttontype = buttoninfo[i].type
		var buttondisplayvalue_initial = buttoninfo[i].displayvalue_initial
		var buttondisplayvalue_submit = buttoninfo[i].displayvalue_submit
		
		var mybutton = $('#' + buttonname)
		
		// BUTTON TYPE: Button
		if(buttontype == "button") {

			// DISABLE
			if(toggletype == "disable") {
				mybutton.prop('disabled',true)
				
				// Update display value
				if(buttondisplayvalue_submit) {
					mybutton.val(buttondisplayvalue_submit)
				}
			} 
			// ENABLE
			else if (toggletype == "enable") {
				mybutton.prop('disabled',false)
				
				// Update display value
				if(buttondisplayvalue_initial) {
					mybutton.val(buttondisplayvalue_initial)
				}
			}
			
		// BUTTON TYPE: Link
		} else if (buttontype == "link") {
			
			// DISABLE
			if(toggletype == "disable") {
				mybutton.addClass('disabled')
			} 
			// ENABLE
			else if (toggletype == "enable") {
				mybutton.removeClass('disabled')
			}
		}
	} 
}