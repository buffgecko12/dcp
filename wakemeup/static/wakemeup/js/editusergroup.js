var mymainform =$("#editUserGroupForm");
var studentsurl = $(mymainform).attr("data-students-url");

// Store variable during form edit
var user_leaderuserid = undefined

// Generate User Group form
function update_usergroupform(type, groupuserid, classid) {
	var url = $(mymainform).attr("data-editusergroup-url");
	var redirecturl = $(mymainform).attr("data-redirect-url");

	if(type == "new") {
		requesttype = "GET";
	}
	else {
		requesttype = "POST";

		// Hidden values
		var groupuserid = $("#id_groupuserid").val();
		var classid = $("#id_classid").val();

		// User-provided values
		var groupname = $("#id_groupname").val();
		var leaderuserid = $("#id_leaderuserid").val();
		var useridlist = $("#id_useridlist").val().toString();		
	}

	$.ajax(
		{
			type:requesttype,
			url:url,
			data: {
				// Hidden form fields
				groupuserid:groupuserid,
				classid:classid,
				
				// User-provided fields
				groupname:groupname,
				leaderuserid:leaderuserid,
				useridlist:useridlist,
				
				// CSRF token
				csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value, // Pass CSRF token
			},
			success: function(data){
	            $("#mymodaldiv").html(data);
	            if(data == "Grupo actualizado.") {
		            setTimeout(
	            		function(){
			            	$('#editUserGroupModal').modal('hide'); // Close after a few seconds
			            	location.href=redirecturl
		            	},
		            	2000
	            	)
	            }
	        	update_students();
	        	
	        	// EVENT LISTENER (MODAL) - Change group members
	    	    $("#id_useridlist").on('keyup change', function(e) {
	    	    	update_leader()
	    	    })
	    	    
	        	// EVENT LISTENER (MODAL) - Cancel button
	            document.getElementById('cancel').onclick = function() {
	            	$('#editUserGroupModal').modal('hide')
	            	return false
	            }
			}
		}
	);
}

//DROP-DOWN: Students
function update_students() {

	// Hidden values
	var groupuserid = $("#id_groupuserid").val();
	var classid = $("#id_classid").val();

	// Get HTML for drop-down
	$.ajax({
		url: studentsurl,
		data: {
			'classid': classid,
			'groupuserid': groupuserid
		},
		success: function (data) {
			$("#id_useridlist").html(data);
			update_leader();
		}
	})
}

// DROP-DOWN: Leader
function update_leader() {

	// Hidden values
	var groupuserid = $("#id_groupuserid").val();
	var classid = $("#id_classid").val();

	// User values
	var useridlist = ($("#id_useridlist").val()).toString();
	var leaderuserid = ($("#id_leaderuserid").val());
	
	$.ajax({
		url: studentsurl,
		data: {
			'classid': classid,
			'groupuserid': groupuserid,
			'useridlist': useridlist,
			'leaderuserid': user_leaderuserid // Supply user-selected value
		},
		success: function (data) {
			$("#id_leaderuserid").html(data);
			user_leaderuserid = $("#id_leaderuserid").val()
		}
	})
}