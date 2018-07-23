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

import psycopg2
import json

from .tables import SchoolsTable, ClassesTable, TeachersTable, StudentsTable, ContractsTable, RewardsTable
from .forms import *
from .models.environment import School, Class, Teacher, Student, TeacherBudget
from .models.contract import Contract, ContractParty, ContractGoal, ContractGoalReward, Reward, ContractInfo

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
        'class':{'userrole':PERM_ADMIN, 'usertype':PERM_NONE},
        'teacher':{'userrole':PERM_ADMIN, 'usertype':PERM_TEACHER},
        'student':{'userrole':PERM_ADMIN, 'usertype':PERM_STUDENT},
        'reward':{'userrole':PERM_ADMIN, 'usertype':PERM_TEACHER},
    },
    'delete_object': {
        'school': {'userrole':PERM_ADMIN, 'usertype':PERM_NONE},
        'class': {'userrole':PERM_ADMIN, 'usertype':PERM_NONE},
        'teacher': {'userrole':PERM_ADMIN, 'usertype':PERM_NONE},
        'student': {'userrole':PERM_ADMIN, 'usertype':PERM_NONE},
        'reward': {'userrole':PERM_ADMIN, 'usertype':PERM_TEACHER}, # TO-DO: Update so user can only delete own objects
        'contract': {'userrole':PERM_ADMIN, 'usertype':PERM_TEACHER}, # TO-DO: Update so user can only delete own objects
    },
    'edit_object': {
        'school':{'userrole':PERM_ADMIN, 'usertype':PERM_NONE},
        'class':{'userrole':PERM_ADMIN, 'usertype':PERM_NONE},
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
    'add_user': {
        'all': {'userrole':PERM_SUPER, 'usertype':PERM_NONE},
    },
    'contract': NO_PERM_REQUIRED,
    'myaccount': NO_PERM_REQUIRED,
}

# Move to util library
def send_email(subject, body, sender, to_list):
    try:
        if(to_list):
            send_mail(subject, body, sender, to_list)
    except:
        print("ERROR - Could not send e-mail(s)")

    return

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
            if (
                myuser.userrole in view_permissions[viewname][objecttype]['userrole'] or view_permissions[viewname][objecttype]['userrole'][0] == 'ALL' or
                myuser.usertype in view_permissions[viewname][objecttype]['usertype'] or view_permissions[viewname][objecttype]['usertype'][0] == 'ALL'
            ):
                # Valid permission - continue
                return view(*args, **kwargs)
        else:
            # TO-DO: Re-direct to login page
            return redirect('login')
        
        # Invalid permission - redirect to homepage
        return redirect_home()
    
    return view_wrapper

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
        classes = Class.objects.get_classes(classid=classid, teacheruserid = teacheruserid)
    else:
        classes = []

    return render(request, 'wakemeup/admin/js/class_dropdown_list_options.html', {'classes': classes, 'classid': classid})

def load_students(request):
    
    contractid = request.GET.get('contractid')
    classid = request.GET.get('classid')

    if(classid):
        students = Student.objects.getclass(classid=classid) # Lookup students for given class
    else:
        students = []

    if(contractid):

         # Generate list of students associated with this contract
        contract_party_list = []
        contract_parties = ContractParty.objects.get_contract_parties(contractid=contractid)

        for mycontractparty in contract_parties:
            contract_party_list.append(mycontractparty.partyuserid)
        
        # Generate new student list (with appended contract user info)
        student_list = []

        for mystudent in students:
            # Set flag to determine whether student is part of contract
            if(mystudent.studentuserid in contract_party_list):
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
    else:
        myredirect = redirect('wakemeup:admin_list', objecttype = objecttype)
        
    if(request.method == 'POST'):
        # Set default redirect
        
        if(objecttype == 'school'):
            myobject = School.objects.get(objectid)
            
        elif(objecttype == 'class'):
            myobject = Class.objects.get(objectid)
        
        elif(objecttype == 'teacher'):
            myobject = Teacher.objects.get(objectid)
        
        elif(objecttype == 'student'):
            myobject = Student.objects.get(objectid)
        
        elif(objecttype == 'reward'):
            myobject = Reward.objects.get(objectid)

        elif(objecttype == 'contract'):
            myobject = Contract.objects.get(objectid)

        if(myobject):
            myobject.delete()

    return myredirect

def index(request):
    return render(request, 'wakemeup/index.html')

@check_permissions
def myaccount(request):
    
    if request.method == "POST":
        form = MyUserForm(request.POST, request.FILES)
        
        if(form.is_valid()):
            
            myuser = get_user_model()(
                userid = form.cleaned_data.get('userid'),
                firstname = form.cleaned_data.get('firstname'),
                lastname = form.cleaned_data.get('lastname'),
                phonenumber = form.cleaned_data.get('phonenumber'),
                emailaddress = form.cleaned_data.get('emailaddress'),
            )

            # Save user
            myuser.save()
    else:
        myuser = get_user_model().objects.get(userid=request.user.userid)
        if(myuser):
            form=MyUserForm(
                initial={
                    'userid':myuser.userid,
                    'firstname':myuser.firstname,
                    'lastname':myuser.lastname,
                    'phonenumber':myuser.phonenumber,
                    'emailaddress':myuser.emailaddress,
                }
            )
        else:
            form=MyUserForm()

    return render(request, 'wakemeup/myaccount.html', {'form':form})

@check_permissions
def create_contract(request, contractid):
    # SAVE CONTRACT
    if request.method == "POST" and 'submit_other' not in request.POST: # Ignore submits from other forms

        # Go to homepage if user clicked "cancel" button        
        if('submit_cancel' in request.POST):
            return redirect_home()
        
        # Create form instance (bind data to form)
        form = ContractForm(request.POST, request=request, contractid=contractid)

        if(form.is_valid()):

            mycontract = Contract(
                contractid = form.cleaned_data.get('contractid'),
                teacheruserid = form.cleaned_data.get('teacheruserid'),
                classid = form.cleaned_data.get('classid'),
                contracttype = form.cleaned_data.get('contracttype'),
                contractvalidperiod = format_timestamp_range_db(form.cleaned_data.get('contractvalidperiod'),'%d/%m/%Y'),
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
            partyuserinfo = convert_array_string_to_int(partyuserinfo)

            # Add contract parties to dictionary
            for myparty in partyuserinfo:
                partyuserinfo_dict['currentparties'].append(
                    {'partyuserid':myparty, 'contractrole':'PT'} # Add contract parties as participants
                )

            # Determine which parties were deleted
            if(form.cleaned_data.get('contractid')):
                current_parties = []
                mycontractparties = ContractParty.objects.get_contract_parties(contractid = contractid)

                for mycontractparty in mycontractparties:
                    current_parties.append(mycontractparty.partyuserid)

                partyuserinfo_dict['deletedparties'] = current_parties
                    
            # Convert dict to json and assign to contract
            mycontract.partyuserinfo = json.dumps(partyuserinfo_dict)

            # Save contract and set status to "Draft"
            mycontract.contractid = mycontract.save()
            mycontract.change_status('D')

            # Return to main page
            return redirect('wakemeup:create_contract_goals', contractid=mycontract.contractid)
              
    # NEW CONTRACT
    elif(contractid == 'new'):
        form = ContractForm(request=request, contractid=contractid,initial={'contractstatus':'D'})
        
    # EDIT EXISTING CONTRACT
    else:
        # Lookup object
        mycontract = Contract.objects.get(contractid=contractid)

        if(mycontract):
            # Populate exusting form only for "Draft" contracts and if user is contract's owner or super / admin user
            if(mycontract.contractstatus == 'D' and (mycontract.teacheruserid == request.user.userid or request.user.userrole in PERM_ADMIN)):
                contractvalidperiod = display_timestamp_range(mycontract.contractvalidperiod)

                form = ContractForm(request=request, contractid=contractid,
                    initial = {
                        'contractid': mycontract.contractid,
                        'teacheruserid': mycontract.teacheruserid,
                        'classid': mycontract.classid,
                        'contracttype': mycontract.contracttype,
                        'contractvalidperiod': contractvalidperiod,
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
        
    return render(request, 'wakemeup/contract/edit_contract.html', {'form': form})

@check_permissions
def create_contract_goals(request, contractid):
    # SAVE FORM
    if request.method == "POST":

        # Go to homepage if user clicked "cancel" button        
        if('submit_cancel' in request.POST):
            return redirect_home()
        
        # Create form instance (bind data to form)
        form = ContractGoalsForm(request.POST, contractid=contractid)

        if(form.is_valid()):

            for goaltype in ('e','m','d'):
                goaltypeid = goaltype + '_'

                myrewardinfo = form.cleaned_data.get(goaltypeid + 'rewardinfo')
                mygoaldescription = form.cleaned_data.get(goaltypeid + 'goaldescription')
                mygoalid = form.cleaned_data.get(goaltypeid + 'goalid')

                # Only save goal if rewards and description have been specified
                if (myrewardinfo and mygoaldescription):
                    rewardinfo = convert_array_string_to_int(myrewardinfo)
                    rewardinfo_dict = {'currentrewards': []}
    
                    for myreward in rewardinfo:
                        rewardinfo_dict["currentrewards"].append({'rewardid':myreward})
    
                    rewardinfo_dict = json.dumps(rewardinfo_dict)
    
                    mycontractgoal = ContractGoal(
                        contractid = contractid,
                        goalid = mygoalid,
                        difficultylevel = goaltype.upper(), # Difficultylevel
                        goaldescription = mygoaldescription,
#                         acceptedflag = False,
                        rewardinfo = rewardinfo_dict
                    )
        
                    # Save contract goal
                    mycontractgoal.goalid = mycontractgoal.save()
                # Delete existing goal
                elif (mygoalid):
                    ContractGoal(contractid = contractid, goalid = mygoalid).delete()

            if('submit_previous' in request.POST):
                # Go to previous page
                return redirect('wakemeup:create_contract', contractid=contractid)
            else:
                # Go to preview/submit page
                return redirect('wakemeup:create_contract_submit', contractid=contractid)
              
#     # NEW GOALS
#     elif(contractid == 'new'):
#         form = ContractGoalsForm(contractid=contractid)
        
    # EDIT EXISTING GOAL
    else:
        # Initialize initial_data 
        initial_data = {'contractid':contractid}

        # Get contract goals
        mycontract = Contract.objects.get(contractid=contractid)
        mygoals = ContractGoal.objects.get_contract_goals(contractid=contractid)

        if(mycontract):
            if(mycontract.contractstatus == 'D' and (mycontract.teacheruserid == request.user.userid or request.user.userrole in PERM_ADMIN)):
                for mygoal in mygoals:
                    # Use difficultylevel (i.e. e/m/d) for id tag (assumes MAX one goal per difficultylevel)
                    goaltypeid = mygoal.difficultylevel.lower() + "_"
        
                    initial_data.update({
                        goaltypeid + 'goalid':mygoal.goalid,
                        goaltypeid + 'goaldescription':mygoal.goaldescription,
                        goaltypeid + 'rewardinfo':"",
                        }
                    )
        
                form = ContractGoalsForm(contractid=contractid, initial = initial_data)
            else:
                # Unauthorized access
                return redirect_home() 
        else:
            # Unauthorized access
            return redirect_home() 

    return render(request, 'wakemeup/contract/edit_contract_goals.html', {'form': form, 'addRewardForm': RewardForm()})

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
        form = RewardForm

    return render(request, 'wakemeup/contract/edit_contract_goals_addreward.html', {'form': form})

@check_permissions
def create_contract_submit(request, contractid):

    if(request.method == "POST"):

        # Go to homepage if user clicked "cancel" button        
        if('submit_cancel' in request.POST):
            return redirect_home()
        # Go to previous page
        elif('submit_previous' in request.POST):
            return redirect('wakemeup:create_contract_goals',contractid = contractid)
        
        form = ContractSubmitForm(request.POST, contractid=contractid)
        if(form.is_valid()):
            
            # Change status to "Pending"
            mycontract = Contract.objects.get(contractid=contractid)
            mycontract.change_status('P') # Change contract status to pending

            # Get teacher's e-mail
            myteacheremail = Teacher.objects.get(teacheruserid = mycontract.teacheruserid).emailaddress

            # Generate e-mail list
            contractpartyemail_list = []
            
            for contractparty in mycontract.partyuserinfo['currentparties']:
                contractpartyemail_list.append(contractparty['emailaddress'])

            EMAIL_FROM = 'duitamacolegioproject@gmail.com'
            EMAIL_SUBJECT = 'Contrato nuevo (#' + str(contractid) + ')'
            EMAIL_BODY = 'Se envi' + mychr('o') + ' un contrato nuevo: ' + request.build_absolute_uri(reverse('wakemeup:contract_detail',kwargs={'contractid':contractid}))

            # Send e-mails
            send_email(EMAIL_SUBJECT, EMAIL_BODY, EMAIL_FROM, contractpartyemail_list)
            send_email(EMAIL_SUBJECT, EMAIL_BODY, EMAIL_FROM, [myteacheremail])

            # Go back to home page
            return redirect_home()
    else:
        mycontract = Contract.objects.get(contractid=contractid)

        if(mycontract):
            if(mycontract.contractstatus == 'D' and (mycontract.teacheruserid == request.user.userid or request.user.userrole in PERM_ADMIN)):
        
                mycontract.contractvalidperiod_disp = display_timestamp_range(mycontract.contractvalidperiod) # Format for display
                classinfo = Class.objects.get(classid=mycontract.classid)
                contractinfo = ContractInfo.objects.get(contractid)
                teacherbudgetinfo = TeacherBudget.objects.get(teacheruserid=mycontract.teacheruserid)
                
                # Prepare context info
                context = {
                    'form':ContractSubmitForm(contractid = contractid),
                    'contract':mycontract,
                    'classinfo':classinfo,
                    'contractinfo':contractinfo, #Contains budget info
                    'teacherbudgetinfo':teacherbudgetinfo
                } 
        
                return render(request, 'wakemeup/contract/edit_contract_submit.html', context)

        # Unauthorized access
        return redirect_home() 
    
# Admin
@check_permissions
def admin_list(request, objecttype):

    # Initialize empty object set    
    objectSet = []

    # Retrieve objects
    if objecttype == 'school':
        objectSet = SchoolsTable(School.objects.all())

    elif objecttype == 'class':
        objectSet = ClassesTable(Class.objects.all())

    elif objecttype == 'teacher':
    
        # Only list info for logged on teacher
        if request.user.usertype == 'TR':
            teacheruserid = request.user.userid
        else:
            teacheruserid = None
            
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
        objectSet = RewardsTable(Reward.objects.get_rewards(createdbyuserid = createdbyuserid, globalflag = False))

    else:
        pass
        
    RequestConfig(request).configure(objectSet)
        
    return render(request, 'wakemeup/admin/index.html', {'objects' : objectSet, 'objecttype': objecttype})

@check_permissions
def edit_object(request, objecttype, objectid):

    # Retrieve objects
    if objecttype == 'school':
        objectForm = SchoolForm
    elif objecttype == 'class':
        objectForm = ClassForm
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

        # Go to main admin page if user clicked "cancel" button        
        if('submit_cancel' in request.POST):
            return redirect('wakemeup:admin_list',objecttype = objecttype)
        
        # Create form instance (bind data to form)
        form = objectForm(request.POST, request.FILES)

        if form.is_valid():
            
            kwargs = {}
            
            # Create new object
            if(objecttype == 'school'):
                myobject = objectClass(
                    schoolid = form.cleaned_data.get('schoolid'),
                    schooldisplayname = form.cleaned_data.get('schooldisplayname'),
                    schoolabbreviation = form.cleaned_data.get('schoolabbreviation'),
                    address = form.cleaned_data.get('address'),
                    city = form.cleaned_data.get('city'),
                    department = form.cleaned_data.get('department'),
                )

            elif(objecttype == 'class'):
                myobject = objectClass(
                    classid = form.cleaned_data.get('classid'),
                    schoolid = form.cleaned_data.get('schoolid'),
                    classdisplayname = form.cleaned_data.get('classdisplayname'),
                )
                
                students = form.cleaned_data.get('students')

                # Assign students to class
                if(students):
                    # Save class before adding students to it
                    if(myobject.classid is None):
                        myobject.classid = myobject.save()
                    
                    for mystudent in students:
                        newstudent = Student(studentuserid=mystudent,classid=myobject.classid)
                        newstudent.save()
            
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
            return admin_list(request, objecttype = objecttype)

    # CREATE FORM (NEW OBJECT)
    elif(objectid == 'new'):
        form = objectForm()

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
                        'department': myobject.department
                    }
                )
            elif(objecttype == 'class'):
                form = objectForm(
                    initial = {
                        'classid': myobject.classid,
                        'schoolid': myobject.schoolid,
                        'classdisplayname': myobject.classdisplayname,
                    }
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
        
    return render(request, 'wakemeup/admin/edit_form.html', {'form': form})

@check_permissions
def contract_detail(request, contractid):
    mycontract = Contract.objects.get(contractid=contractid)

    if(mycontract):
        mycontract.contractvalidperiod_disp = display_timestamp_range(mycontract.contractvalidperiod) # Format for display
        classinfo = Class.objects.get(classid=mycontract.classid)
        contractinfo = ContractInfo.objects.get(contractid)
        
        # Prepare context info
        context = {
            'form':ContractSubmitForm(contractid = contractid),
            'contract':mycontract,
            'classinfo':classinfo,
            'contractinfo':contractinfo, #Contains budget info
        } 
    
        return render(request, 'wakemeup/contract/detail.html', context)
    else:
        return redirect_home()
        
@check_permissions
def contract_accept(request):

    if(request.method == "POST"):
        form = ContractPartyAcceptForm(request.POST,request.FILES)

        if(form.is_valid()):

            mydatafile = convert_form_binary_to_db(request.FILES.get('partyapprovalsignature'))
            mycontractid = form.cleaned_data.get('contractid')
            
            # Create new contractparty object
            mycontractparty = ContractParty(
                contractid = mycontractid,
                partyuserid = form.cleaned_data.get('partyuserid'),
                preferredgoalid = form.cleaned_data.get('preferredgoalid'),
                partyapprovalsignature = psycopg2.Binary(mydatafile),
                partylogonuserid = request.user.userid,
            )
            
            # Accept contract
            mycontractparty.approve_contract()

            # Redirect
            return redirect('wakemeup:contract_detail', mycontractid)
    else:
        return redirect_home()

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
        form = SignupForm(request.POST)

        if form.is_valid():

            # Store variables to reuse
            username = form.cleaned_data.get('username')
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
            get_user_model().objects.create_user(
                raw_password, 
                username,
                form.cleaned_data.get('usertype'),
                form.cleaned_data.get('firstname'),
                form.cleaned_data.get('lastname'),
                form.cleaned_data.get('defaultsignaturescanfile'),
                form.cleaned_data.get('phonenumber'),
                myemailaddress,
                form.cleaned_data.get('userrole'),
            )

            # Login as newly created user
#             myuser = authenticate(username=username, password=raw_password)
#             login(request, user)

            # Go back to index page
            return index(request)
    else:
        # Return empty form
        form = SignupForm()
        
    return render(request, 'wakemeup/admin/edit_form.html', {'form': form})