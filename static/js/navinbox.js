var manageUrl = '/wakemeup/ajax/manage-user-display/'
var $loading = $('.spinner').hide();

$(document)
  .ajaxStart(function () {
    $loading.show();
  })
  .ajaxStop(function () {
    $loading.hide();
  });


// Clear Reputation Value notification (called when user loads Reputation tab)
function clearReputationNotification() {
	// Set Reputation Value "seen" TS
	$.ajax({
		url : manageUrl,
		data : {'actiontype':'clearnewrepnotification'},
		success: function(data) {
			$("#ReputationValueDelta").fadeOut(); // Clear reputation delta notification
		}
	});
}
	
// NOTIFICATIONS - Show dropdown
$("#NotificationInboxIcon").on("click", function() {

	// Display spinner
	$("#NotificationInboxItems").html('<div class="spinner"><i class="fas fa-spinner fa-spin"></i></div>');
	
	// Load notifications
	$.ajax({
		url : manageUrl,
		data : {'actiontype':'loadnotifications'},
		success: function(data) {
			$("#NotificationInboxItems").html(data);
		}
	})
});

// NOTIFICATIONS - Hide dropdown
$("#NotificationInboxDropdown").on("hide.bs.dropdown", function(){

	// Clear notifications
	$.ajax({
		url : manageUrl,
		data : {'actiontype':'clearnotifications'},
		success: function(data) {
			$("#NotificationInboxIcon").attr('style','fill:grey;cursor:pointer;'); // Change inbox icon to grey
		}
	})
  });
