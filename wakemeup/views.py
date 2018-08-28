from django.contrib.auth import get_user_model

from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.urls import reverse

from django.core.validators import validate_email
from django.core.mail import send_mail

from django_tables2 import RequestConfig

from lib.UsefulFunctions.imgUtils import renderImageFromDb
from lib.UsefulFunctions.dateUtils import *
from lib.UsefulFunctions.dataUtils import *
from lib.UsefulFunctions.stringUtils import *
from lib.UsefulFunctions.httpUtils import *
from lib.UsefulFunctions.fileUtils import get_file_name_info

import psycopg2
import json

from .tables import *
from .forms import *
from .models.environment import School, Class, Teacher, Student, TeacherBudget, File
from .models.contract import Contract, ContractParty, ContractGoal, ContractGoalReward, Reward, ContractInfo

from users.models import UserReputationEvent, UserBadge, UserNotification

# Define user permission roles
PERM_NONE = ['NONE']
PERM_ADMIN = ['S','A']
PERM_SUPER = ['S']
PERM_TEACHER = ['TR']
PERM_STUDENT = ['ST']
PERM_ALL = ['ALL']

NO_PERM_REQUIRED = {'all': {'userrole':PERM_ALL, 'usertype':PERM_ALL}}

# Define view permissions
#TO-DO: Move to database
view_permissions = {
    'admin_list': {
        'school':{'userrole':PERM_ADMIN, 'usertype':PERM_NONE},
        'class':{'userrole':PERM_ADMIN, 'usertype':PERM_TEACHER},
        'teacher':{'userrole':PERM_ADMIN, 'usertype':PERM_TEACHER},
        'student':{'userrole':PERM_ADMIN, 'usertype':PERM_STUDENT},
        'reward':{'userrole':PERM_ADMIN, 'usertype':PERM_TEACHER},
    },
    'delete_object': {
        'school': {'userrole':PERM_ADMIN, 'usertype':PERM_NONE},
        'class': {'userrole':PERM_ADMIN, 'usertype':PERM_NONE},
        'teacher': {'userrole':PERM_ADMIN, 'usertype':PERM_NONE},
        'student': {'userrole':PERM_ADMIN, 'usertype':PERM_NONE},
        'reward': {'userrole':PERM_ADMIN, 'usertype':PERM_TEACHER},
        'contract': {'userrole':PERM_ADMIN, 'usertype':PERM_TEACHER},
        'usergroup': {'userrole':PERM_ADMIN, 'usertype':PERM_TEACHER},
    },
    'edit_object': {
        'school':{'userrole':PERM_ADMIN, 'usertype':PERM_NONE},
        'class':{'userrole':PERM_ADMIN, 'usertype':PERM_TEACHER},
        'teacher':{'userrole':PERM_ADMIN, 'usertype':PERM_TEACHER},
        'student':{'userrole':PERM_ADMIN, 'usertype':PERM_STUDENT},
        'reward':{'userrole':PERM_ADMIN, 'usertype':PERM_TEACHER},
    },
    'create_contract': {
        'all': {'userrole':PERM_ADMIN, 'usertype':PERM_TEACHER},
    },
    'addreward': {
        'all': {'userrole':PERM_ADMIN, 'usertype':PERM_TEACHER},
    },
    'edit_usergroup': {
        'all': {'userrole':PERM_ADMIN, 'usertype':PERM_TEACHER},
    },
    'add_user': {
        'all': {'userrole':PERM_SUPER, 'usertype':PERM_TEACHER},
    },
    'contract': NO_PERM_REQUIRED,
    'myaccount': NO_PERM_REQUIRED,
    'useragreement':NO_PERM_REQUIRED,
}

def download_file_fromdb(request, fileid):
    myfile = File.objects.get(fileid)

    # Allow access for "public" files (TO-DO: Update to be more inclusive)
    if(myfile.accessclass == "PB"):
        return getFileResponse(filedata = myfile.filedata, filename = myfile.filename + myfile.fileextension, filesize = myfile.filesize, contenttype = myfile.filetype)
    else:
        return redirect_home()

# Check user authentication / authorization
def check_permissions(view):
    viewname = view.__name__

    # Group create contract views together
    if(viewname[0:15] == 'create_contract'):
        viewname = "create_contract"
    elif(viewname[0:8] == 'contract'):
        viewname = "contract"
    
    def view_wrapper(*args, **kwargs):

        # Set objecttype (admin list)
        if('objecttype' in kwargs):
            objecttype = kwargs['objecttype']
        else:
            objecttype = 'all'

        myuser = args[0].user

        # Check user permissions
        if myuser.is_authenticated:

            # Look up school's data use policy requirements
            if(myuser.schoolid):
                datausepolicyrequiredflag = School.objects.get(schoolid=myuser.schoolid).datausepolicyfileid
            else:
                datausepolicyrequiredflag = True # Translates to value exists --> "policy not accepted"

            # Check if user has accepted data use policy and acceptance is required
            if(myuser.datausepolicyacceptedts or not datausepolicyrequiredflag or myuser.is_admin()):
                if (
                    myuser.userrole in view_permissions[viewname][objecttype]['userrole'] or view_permissions[viewname][objecttype]['userrole'][0] == 'ALL' or
                    myuser.usertype in view_permissions[viewname][objecttype]['usertype'] or view_permissions[viewname][objecttype]['usertype'][0] == 'ALL'
                ):
                    # Valid permission - continue
                    return view(*args, **kwargs)
            else:
                # Data use policy has not been accepted yet (and is required)
                return redirect('wakemeup:useragreement')
        else:
            # TO-DO: Re-direct to login page
            return redirect('login')
        
        # Invalid permission - redirect to homepage
        return redirect_home()
    
    return view_wrapper

def get_effective_contractid(contractid):

    # Determine which contractid to use
    try:
        mycontract = Contract.objects.get(contractid=contractid)
    
        # If contract is being revised, return tempcontractid
        if(mycontract.contractstatus == 'R' and mycontract.tempcontractid):
            return mycontract.tempcontractid
    except:
        pass

    return contractid

# AJAX Request handler
def get_contract_info(request):
    contractid = request.GET.get('contractid') # Check if existing contract
    infotype = request.GET.get('infotype')
    numparticipants = request.GET.get('numparticipants')
    returndata = ''
    
    if(contractid):
        if(infotype == "hypotheticalcontractvalue"):
            returndata = ContractInfo.objects.get_contract_value(contractid=contractid, numparticipants=numparticipants)[0].contractvalue
        else:
            mycontractinfo = ContractInfo.objects.get(contractid=contractid)
            returndata = eval('mycontractinfo.' + infotype)
    
    return HttpResponse(returndata)

# AJAX Request handler
def load_teachers(request):
    contractid = request.GET.get('contractid') # Check if existing contract

    # Determine which teachers to display
    # If existing contract, use contract teacheruserid
    if(contractid):
        teacheruserid = Contract.objects.get(contractid=contractid).teacheruserid
    # If logged on user is a teacher teacheruserid
    elif(request.user.usertype == 'TR'):
        teacheruserid = request.user.userid
    # Otherwise, return all teachers
    else:
        teacheruserid = None
    
    # Lookup teacher classes
    teachers = Teacher.objects.get_teachers(teacheruserid = teacheruserid)
    
    return render(request, 'wakemeup/admin/js/teacher_dropdown_list_options.html', {'teachers': teachers, 'teacheruserid':teacheruserid})

def load_classes(request):
    contractid = request.GET.get('contractid') # Check for existing contract
    teacheruserid = request.GET.get('teacheruserid') # Check selected teacher

    classid = None

    # If existing contract, use existing data
    if(contractid):
        mycontract = Contract.objects.get(contractid=contractid)
        classid = mycontract.classid
        teacheruserid = mycontract.teacheruserid

        classes = Class.objects.get_classes(classid=classid, teacheruserid = teacheruserid)
        
    # Lookup teacher classes
    elif teacheruserid:
        # If id = 0, include all teachers (used for add user form)
        if str(teacheruserid) == "0":
            teacheruserid = None
            
        classes = Class.objects.get_classes(classid=classid, teacheruserid = teacheruserid)
    else:
        classes = [] # Return empty list (create contract form)

    return render(request, 'wakemeup/admin/js/class_dropdown_list_options.html', {'classes': classes, 'classid': classid})

def load_students(request):

    # Contract
    contractid = request.GET.get('contractid')
    classid = request.GET.get('classid')
    
    # User groups
    groupuserid = request.GET.get('groupuserid')
    useridlist = request.GET.get('useridlist')
    leaderuserid = request.GET.get('leaderuserid')

    # Generate list of available participants
    if(classid):
        students = []

        # CONTRACTS: Add any user groups associated with class
        if(not contractid is None):

            # Get user groups associated with class
            classusergroups = UserGroup.objects.get_user_groups(classid=classid)
            
            # Convert user groups to "students"
            for usergroup in classusergroups:
                usergroup_student = Student(
                    studentuserid = usergroup.groupuserid,
                    classid = usergroup.classid,
                    firstname = usergroup.groupname
                )
                
                # Add user group to student list
                students.append(usergroup_student)
        
        # Add students for given class
        for mystudent in Student.objects.getclass(classid=classid):
            students.append(mystudent)
    else:
        students = []

    selected_user_list = []
    student_list = []
    
     # CONTRACTS
    if(contractid):
        mycontractparties = ContractParty.objects.get_contract_parties(contractid=contractid)

        for mycontractparty in mycontractparties:
            selected_user_list.append(mycontractparty.partyuserid)

    # USER GROUPS
    elif(classid): 
        
        # EXISTING GROUP
        if(groupuserid):

            # LEADER: Mark selected
            if(useridlist):
                selected_user_list = [int(leaderuserid) if leaderuserid else UserGroup.objects.get(groupuserid = groupuserid).leaderuserid,]

            # STUDENTS: Mark selected
            else:
                selected_user_list = UserGroup.objects.get(groupuserid = groupuserid).useridlist
            
        # LEADER: No users selected --> No leader available
        if(useridlist == ""):
            students = []
        
        # LEADER: Only return users in useridlist
        if(useridlist):
            students_revised = []
            
            myuseridlist = convert_array_string_to_int(useridlist)
            
            # Recreate student list
            for mystudent in students:
                if(mystudent.studentuserid in myuseridlist):
                    students_revised.append(mystudent)
            
            students = students_revised

    # Generate final student list (with appended user info)
    for mystudent in students:

        # Set flag to determine whether student is "selected"
        if(mystudent.studentuserid in selected_user_list):
            selected = True
        else:
            selected = False

        # Add updated student info to new student list
        student_list.append(
            {
                'studentuserid':mystudent.studentuserid, 
                'firstname':mystudent.firstname, 
                'lastname':mystudent.lastname, 
                'selected': selected
            }
        )

    students = student_list
    
    return render(request, 'wakemeup/admin/js/student_dropdown_list_options.html', {'students': students})

def load_rewards(request):
    contractid = request.GET.get('contractid') # Check if existing contract
    goalid = request.GET.get('goalid') # Check if existing contract
    userid = request.user.userid

    # Get all existing rewards for given goal
    if(contractid and goalid):
        selectedrewards = ContractGoalReward.objects.get_contract_rewards(contractid=contractid, goalid=goalid)        
        selectedrewards = [myreward.rewardid for myreward in selectedrewards]
        
    else:
        selectedrewards = []

    # Get all eligible rewards to display
    availablerewards = Reward.objects.get_rewards(createdbyuserid = userid)
    
    context = {
        'availablerewards': availablerewards,
        'selectedrewards': selectedrewards
    }
    
    return render(request, 'wakemeup/admin/js/reward_dropdown_list_options.html', context)

def manage_user_display(request):
    actiontype = request.GET.get('actiontype') # Check if existing contract

    # Load notifications
    if(actiontype == 'loadnotifications'):
        mynotifications = UserNotification.objects.get_notifications(userid=request.user.userid,activeonlyflag=False,maxrows=10)

        return render(request, 'wakemeup/navbar_usernotifications.html', {'usernotifications': mynotifications})

    # Set notifications as "seen"
    elif(actiontype == "clearusernotifications"):
        notificationtype = request.GET.get('notificationtype')
        get_user_model()(userid=request.user.userid).manage_display_info(actiontype='clearusernotifications',notificationtype=notificationtype)
        
    # Set notifications as "seen"
    elif(actiontype == "clearnewrepnotification"):
        get_user_model()(userid=request.user.userid).manage_display_info(actiontype='clearnewrepnotification')
        
    return HttpResponse()

# View to display images from DB
def preview_image(request, objecttype, objectid):
    if(objecttype == 'teacher'):
        img = Teacher.objects.get(objectid).defaultsignaturescanfile
    elif(objecttype == 'student'):
        img = Student.objects.get(objectid).defaultsignaturescanfile

    if(img):
        return renderImageFromDb(img)
    else:
        return HttpResponse()

def redirect_home():
    return redirect('wakemeup:index')        

@check_permissions
def delete_object(request, objecttype, objectid):
    
    if(objecttype == 'contract'):        
        myredirect = redirect('wakemeup:contract_list')
    elif(objecttype == 'usergroup'):
        # Redirect to class associated with user group after delete
        myusergroup = UserGroup.objects.get(groupuserid = objectid)
        myredirect = redirect('wakemeup:edit_object', objecttype = 'class', objectid=myusergroup.classid)
    else:
        myredirect = redirect('wakemeup:admin_list', objecttype = objecttype)
        
    if(request.method == 'POST'):
        # Set default redirect
        
        if(objecttype == 'contract'):
            myobject = Contract.objects.get(objectid)

            # Send notification when deleting non-draft contracts
            if myobject.contractstatus != 'D':
                sendnotifications = True
            else:
                sendnotifications = False

            # Delete contract
            myobject.delete(sendnotifications=sendnotifications)

            # Send notifications
            if(sendnotifications):
                myobject.send_emails(
                    email_subject = 'Duitama Colegio Project - Contrato (#' + str(myobject.contractid) + ') ha sido eliminado',
                    email_body = 'Se elimin' + mychr('o') + ' su contrato (#' + str(myobject.contractid) + ')'
                )
        else:

            if(objecttype == 'school'):
                myobject = School.objects.get(objectid)
                
            elif(objecttype == 'class'):
                myobject = Class.objects.get(objectid)
            
            elif(objecttype == 'usergroup'):

                # Delete if admin                
                if(request.user.is_admin()):
                    myobject = UserGroup.objects.get(objectid)

                # Verify user access
                elif(request.user.usertype == "TR"):
                    usergroup = UserGroup.objects.get(groupuserid = objectid)
                    myteacher = Teacher.objects.get(teacheruserid = request.user.userid)

                    # Allow delete if user group belongs to one of current user's classes
                    if(usergroup and myteacher):
                        if(myteacher.get_teacher_classes(classid = usergroup.classid)):
                            myobject = UserGroup.objects.get(objectid)
                    
            elif(objecttype == 'teacher'):
                myobject = Teacher.objects.get(objectid)
            
            elif(objecttype == 'student'):
                myobject = Student.objects.get(objectid)
            
            elif(objecttype == 'reward'):
                myobject = Reward.objects.get(objectid)
    
            if(myobject):
                myobject.delete()

    return myredirect

def index(request):
    return render(request, 'wakemeup/index.html')

def about(request):
    return render(request, 'wakemeup/about.html')

@check_permissions
def useragreement(request):
    # User has accepted the agreement
    if(request.method == "POST" and request.POST.get('acceptflag')):

        # Mark user as accepted and send back to homepage
        get_user_model()(userid=request.user.userid).manage_display_info(actiontype='acceptdatausepolicy')
        return redirect_home()
    
    # User has not accepted the agreement - display agreement form
    else:
        
        # Look up school's data use policy requirements
        if(request.user.schoolid):
            datausepolicyfileid = School.objects.get(schoolid=request.user.schoolid).datausepolicyfileid 
        else:
            datausepolicyfileid = None
    
        # Display agreement form
        return render(request, 'wakemeup/admin/useragreement.html', context={'datausepolicyfileid':datausepolicyfileid})

@check_permissions
def myaccount(request):
    if request.method == "POST":
        
        # Bind form data
        form = MyUserForm(request.POST, request.FILES, request=request)

        if(form.is_valid()):
            
            # Create user object
            myuser = get_user_model()(
                userid = form.cleaned_data.get('userid'),
                schoolid = form.cleaned_data.get('schoolid'),
                firstname = form.cleaned_data.get('firstname'),
                lastname = form.cleaned_data.get('lastname'),
                phonenumber = form.cleaned_data.get('phonenumber'),
                emailaddress = form.cleaned_data.get('emailaddress'),
                profilepictureid = form.cleaned_data.get('profilepictureid'),
            )

            # Save user
            myuser.save_user()
    else:
        myuser = get_user_model().objects.get(userid=request.user.userid)
        
        if(myuser):
            form=MyUserForm(request=request,
                initial={
                    'userid':myuser.userid,
                    'schoolid':myuser.schoolid,
                    'firstname':myuser.firstname,
                    'lastname':myuser.lastname,
                    'phonenumber':myuser.phonenumber,
                    'emailaddress':myuser.emailaddress,
                    'profilepictureid':myuser.profilepictureid,
                }
            )
        # Return empty form
        else:
            form=MyUserForm(request=request)

    # Get user objects
    myreputationevents = UserReputationEventsTable(UserReputationEvent.objects.get_events(userid=request.user.userid))
    mybadges = UserBadgesTable(UserBadge.objects.get_badges(userid=request.user.userid))

    # Config object for tables
    RequestConfig(request).configure(myreputationevents)
    RequestConfig(request).configure(mybadges)

    context = {
        'form': form,
        'reputationevents': myreputationevents,
        'badges': mybadges
        }

    return render(request, 'wakemeup/myaccount.html', context)

@check_permissions
def create_contract(request, contractid):

    # Get correct contractid to use (in case of revision)
    contractid_effective = get_effective_contractid(contractid)

    if(contractid != contractid_effective):
        revisionflag = True
    else:
        revisionflag = False
    
    # SAVE CONTRACT
    if request.method == "POST" and 'submit_other' not in request.POST: # Ignore submits from other forms

        # Create form instance (bind data to form)
        form = ContractForm(request.POST, request=request, contractid=contractid_effective, revisionflag = revisionflag)

        if(form.is_valid()):

            mycontract = Contract(
                contractid = form.cleaned_data.get('contractid'),
                contractname = form.cleaned_data.get('contractname'),
                teacheruserid = form.cleaned_data.get('teacheruserid'),
                classid = form.cleaned_data.get('classid'),
                contracttype = form.cleaned_data.get('contracttype'),
                contractvalidperiod = format_timestamp_range_db(form.cleaned_data.get('contractvalidstartdate'),form.cleaned_data.get('contractvalidenddate')),
                revisiondeadlinets = form.cleaned_data.get('revisiondeadlinets'),
                contractstatus = form.cleaned_data.get('contractstatus'),
                guardianapprovalflag = False,
            )

            # Prepare party user info
            partyuserinfo_dict = {
                'deletedparties': [], # Array of partyuserid values
                'currentparties': [], # Array of party user tuples
            }

            # Convert string array to int
            partyuserinfo = form.cleaned_data.get('partyuserinfo')
            partyuserinfo = convert_array_string_to_int_old(partyuserinfo)

            # Add contract parties to dictionary
            for myparty in partyuserinfo:
                partyuserinfo_dict['currentparties'].append(
                    {'partyuserid':myparty, 'contractrole':'PT'} # Add contract parties as participants
                )

            # Determine which parties were deleted
            if(form.cleaned_data.get('contractid')):
                deleted_parties = []
                mycontractparties = ContractParty.objects.get_contract_parties(contractid=contractid_effective)

                for mycontractparty in mycontractparties:
                    if(str(mycontractparty.partyuserid) not in partyuserinfo):
                        deleted_parties.append(mycontractparty.partyuserid)

                partyuserinfo_dict['deletedparties'] = deleted_parties
                    
            # Convert dict to json and assign to contract
            mycontract.partyuserinfo = json.dumps(partyuserinfo_dict)

            # Save contract
            originalcontractid = mycontract.contractid
            mycontract.contractid = mycontract.save()

            # For new contracts, set status to 'D'            
            if(not originalcontractid):
                mycontract.change_status('D')

            # Return to main page
            return redirect('wakemeup:create_contract_goals', contractid = contractid if revisionflag else mycontract.contractid)
              
    # NEW CONTRACT
    elif(contractid == 'new'):
        form = ContractForm(request=request, contractid=contractid,initial={'contractstatus':'D'}, revisionflag=revisionflag)
        
    # EDIT EXISTING CONTRACT
    else:
        # Lookup object
        mycontract = Contract.objects.get(contractid=contractid_effective)

        if(mycontract):
            # Populate existing form only for "Draft" contracts and if user is contract's owner or super / admin user
            if(mycontract.contractstatus in ('D','P') and (mycontract.teacheruserid == request.user.userid or request.user.userrole in PERM_ADMIN)):

                form = ContractForm(request=request, contractid=contractid_effective, revisionflag=revisionflag,
                    initial = {
                        'contractid': mycontract.contractid,
                        'contractname': mycontract.contractname,
                        'teacheruserid': mycontract.teacheruserid,
                        'classid': mycontract.classid,
                        'contracttype': mycontract.contracttype,
                        'contractvalidstartdate': mycontract.contractvalidperiod.lower,
                        'contractvalidenddate': mycontract.contractvalidperiod.upper,
                        'revisiondeadlinets': mycontract.revisiondeadlinets,
                        'contractstatus': mycontract.contractstatus,
                    }
                )
            else:
                # Unauthorized access
                return redirect_home() 

        # Handle off-case for invalid object id
        else:
            return redirect_home()
        
    return render(request, 'wakemeup/contract/edit_contract.html', {'form': form,'revisionflag':revisionflag})

@check_permissions
def create_contract_goals(request, contractid):

    # Get correct contractid to use (in case of revision)
    contractid_effective = get_effective_contractid(contractid)

    if(contractid != contractid_effective):
        revisionflag = True
    else:
        revisionflag = False
    
    # SAVE GOALS
    if request.method == "POST":

        # Create form instance (bind data to form)
        form = ContractGoalsForm(request.POST, contractid=contractid_effective, revisionflag=revisionflag)

        if(form.is_valid()):

            for goaltype in ('e','m','d'):
                goaltypeid = goaltype + '_'

                myrewardinfo = form.cleaned_data.get(goaltypeid + 'rewardinfo')
                mygoaldescription = form.cleaned_data.get(goaltypeid + 'goaldescription')
                mygoalid = form.cleaned_data.get(goaltypeid + 'goalid')
                mymaxnumrewards = form.cleaned_data.get(goaltypeid + 'maxnumrewards')
                myacceptedflag = form.cleaned_data.get(goaltypeid + 'acceptedflag')
                myrewardselectedby = form.cleaned_data.get(goaltypeid + 'rewardselectedby')
                
                # Only save goal if rewards and description have been specified
                if (myrewardinfo and mygoaldescription):
                    rewardinfo = convert_array_string_to_int_old(myrewardinfo)
                    rewardinfo_dict = {'currentrewards': []}
    
                    for myreward in rewardinfo:
                        rewardinfo_dict["currentrewards"].append({'rewardid':myreward})
    
                    rewardinfo_dict = json.dumps(rewardinfo_dict)
    
                    mycontractgoal = ContractGoal(
                        contractid = contractid_effective,
                        goalid = mygoalid,
                        difficultylevel = goaltype.upper(), # Difficultylevel
                        goaldescription = mygoaldescription,
                        acceptedflag = myacceptedflag,
                        rewardinfo = rewardinfo_dict,
                        maxnumrewards = mymaxnumrewards,
                        rewardselectedby = myrewardselectedby
                    )
        
                    # Save contract goal
                    mycontractgoal.goalid = mycontractgoal.save()
                # Delete existing goal
                elif (mygoalid):
                    ContractGoal(contractid = contractid_effective, goalid = mygoalid).delete()

            if('submit_previous' in request.POST):
                # Go to previous page
                return redirect('wakemeup:create_contract', contractid=contractid)
            else:
                # Go to preview/submit page
                return redirect('wakemeup:create_contract_submit', contractid=contractid)

    # EDIT EXISTING GOALS
    else:
        # Initialize initial_data 
        initial_data = {'contractid':contractid_effective}

        # Get contract goals
        mycontract = Contract.objects.get(contractid=contractid_effective)
        mygoals = ContractGoal.objects.get_contract_goals(contractid=contractid_effective)

        if(mycontract):
            if(mycontract.contractstatus in ('D','P') and (mycontract.teacheruserid == request.user.userid or request.user.userrole in PERM_ADMIN)):
                for mygoal in mygoals:
                    # Use difficultylevel (i.e. e/m/d) for id tag (assumes MAX one goal per difficultylevel)
                    goaltypeid = mygoal.difficultylevel.lower() + "_"
        
                    initial_data.update({
                        goaltypeid + 'goalid':mygoal.goalid,
                        goaltypeid + 'goaldescription':mygoal.goaldescription,
                        goaltypeid + 'rewardinfo':"",
                        goaltypeid + 'maxnumrewards':mygoal.maxnumrewards,
                        goaltypeid + 'acceptedflag':mygoal.acceptedflag,
                        goaltypeid + 'rewardselectedby':mygoal.rewardselectedby,
                        }
                    )
        
                form = ContractGoalsForm(contractid=contractid_effective, initial = initial_data, revisionflag=revisionflag)
            else:
                # Unauthorized access
                return redirect_home() 
        else:
            # Unauthorized access
            return redirect_home() 

    return render(request, 'wakemeup/contract/edit_contract_goals.html', {'form': form, 'revisionflag':revisionflag})

@check_permissions
def create_contract_submit(request, contractid):

    # Get correct contractid to use (in case of revision)
    contractid_effective = get_effective_contractid(contractid)

    if(contractid != contractid_effective):
        revisionflag = True
    else:
        revisionflag = False

    # SUBMIT
    if(request.method == "POST"):

        # Lookup original contract info
        mycontract_orig = Contract.objects.get(contractid=contractid)

        # DISCARD REVISION
        if('submit_discard' in request.POST):
            mycontract_orig.revise(actiontype='cancel')

            # Return to contract list            
            return redirect('wakemeup:contract_list')
        
        form = ContractSubmitForm(request.POST, contractid=contractid_effective, revisionflag=revisionflag)
        
        if(form.is_valid()):

            # Lookup contract info
            mycontract = Contract.objects.get(contractid=contractid_effective)

            # SUBMIT REVISION
            if(mycontract_orig.tempcontractid):
                revise_results = mycontract_orig.revise(
                    actiontype='submit',
                    revisiondescription=form.cleaned_data.get('revisiondescription'),
                    revisionrevoteflag=form.cleaned_data.get('revisionrevoteflag'),
                )

                # Get any newly added parties
                mynewparties = revise_results.get('newparties')

                # Send e-mails to original users
                myoriginalparties = revise_results.get('originalparties')
                if(myoriginalparties):
                    mycontract.send_emails(
                        email_subject = 'Duitama Colegio Project - Contrato (#' + str(contractid) + ') ha sido modificado',
                        email_body = 'Su contrato (#' + str(contractid) + ') ha sido modificado: ' + \
                            request.build_absolute_uri(reverse('wakemeup:contract_detail',kwargs={'contractid':contractid})),
                        useridlist = myoriginalparties
                    )

                # Send e-mails to users in "new parties" list (if any)
                if(mynewparties):
                    mycontract.send_emails(
                        email_subject = 'Duitama Colegio Project - Contrato nuevo (#' + str(contractid) + ')',
                        email_body = 'Se envi' + mychr('o') + ' un contrato nuevo: ' + \
                            request.build_absolute_uri(reverse('wakemeup:contract_detail',kwargs={'contractid':contractid})),
                        useridlist = mynewparties
                    )

            else:
                # Set contract status to pending
                mycontract.change_status('P') 

                # SUBMIT NEW CONTRACT
                if(mycontract_orig.contractstatus == 'D'):
                    # Send e-mails
                    mycontract.send_emails(
                        email_subject = 'Duitama Colegio Project - Contrato nuevo (#' + str(contractid) + ')',
                        email_body = 'Se envi' + mychr('o') + ' un contrato nuevo: ' + \
                            request.build_absolute_uri(reverse('wakemeup:contract_detail',kwargs={'contractid':contractid}))
                    )
                    
                # UPDATE EXISTING CONTRACT
                elif(mycontract_orig.contractstatus == 'P'):
                    # Send e-mails
                    mycontract.send_emails(
                        email_subject = 'Duitama Colegio Project - Contrato (#' + str(contractid) + ') ha sido actualizado',
                        email_body = 'Su contrato (#' + str(contractid) + ') ha sido actualizado: ' + \
                            request.build_absolute_uri(reverse('wakemeup:contract_detail',kwargs={'contractid':contractid}))
                    )

            # Go back to home page
            return redirect_home()
    else:
        mycontract = Contract.objects.get(contractid=contractid_effective)

        if(mycontract):
            if(mycontract.contractstatus in ('D','P') and (mycontract.teacheruserid == request.user.userid or request.user.userrole in PERM_ADMIN)):
        
                mycontract.contractvalidperiod_disp = display_timestamp_range(mycontract.contractvalidperiod) # Format for display
                classinfo = Class.objects.get(classid=mycontract.classid)
                contractinfo = ContractInfo.objects.get(contractid_effective)
                teacherbudgetinfo = TeacherBudget.objects.get(teacheruserid=mycontract.teacheruserid)
                
                # Prepare context info
                context = {
                    'form':ContractSubmitForm(contractid = contractid, revisionflag=revisionflag),
                    'contract':mycontract,
                    'classinfo':classinfo,
                    'contractinfo':contractinfo, #Contains budget info
                    'teacherbudgetinfo':teacherbudgetinfo,
                    'revisionflag':revisionflag,
                } 
        
                return render(request, 'wakemeup/contract/edit_contract_submit.html', context)

        # Unauthorized access
        return redirect_home() 

@check_permissions
def create_contract_revise(request, contractid):

    if(request.method == "POST"):
        mycontract = Contract.objects.get(contractid=contractid)
        
        # Start revision process for active contracts
        if(mycontract and mycontract.contractstatus == 'A'):
            mycontract.revise(actiontype='revise')
        
        return redirect('wakemeup:create_contract', contractid=contractid)

    # Unauthorized access
    return redirect_home() 

@check_permissions
def addreward(request):

    if request.method == 'POST':

        # Create form instance (bind data to form)
        form = RewardForm(request.POST)

        if form.is_valid():
            myreward = Reward(
                rewardid = form.cleaned_data.get('rewardid'),
                rewarddisplayname = form.cleaned_data.get('rewarddisplayname'),
                rewarddescription = form.cleaned_data.get('rewarddescription'),
                rewardvalue = form.cleaned_data.get('rewardvalue'),
                createdbyuserid=request.user.userid
            )

            # Save object
            myreward.save()

            return HttpResponse("Premio guardado.")
    else:
        form = RewardForm(cancel_type="button")

    return render(request, 'wakemeup/contract/edit_contract_goals_addreward.html', {'form': form})

@check_permissions
def edit_usergroup(request, classid):
    if request.method == 'POST':

        # Create form instance (bind data to form)
        form = UserGroupForm(request.POST,classid=classid)

        if form.is_valid():
            myusergroup = UserGroup(
                groupuserid = form.cleaned_data.get('groupuserid'),
                groupname = form.cleaned_data.get('groupname'),
                classid = form.cleaned_data.get('classid'),
                leaderuserid = form.cleaned_data.get('leaderuserid'),
                useridlist = convert_array_string_to_int(form.cleaned_data.get('useridlist'))
            )

            # Save user group
            myusergroup.save()

            # Return success response
            return HttpResponse("Grupo actualizado.")
    else:
        # Retrieve parameters
        groupuserid = request.GET.get('groupuserid')
        classid = request.GET.get('classid')

        # Initialize form
        form=UserGroupForm(
            classid=classid,
            initial={}
        )
        
        myusergroup = UserGroup.objects.get(groupuserid=groupuserid)

        # Add initial data (if existing object)        
        if(myusergroup):
            form.initial.update({
                'groupuserid' : myusergroup.groupuserid,
                'classid' : myusergroup.classid,
                'groupname' : myusergroup.groupname,
                'leaderuserid' : myusergroup.leaderuserid,
                'useridlist' : myusergroup.useridlist,
            })

    return render(request, 'wakemeup/admin/edit_usergroup.html', {'form': form})

# Admin
@check_permissions
def admin_list(request, objecttype):

    # Get teacheruserid (if teacher is logged on)
    if request.user.usertype == 'TR':
        teacheruserid = request.user.userid
    else:
        teacheruserid = None

    # Initialize empty object set    
    objectSet = []

    # Retrieve objects
    if objecttype == 'school':
        objectSet = SchoolsTable(School.objects.all())

    elif objecttype == 'class':
        objectSet = ClassesTable(Class.objects.get_classes(teacheruserid = teacheruserid))

    elif objecttype == 'teacher':
        objectSet = TeachersTable(Teacher.objects.get_teachers(teacheruserid = teacheruserid))

    elif objecttype == 'student':
        objectSet = StudentsTable(Student.objects.all())

    elif objecttype == 'reward':

        # Only show rewards created by logged on teacher
        if request.user.usertype == 'TR':
            createdbyuserid = request.user.userid
        else:
            createdbyuserid = None

        # Look up rewards
        objectSet = RewardsTable(Reward.objects.get_rewards(createdbyuserid = createdbyuserid))

    else:
        pass
        
    RequestConfig(request).configure(objectSet)
        
    return render(request, 'wakemeup/admin/index.html', {'objects' : objectSet, 'objecttype': objecttype})

@check_permissions
def edit_object(request, objecttype, objectid):
    form_template = 'wakemeup/admin/edit_form.html'
    contextkwargs = {}

    # Retrieve objects
    if objecttype == 'school':
        objectForm = SchoolForm
    elif objecttype == 'class':
        objectForm = ClassForm

        myteacherclass = None

        # Make sure teacher has access to class
        myteacher = Teacher.objects.get(teacheruserid = request.user.userid)
        
        if(myteacher):
            myteacherclass = myteacher.get_teacher_classes(classid=objectid)
        
        # Teachers can only view their own information
        if not (
            (request.user.usertype == 'TR' and myteacherclass) or
            request.user.is_admin()
        ):
            return redirect_home()

        if(objectid != "new"):
            usergroupstable = UserGroupsTable(UserGroup.objects.get_user_groups(classid = objectid))
            RequestConfig(request).configure(usergroupstable)
        else:
            usergroupstable = None

        contextkwargs.update({
            'studentgroups':usergroupstable, 
            'classid':objectid
        })


        
    elif objecttype == 'teacher':
        objectForm = TeacherForm

        # Teachers can only view their own information
        if not (
            (request.user.usertype == 'TR' and request.user.userid == int(objectid)) or
            request.user.is_admin()
        ):
            return redirect_home()

    elif objecttype == 'student':
        objectForm = StudentForm

        # Students can only view their own information
        if not (
            (request.user.usertype == 'ST' and request.user.userid == int(objectid)) or
            request.user.is_admin()
        ):
            return redirect_home()

    elif objecttype == 'reward':
        objectForm = RewardForm

        # Try to lookup object creator
        try:
            myreward = Reward.objects.get(rewardid=int(objectid))
            createdbyuserid = myreward.createdbyuserid
        except:
            createdbyuserid = None
        
        # Teachers can only view their own rewards
        if not (
            (request.user.usertype == 'TR' and request.user.userid == createdbyuserid) or
            request.user.is_admin() or
            objectid == 'new' # Used in case of adding a reward
        ):
            return redirect_home()

    else:
        pass

    # Lookup form's base class
    objectClass = objectForm.Meta.model

    # PROCESS FORM
    if request.method == 'POST' and 'submit_other' not in request.POST: # Ignore submits from other forms

        # Create form instance (bind data to form)
        form = objectForm(request.POST, request.FILES, request=request)

        if form.is_valid():
            
            kwargs = {}
            
            # Create new object
            if(objecttype == 'school'):

                # Capture data use policy file info
                originalpolicyfileid = request.POST.get("datausepolicyfileid") # Read in original fileid
                
                mydatausepolicyfileid = originalpolicyfileid or None
                mydatausepolicyfile = request.FILES.get('datausepolicyfile')

                # New file was uploaded
                if(mydatausepolicyfile):

                    # Read in binary data
                    mydatafile = convert_form_binary_to_db(mydatausepolicyfile)
                    
                    # Create new file object
                    myfile = File(
                        fileid = None,
                        filename = get_file_name_info(mydatausepolicyfile.name)['file_name'],
                        fileextension = get_file_name_info(mydatausepolicyfile.name)['file_extension'],
                        filesize = mydatausepolicyfile.size,
                        filetype = mydatausepolicyfile.content_type,
#                         description = 'File description',
                        filedata = psycopg2.Binary(mydatafile),
                        accessclass = 'PB' # File accessible to public
                    )
                    
                    # Save new file and capture fileid
                    mydatausepolicyfileid = myfile.save()
                    
                    # Delete old file (if exists)
                    if(originalpolicyfileid):
                        File(fileid=originalpolicyfileid).delete()
                
                # Process guardian approval policy
                guardianapprovalpolicy = json.dumps({'requiredfields':form.cleaned_data.get('guardianapprovalpolicy')})
                
                myobject = objectClass(
                    schoolid = form.cleaned_data.get('schoolid'),
                    schooldisplayname = form.cleaned_data.get('schooldisplayname'),
                    schoolabbreviation = form.cleaned_data.get('schoolabbreviation'),
                    address = form.cleaned_data.get('address'),
                    city = form.cleaned_data.get('city'),
                    department = form.cleaned_data.get('department'),
                    datausepolicyfileid = mydatausepolicyfileid,
                    guardianapprovalpolicy = guardianapprovalpolicy
                )

            elif(objecttype == 'class'):
                myobject = objectClass(
                    classid = form.cleaned_data.get('classid'),
                    schoolid = form.cleaned_data.get('schoolid'),
                    classdisplayname = form.cleaned_data.get('classdisplayname'),
                    gradelevel = form.cleaned_data.get('gradelevel'),
                )
                
            elif(objecttype == 'teacher'):

                # Get signature scan file
                mydatafile = convert_form_binary_to_db(request.FILES.get('defaultsignaturescanfile'))

                # Build original class list (values)
                initial_classes = []
                myobject = objectClass.objects.get(teacheruserid=form.cleaned_data.get('teacheruserid')) # Lookup teacher info

                if(myobject.classinfo):
                    for myclass in myobject.classinfo:
                        initial_classes.append(myclass['classid'])

                # Build current class list (dictionaries)
                current_classes_final = []
                current_classes_form = convert_string_array(form.cleaned_data.get('currentclasses'))
                
                for myclass in current_classes_form:
                    current_classes_final.append({'classid':myclass})
                
                # Generate class info field
                classinfo = json.dumps({
                    'deletedclasses' : subtract_arrays(initial_classes, current_classes_form),
                    'currentclasses' : current_classes_final
                })

                myobject = objectClass(
                    teacheruserid = form.cleaned_data.get('teacheruserid'),
                    schoolid = form.cleaned_data.get('schoolid'),
                    classinfo = classinfo,
                    firstname = form.cleaned_data.get('firstname'),
                    lastname = form.cleaned_data.get('lastname'),
                    defaultsignaturescanfile = psycopg2.Binary(mydatafile),
                    phonenumber = form.cleaned_data.get('phonenumber'),
                    emailaddress = form.cleaned_data.get('emailaddress'),
                    profilepictureid = form.cleaned_data.get('profilepictureid'),
                )
            
            elif(objecttype == 'student'):

                # Get signature scan file
                mydatafile = convert_form_binary_to_db(request.FILES.get('defaultsignaturescanfile'))
                
                myobject = objectClass(
                    studentuserid = form.cleaned_data.get('studentuserid'),
                    schoolid = form.cleaned_data.get('schoolid'),
                    classid = form.cleaned_data.get('classid'),
                    firstname = form.cleaned_data.get('firstname'),
                    lastname = form.cleaned_data.get('lastname'),
                    defaultsignaturescanfile = psycopg2.Binary(mydatafile),
                    phonenumber = form.cleaned_data.get('phonenumber'),
                    emailaddress = form.cleaned_data.get('emailaddress'),
                    profilepictureid = form.cleaned_data.get('profilepictureid'),
                )

            elif(objecttype == 'reward'):
                
                myobject = objectClass(
                    rewardid = form.cleaned_data.get('rewardid'),
                    rewarddisplayname = form.cleaned_data.get('rewarddisplayname'),
                    rewarddescription = form.cleaned_data.get('rewarddescription'),
                    rewardvalue = form.cleaned_data.get('rewardvalue'),
                    createdbyuserid = request.user.userid,
                )

            # Save object
            myobject.save(**kwargs)

            # Return to main page
            return redirect('wakemeup:admin_list', objecttype=objecttype)

    # CREATE FORM (NEW OBJECT)
    elif(objectid == 'new'):
        kwargs = {}
        
        if(objecttype == 'class'):
            kwargs = {'request':request}

        form = objectForm(**kwargs)

    # CREATE FORM (EXISTING OBJECT)
    else:
        
        # Lookup object
        myobject = objectClass.objects.get(objectid)
        
        # Create form
        if(myobject):
            if(objecttype == 'school'):
                form = objectForm(
                    initial = {
                        'schoolid': myobject.schoolid,
                        'schooldisplayname': myobject.schooldisplayname,
                        'schoolabbreviation': myobject.schoolabbreviation,
                        'address': myobject.address,
                        'city': myobject.city,
                        'department': myobject.department,
                        'datausepolicyfileid':myobject.datausepolicyfileid,
                        'guardianapprovalpolicy':myobject.guardianapprovalpolicy.get('requiredfields') if myobject.guardianapprovalpolicy else None
                    }
                )
            elif(objecttype == 'class'):
                form_template = 'wakemeup/admin/edit_class.html'
                
                form = objectForm(
                    initial = {
                        'classid': myobject.classid,
                        'schoolid': myobject.schoolid,
                        'classdisplayname': myobject.classdisplayname,
                        'gradelevel': myobject.gradelevel,
                    },
                    request=request
                )
                
            elif(objecttype == 'teacher'):
                form = objectForm(
                    initial = {
                        'teacheruserid': myobject.teacheruserid,
                        'schoolid': myobject.schoolid,
                        'currentclasses': myobject.get_classes_id(None),
                        'firstname': myobject.firstname,
                        'lastname': myobject.lastname,
                        'defaultsignaturescanfile': myobject.defaultsignaturescanfile,
                        'phonenumber': myobject.phonenumber,
                        'emailaddress': myobject.emailaddress,
                        'profilepictureid': myobject.profilepictureid,
                    }
                )
            
            elif(objecttype == 'student'):
                form = objectForm(
                    initial = {
                        'studentuserid': myobject.studentuserid,
                        'schoolid': myobject.schoolid,
                        'classid': myobject.classid,
                        'firstname': myobject.firstname,
                        'lastname': myobject.lastname,
                        'defaultsignaturescanfile': myobject.defaultsignaturescanfile,
                        'phonenumber': myobject.phonenumber,
                        'emailaddress': myobject.emailaddress,
                        'profilepictureid': myobject.profilepictureid,
                    }
                )

            elif(objecttype == 'reward'):
                form = objectForm(
                    initial = {
                        'rewardid': myobject.rewardid,
                        'rewarddisplayname': myobject.rewarddisplayname,
                        'rewarddescription': myobject.rewarddescription,
                        'rewardvalue': myobject.rewardvalue,
                    }
                )
                
        # Handle off-case for invalid object id
        else:
            return redirect_home()
        
    return render(request, form_template, {'form': form, 'objecttype':objecttype, **contextkwargs})

@check_permissions
def contract_detail(request, contractid):
    mycontract = Contract.objects.get(contractid=contractid)

    # Make sure contract exists
    if(mycontract):
        # Check contract is not a draft
        if(mycontract.contractstatus != 'D'):
            mycontract.contractvalidperiod_disp = display_timestamp_range(mycontract.contractvalidperiod) # Format for display
            classinfo = Class.objects.get(classid=mycontract.classid)
            contractinfo = ContractInfo.objects.get(contractid=contractid, allowrevisioncontractflag=True)
            
            # Prepare context info
            context = {
                'record':mycontract,
                'objecttype':'contract', # Used for contract button links
                'classinfo':classinfo,
                'contractinfo':contractinfo, #Contains budget info
                'displayinfo': {
                    'buttonsize':'', # Contract button size
                    'displaytextflag':False # Hide info text
                }
            } 
        
            return render(request, 'wakemeup/contract/detail.html', context)

    # Contract doesn't exist or is a "Draft"
    return redirect_home()
        
@check_permissions
def contract_accept(request, contractid):

    if(request.method == "POST"):
        form = ContractPartyAcceptForm(request.POST,request.FILES, request=request, contractid=contractid)
        
        # Determine where the button was clicked from
        post_source = request.POST.get('post_source')

        if(form.is_valid()):

#             mydatafile = convert_form_binary_to_db(request.FILES.get('partyapprovalsignature'))
            mycontractid = form.cleaned_data.get('contractid')
            mycontract = Contract.objects.get(contractid=mycontractid) # Used to generate e-mails
            
            # Process guardian approval info
            myguardianapprovalinfo = {'requiredfields':[]}
            
            for field in ('idfullname','idnumber','idissuedate','idissuelocation'):
                if(form.cleaned_data.get(field)):
                    myguardianapprovalinfo['requiredfields'].append({field:form.cleaned_data.get(field)})
            
            # Create new contractparty object
            mycontractparty = ContractParty(
                contractid = mycontractid,
                partyuserid = form.cleaned_data.get('partyuserid'),
                preferredgoalid = form.cleaned_data.get('preferredgoalid'),
#                 partyapprovalsignature = psycopg2.Binary(mydatafile),
                partylogonuserid = request.user.userid,
                guardianapprovalinfo = json.dumps(myguardianapprovalinfo)
            )

            # Accept contract
            approveresult = mycontractparty.approve_contract()
            
            # Send e-mails if contract approved by all parties
            if(approveresult):

                # Send e-mails
                mycontract.send_emails(
                    email_subject = 'Duitama Colegio Project - Contrato #' + str(mycontractid) + ' ha sido aprobado',
                    email_body = 'Se aprob' + mychr('o') + ' contrato #' + str(mycontractid) + '\n\n' + \
                        request.build_absolute_uri(reverse('wakemeup:contract_detail',kwargs={'contractid':mycontractid})),
                )
            
            # APPROVE CONTRACT (teacher) - Redirect to contract list
            if(post_source):
                return redirect('wakemeup:contract_list')
            
            # ACCEPT CONTRACT (student) - Return message
            else:
                return HttpResponse("Contrato ha sido aceptado.")
    else:
        initial = {
            'contractid': request.GET.get('contractid'),
            'partyuserid': request.GET.get('partyuserid'),
            'preferredgoalid': request.GET.get('preferredgoalid')
        }
        form = ContractPartyAcceptForm(initial=initial, request=request, contractid=contractid)

    return render(request, 'wakemeup/contract/approve_contract.html', {'form': form})

@check_permissions
def contract_list(request):
    
    # Determine which contracts to display
    if request.user.userrole in PERM_ADMIN:
        myargs = {} # Return all contracts
    elif(request.user.usertype == 'TR'):
        myargs = {'teacheruserid':request.user.userid} # Return only contracts tied to teacher
    else:
        myargs = {'partyuserid':request.user.userid,'excludedraftsflag':True} # Return only contracts related to student

    # Exclude un-necessary columns
    if(request.user.usertype == 'TR'):
        exclude = ('teacheruserid',)
    elif(request.user.usertype == 'ST'):
        exclude = ('classdisplayname',)
    else:
        exclude = ()
    
    contracts = ContractsTable(Contract.objects.get_contracts(**myargs), exclude=exclude, request=request)
    RequestConfig(request).configure(contracts)

    context = {
        'contracts': contracts
    }
        
    return render(request, 'wakemeup/contract/list.html', context)

@check_permissions
def add_user(request):
    
    if request.method == 'POST':
        # Go home if user clicks cancel
        if("submit_cancel" in request.POST):
            return redirect_home()
        
        # Bind form
        form = SignupForm(request.POST, request=request)

        if form.is_valid():

            # Store variables to reuse
            username = form.cleaned_data.get('username')

            # Generate password (if not provided)
            if(not form.cleaned_data.get('password1')):
                raw_password = get_user_model().objects.make_random_password()
            else:
                raw_password = form.cleaned_data.get('password1')

            # Check if username is an e-mail address
            try:
                validate_email(username)
                username_isemail = True
            except:
                username_isemail = False

            # If user provides e-mail address as username, use it as emailaddress if not provided
            if not form.cleaned_data.get('emailaddress') and username_isemail:
                myemailaddress = username
            else:
                myemailaddress = form.cleaned_data.get('emailaddress')

            # Create new user
            newuser = get_user_model().objects.create_user(
                password = raw_password, 
                schoolid = form.cleaned_data.get('schoolid'),
                username = username,
                usertype = form.cleaned_data.get('usertype'),
                firstname = form.cleaned_data.get('firstname'),
                lastname = form.cleaned_data.get('lastname'),
                defaultsignaturescanfile = form.cleaned_data.get('defaultsignaturescanfile'),
                phonenumber = form.cleaned_data.get('phonenumber'),
                emailaddress = myemailaddress,
                userrole = form.cleaned_data.get('userrole'),
            )

            # Send confirmation / review e-mail (only if e-mail provided)
            newuser.send_email(
                email_subject = "Duitama Colegio Project - Nueva cuenta de usuario",
                email_body = 'Se ha creado una nueva cuenta de usuario.  Se puede iniciar una nueva sesi' + mychr('o') + 'n aqu' + mychr('i') + ': ' + \
                             request.build_absolute_uri(reverse('login')) + '\n\n' + 
                             'Nombre de usuario: ' + newuser.username + '\n' + \
                             'Contrase' + mychr('n') + 'a: ' + raw_password + '\n' + \
                             'Nombre(s): ' + newuser.firstname + '\n' + \
                             'Apellido(s): ' + newuser.lastname + '\n' + \
                             'Correo: ' + newuser.emailaddress + '\n\n' + \
                             'Para cambiar su contrase' + mychr('n') + 'a, iniciar una sesi' + mychr('o') + 'n y haga click en "Mi Cuenta --> Cuenta"' + '\n\n' + \
                             'Saludos, ' + '\n\n' + \
                             'Duitama Colegio Project'
            )

            # If student, save additional data
            if(form.cleaned_data.get('usertype') == "ST"):
                mystudent = Student(studentuserid=newuser.userid,classid=form.cleaned_data.get("classid"))
                mystudent.save()

            # Go back to index page
            return render(request, 'wakemeup/admin/add_user_confirmation.html', {'userinfo':newuser, 'raw_password':raw_password})
    else:
        # Return empty form
        form = SignupForm(request=request)
        
    return render(request, 'wakemeup/admin/add_user.html', {'form': form})

def reset_password(email, from_email, template='registration/password_reset_email.html'):
    form = PasswordResetForm({'email':email})
    return form.save(from_email=from_email, email_template_name=template)