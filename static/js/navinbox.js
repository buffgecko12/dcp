// NOTIFICATIONS - Inbox icon click
$("#NotificationInboxIcon").on("click", function() {
	
	// Load notifications
	$.ajax({
		url : '/wakemeup/ajax/manage-user-display/',
		data : {'actiontype':'loadnotifications'},
		success: function(data) {
			$("#NotificationInboxItems").html(data);
		}
	})
});

// NOTIFICATIONS - Dropdown menu hide
$("#NotificationInboxDropdown").on("hide.bs.dropdown", function(){

	// Clear notifications
	$.ajax({
		url : '/wakemeup/ajax/manage-user-display/',
		data : {'actiontype':'clearnotifications'},
		success: function(data) {
			$("#NotificationInboxItems").html(""); // Clear dropdown
			$("#NotificationInboxIcon").attr('style','fill:grey;cursor:pointer;'); // Change inbox icon to grey
		}
	})
  });