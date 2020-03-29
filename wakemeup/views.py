from django.contrib.auth import get_user_model
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.urls import reverse
from django.core.validators import validate_email
from django.core.mail import send_mail
from django.forms.models import formset_factory

from lib.UsefulFunctions.imgUtils import renderImageFromDb
from lib.UsefulFunctions.dateUtils import *
from lib.UsefulFunctions.dataUtils import *
from lib.UsefulFunctions.stringUtils import *
from lib.UsefulFunctions.httpUtils import *
from lib.UsefulFunctions.fileUtils import get_file_name_info
from lib.UsefulFunctions.googleUtils import GoogleDrive

from django_tables2 import RequestConfig

import psycopg2

from wakemeup.tables import *
from wakemeup.forms import *
from wakemeup.models.school import *
from wakemeup.models.program import *
from wakemeup.models.environment import *
from user.models.user import UserReputationEvent, UserBadge, UserNotification
from user.models.authorization import Object

def download_file_fromdb(request, fileid):
    myfile = File.objects.get(fileid)

    # Allow access for "public" files (TO-DO: Update to be more inclusive)
    if(myfile.accessrules == "PB"):
        return getFileResponse(filedata = myfile.filedata, filename = myfile.filename + myfile.fileextension, filesize = myfile.filesize, contenttype = myfile.filetype)
    else:
        return redirect_home()

# Check authentication (logged in)
def check_authentication(view):
    
    def view_wrapper(*args, **kwargs):
        myuser = args[0].user

        # Check user is logged on
        if myuser.is_authenticated:
            return view(*args, **kwargs)
        else:
            return redirect('login')
        
    return view_wrapper

# Check authorization (logged in & permissions)
def check_authorization(view):
    
    def view_wrapper(*args, **kwargs):

        # Parse out view info
        viewname = view.__name__ # i.e. "create_contract"
        viewname_split = viewname.split("_")
        
        # Get action & object
        view_action = viewname_split[0]
        view_object = viewname_split[1] if len(viewname_split) > 1 else None # Use second index of view name (if specified)
    
        # Convert to access levels
        if(view_action == "list"):
            myrequestedaccesslevel = 1
            
        elif(view_action == "get"):
            myrequestedaccesslevel = 4
            
        elif(view_action == "edit"):
            if(kwargs.get('objectid') == "new"):
                myrequestedaccesslevel = 10 # Create
            else:
                myrequestedaccesslevel = 8 # Edit
                
        elif(view_action == "create"):
            myrequestedaccesslevel = 10
            
        elif(view_action == "delete"):
            myrequestedaccesslevel = 12
            
        else:
            myrequestedaccesslevel = 1 # Browse
        
        myuser = args[0].user

        # Check user is logged on
        if myuser.is_authenticated:

            # Get object
            if(view_action in ('list','get','edit','create','delete')):
                myobject = Object.objects.get_object_by_name(objectname=kwargs.get('objecttype') or view_object) # business object
            else:
                myobject = Object.objects.get_object_by_name(objectname=viewname) # view

            # Check valid object
            if(myobject):

                # Check user has requested access to object
                if (myuser.check_access(objectid=myobject.objectid,objectclass=myobject.objectclass,requestedaccesslevel=myrequestedaccesslevel)):
                    
                    # Valid permission - continue
                    return view(*args, **kwargs)
        else:
            # Not authenticated - redirect to login page
            return redirect('login')
        
        # Not authorized - redirect to homepage (TO-DO: Create "not authorized" page
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
    
    return render(request, 'wakemeup/admin/menus/teacher_options.html', {'teachers': teachers, 'teacheruserid':teacheruserid})

def load_classes(request):
    contractid = request.GET.get('contractid') # Check for existing contract
    schoolid = request.GET.get('schoolid') # Check for existing school
    teacheruserid = request.GET.get('teacheruserid') # Check selected teacher

    classid = None

    # If existing contract, use existing data
    if(contractid):
        mycontract = Contract.objects.get(contractid=contractid)
        classid = mycontract.classid
        teacheruserid = mycontract.teacheruserid

        classes = Class.objects.get_classes(classid=classid, teacheruserid = teacheruserid)
        
    elif(schoolid):
        classes = Class.objects.get_classes(schoolid=schoolid)
        
    # Lookup teacher classes
    elif (teacheruserid):
        
        # If id = 0, include all teachers (used for add user form)
        if str(teacheruserid) == "0":
            teacheruserid = None
            
        classes = Class.objects.get_classes(teacheruserid = teacheruserid)
        
    else:
        classes = [] # Return empty list (create contract form)

    return render(request, 'wakemeup/admin/menus/class_options.html', {'classes': classes, 'classid': classid})

def load_rewards(request):
    contractid = request.GET.get('contractid') # Check if existing contract
    userid = request.user.userid

    # Get all existing rewards for given goal
    if(contractid):
        selectedrewards = ContractPartyReward.objects.get_contract_party_rewards(contractid=contractid)        
        selectedrewards = [myreward.rewardid for myreward in selectedrewards]
        
    else:
        selectedrewards = []

    context = {
        'selectedrewards': selectedrewards
    }
    
    return render(request, 'wakemeup/admin//reward_options.html', context)

def manage_user_display(request):
    actiontype = request.GET.get('actiontype') # Check if existing contract

    # Load notifications
    if(actiontype == 'loadnotifications'):
        mynotifications = UserNotification.objects.get_notifications(userid=request.user.userid,activeonlyflag=False,maxrows=10)

        return render(request, 'wakemeup/notifications.html', {'usernotifications': mynotifications})

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

    if(img):
        return renderImageFromDb(img)
    else:
        return HttpResponse()

def redirect_home():
    return redirect('wakemeup:index')        

@check_authorization
def delete_object(request, objecttype, objectid):
    
    if(objecttype == 'contract'):        
        myredirect = redirect('wakemeup:list_contract')
    else:
        myredirect = redirect('wakemeup:list_object', objecttype = objecttype)
        
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
            
            elif(objecttype == 'teacher'):
                myobject = Teacher.objects.get(objectid)
            
            elif(objecttype == 'reward'):
                myobject = Reward.objects.get(objectid)
    
            if(myobject):
                myobject.delete()

    return myredirect

def index(request):
    return render(request, 'wakemeup/index.html')

def about(request):
    return render(request, 'wakemeup/about.html')

@check_authentication
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
                    'emailaddress':myuser.emailaddress,
                    'profilepictureid':myuser.profilepictureid,
                }
            )
        # Return empty form
        else:
            form=MyUserForm(request=request)

    # Get user objects
    myreputationevents = UserReputationEventsTable(UserReputationEvent.objects.get_events(userid=request.user.userid), orderable=False)
    mybadges = UserBadgesTable(UserBadge.objects.get_badges(userid=request.user.userid), orderable=False)

    # Config object for tables
    RequestConfig(request).configure(myreputationevents)
    RequestConfig(request).configure(mybadges)

    context = {
        'form': form,
        'reputationevents': myreputationevents,
        'badges': mybadges
        }

    return render(request, 'wakemeup/myaccount.html', context)

def create_file(request):

    if request.method == "POST":
        
        # Bind form data
        form = UploadFileForm(request.POST,request.FILES,request=request)

        if(form.is_valid()):

            # Connect to Google Drive
            gd = GoogleDrive(permissions=['write'])
            
            results = gd.connection.files().list(pageSize=100, fields="nextPageToken, files(id, name)").execute()
            items = results.get('files', [])
            
            if not items:
                print('No files found.')
            else:
                print('Files:')
                for item in items:
                    print(u'{0} ({1})'.format(item['name'], item['id']))

            
            filetype = form.cleaned_data.get('filetype')

            contractfiletypes = Category.objects.get_categories(categoryclass='contractfile')

            # Look up default upload directory
            if(filetype == "contractupload"):
                pass

                # use teacheruserid / schoolyear (TeacherProgram / File)
#                 parentdirectory = File.objects.get_files()

            # Loop through files
            files = [request.FILES.get('file[%d]' % i)
                 for i in range(0, len(request.FILES))]

            for myfile in files:

                myfiletype = get_matching_item(contractfiletypes,'categorytype',filetype).categorydisplayname # In loop in case filetype is applied at this level

                file_metadata = {
                    'name': myfiletype + ' - ' + myfile.name,
                    'originalFilename': myfile.name,
                    'description':'Archivo subido por ' + request.user.userdisplayname,
                    'parents':['18INeTgh1KIDUHLes92--nBFLdQPW7k-z'], # Upload directory # TO-DO: Update with correct value
#                     'appProperties':{'drivepath': get_gd_fileid(gd_storage, request, schoolyear, 'contractupload')}
                }

                # Create file on Google Drive
                file = gd.create_file(
                    metadata = file_metadata,
                    file_data = myfile,
                    fields = ('id,mimeType,description,fileExtension,size')
                )

                # Create file in repository
                newfile = File(
                    filename=myfile.name,
                    fileextension=file.get('fileExtension'),
                    filesize=file.get('size'),
                    filetype=file.get('mimeType'),
                    filedescription=file.get('description'),
                    filesource='GD',
                    filedata=None,
                    filecategory=filetype,
                    alternatefileid=file.get('id'),
                    schoolyear=form.cleaned_data.get('schoolyear'),
                    schoolid=form.cleaned_data.get('schoolid')
                )

                newfile.fileid = newfile.save()['fileid']

    else:
        form = UploadFileForm(request=request)
        
    return render(request, 'wakemeup/admin/upload.html',context={'form':form})



@check_authorization
def create_contract(request, contractid):

    # SAVE CONTRACT
    if request.method == "POST":

        # Create form instance (bind data to form)
        form = ContractForm(request.POST, request=request, contractid=contractid)

        if(form.is_valid()):

            mycontract = Contract(
                contractid = form.cleaned_data.get('contractid'),
                contractname = form.cleaned_data.get('contractname'),
                teacheruserid = form.cleaned_data.get('teacheruserid'),
                classid = form.cleaned_data.get('classid'),
                contractvalidperiod = format_timestamp_range_db(form.cleaned_data.get('contractvalidstartdate'),form.cleaned_data.get('contractvalidenddate')),
                contractstatus = form.cleaned_data.get('contractstatus'),
            )

            # Save contract
            originalcontractid = mycontract.contractid
            mycontract.contractid = mycontract.save()

    # NEW CONTRACT
    elif(contractid == 'new'):
        form = ContractForm(request=request, contractid=contractid)
        
    # EDIT EXISTING CONTRACT
    else:
        # Lookup object
        mycontract = Contract.objects.get(contractid=contractid)

        if(mycontract):
            # Populate existing form only for "Draft" contracts and if user is contract's owner or super / admin user
            if(mycontract.teacheruserid == request.user.userid or request.user.is_admin): # TO-DO: Update to check permissions

                form = ContractForm(request=request, contractid=contractid,
                    initial = {
                        'contractid': mycontract.contractid,
                        'contractname': mycontract.contractname,
                        'teacheruserid': mycontract.teacheruserid,
                        'classid': mycontract.classid,
                        'contractvalidstartdate': mycontract.contractvalidperiod.lower,
                        'contractvalidenddate': mycontract.contractvalidperiod.upper,
                        'contractstatus': mycontract.contractstatus,
                    }
                )
            else:
                # Unauthorized access
                return redirect_home() 

        # Handle off-case for invalid object id
        else:
            return redirect_home()
        
    return render(request, 'wakemeup/contract/edit_contract.html', {'form': form,})

@check_authorization
def addreward(request):

    if request.method == 'POST':

        # Create form instance (bind data to form)
        form = RewardForm(request.POST)

        if form.is_valid():
            myreward = Reward(
                rewardid = form.cleaned_data.get('rewardid'),
                vendor = form.cleaned_data.get('vendor'),
                rewardcategory = form.cleaned_data.get('rewardcategory'),
                rewarddisplayname = form.cleaned_data.get('rewarddisplayname'),
                rewarddescription = form.cleaned_data.get('rewarddescription'),
                rewardvalue = form.cleaned_data.get('rewardvalue'),
            )

            # Save object
            myreward.save()

            return HttpResponse("Premio guardado.")
    else:
        form = RewardForm(cancel_type="button")

    return render(request, 'wakemeup/contract/edit_contract_goals_addreward.html', {'form': form})

@check_authorization
def list_object(request, objecttype):

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

    elif objecttype == 'reward':

        # Look up rewards
        objectSet = RewardsTable(Reward.objects.get_rewards())

    else:
        pass
        
    RequestConfig(request).configure(objectSet)
        
    return render(request, 'wakemeup/admin/index.html', {'objects' : objectSet, 'objecttype': objecttype})

@check_authorization
def edit_object(request, objecttype, objectid):
    
    form_template = 'wakemeup/admin/edit_form.html'
    context = {}

    # Retrieve objects
    if objecttype == 'school':
        objectForm = SchoolForm
        SchoolRewardFormSet = formset_factory(form=SchoolRewardForm, extra=0)
        SchoolCalendarFormSet = formset_factory(form=SchoolCalendarForm, extra=1)
        
    elif objecttype == 'class':
        objectForm = ClassForm

        # Make sure teacher has access to class
        myteacherclass = TeacherClass.objects.get_teacher_classes(teacheruserid=request.user.userid,classid=objectid)
        
        # Teachers can only view their own information
        if not (
            (request.user.usertype == 'TR' and myteacherclass) or
            request.user.is_admin()
        ):
            return redirect_home()

        context.update({
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

    elif objecttype == 'reward':
        objectForm = RewardForm

        # Teachers can only view their own rewards
        if not (
            request.user.is_admin() or
            objectid == 'new' # Used in case of adding a reward
        ):
            return redirect_home()

    else:
        pass

    # Lookup form's base class
    objectClass = objectForm.Meta.model

    # SAVE OBJECT
    if request.method == 'POST' and 'submit_other' not in request.POST: # Ignore submits from other forms

        # Create form instance (bind data to form)
        form = objectForm(request.POST, request.FILES, request=request)

        if form.is_valid():
            
            kwargs = {}
            
            # Create new object
            if(objecttype == 'school'):

                # Capture data use policy file info
#                 originalpolicyfileid = request.POST.get("datausepolicyfileid") # Read in original fileid
#                 
#                 mydatausepolicyfileid = originalpolicyfileid or None
#                 mydatausepolicyfile = request.FILES.get('datausepolicyfile')

                # New file was uploaded
#                 if(mydatausepolicyfile):
# 
#                     # Read in binary data
#                     mydatafile = convert_form_binary_to_db(mydatausepolicyfile)
#                     
#                     # Create new file object
#                     myfile = File(
#                         fileid = None,
#                         filename = get_file_name_info(mydatausepolicyfile.name)['file_name'],
#                         fileextension = get_file_name_info(mydatausepolicyfile.name)['file_extension'],
#                         filesize = mydatausepolicyfile.size,
#                         filetype = mydatausepolicyfile.content_type,
# #                         description = 'File description',
#                         filedata = psycopg2.Binary(mydatafile),
#                     )
#                     
#                     # Save new file and capture fileid
#                     mydatausepolicyfileid = myfile.save()
#                     
#                     # Delete old file (if exists)
#                     if(originalpolicyfileid):
#                         File(fileid=originalpolicyfileid).delete()
                
                # Process guardian approval policy
#                 guardianapprovalpolicy = json.dumps({'requiredfields':form.cleaned_data.get('guardianapprovalpolicy')})
                
                myschool = objectClass(
                    schoolid = form.cleaned_data.get('schoolid'),
                    schooldisplayname = form.cleaned_data.get('schooldisplayname'),
                    schoolabbreviation = form.cleaned_data.get('schoolabbreviation'),
                    address = form.cleaned_data.get('address'),
                    city = form.cleaned_data.get('city'),
                    department = form.cleaned_data.get('department'),
#                     datausepolicyfileid = mydatausepolicyfileid,
#                     guardianapprovalpolicy = guardianapprovalpolicy
                )

                schoolrewardformset = SchoolRewardFormSet(request.POST)
                schoolcalendarformset = SchoolCalendarFormSet(request.POST)

                context.update({ # TO-DO: Not sure if needed?
                    'schoolrewardformset':schoolrewardformset,
                    'schoolcalendarformset':schoolcalendarformset
                })
                
                if(schoolrewardformset.is_valid() and schoolcalendarformset.is_valid()):
                    schoolreward_data = []
                    
                    # Loop through formset
                    for myform in schoolrewardformset:

                        if(myform.cleaned_data.get('selected')):
                            schoolreward_data.append({
                                'rewardid': myform.cleaned_data.get('rewardid'),
                                'rewardvalue': myform.cleaned_data.get('rewardvalue'),
                            })

                    schoolcalendar_data = []
                    
                    # Loop through formset
                    for myform in schoolcalendarformset:

                        if(myform.cleaned_data.get('selected')):
                            schoolcalendar_data.append({
                                'itemdate': str(myform.cleaned_data.get('itemdate')),
                                'itemtype': myform.cleaned_data.get('itemtype'),
                                'itemnotes': myform.cleaned_data.get('itemnotes'),
                            })

                    # Save school info
                    myschool.save(**kwargs)
                    SchoolReward(schoolid=myschool.schoolid).save(rewardinfo=to_json(schoolreward_data))
                    SchoolCalendar(schoolid=myschool.schoolid).save(calendarinfo=to_json(schoolcalendar_data))

            elif(objecttype == 'class'):
                myclass = objectClass(
                    classid = form.cleaned_data.get('classid'),
                    schoolid = form.cleaned_data.get('schoolid'),
                    classdisplayname = form.cleaned_data.get('classdisplayname'),
                    gradelevel = form.cleaned_data.get('gradelevel'),
                )
                
                # Save object
                myclass.save(**kwargs)
                
            elif(objecttype == 'teacher'):

                # Get signature scan file
                mydatafile = convert_form_binary_to_db(request.FILES.get('defaultsignaturescanfile'))

                # Build original class list (values)
                initial_classes = []
                myteacher = objectClass.objects.get(teacheruserid=form.cleaned_data.get('teacheruserid')) # Lookup teacher info

                if(myteacher.classinfo):
                    for myclass in myteacher.classinfo:
                        initial_classes.append(myclass['classid'])

                # Build current class list (dictionaries)
                current_classes_final = []
                current_classes_form = convert_string_array(form.cleaned_data.get('currentclasses'))
                
                for myclass in current_classes_form:
                    current_classes_final.append({'classid':myclass})
                
                # Generate class info field
                classinfo = to_json({
                    'deletedclasses' : subtract_arrays(initial_classes, current_classes_form),
                    'currentclasses' : current_classes_final
                })

                myteacher = objectClass(
                    teacheruserid = form.cleaned_data.get('teacheruserid'),
                    schoolid = form.cleaned_data.get('schoolid'),
                    classinfo = classinfo,
                    firstname = form.cleaned_data.get('firstname'),
                    lastname = form.cleaned_data.get('lastname'),
                    emailaddress = form.cleaned_data.get('emailaddress'),
                    profilepictureid = form.cleaned_data.get('profilepictureid'),
                )

                # Save object
                myteacher.save(**kwargs)
            
            elif(objecttype == 'reward'):
                
                myreward = objectClass(
                    rewardid = form.cleaned_data.get('rewardid'),
                    vendor = form.cleaned_data.get('vendor'),
                    rewardcategory = form.cleaned_data.get('rewardcategory'),
                    rewarddisplayname = form.cleaned_data.get('rewarddisplayname'),
                    rewarddescription = form.cleaned_data.get('rewarddescription'),
                    rewardvalue = form.cleaned_data.get('rewardvalue'),
                )

                # Save object
                myreward.save(**kwargs)

            # Return to main page
            return redirect('wakemeup:list_object', objecttype=objecttype)

    # CREATE NEW OBJECT
    elif(objectid == 'new'):
        kwargs = {}
        
        if(objecttype == 'class'):
            kwargs = {'request':request}
            
        elif(objecttype == 'school'):
            kwargs = {'schoolrewardformset':SchoolRewardFormSet(initial=Reward.objects.get_rewards())}
            kwargs = {'schoolcalendarformset':SchoolCalendarFormSet()}

        form = objectForm(**kwargs)

    # UPDATE EXISTING OBJECT
    else:
        
        # Lookup object
        myobject = objectClass.objects.get(objectid)
        
        # Create form
        if(myobject):
            if(objecttype == 'school'):
                
                form_template = 'wakemeup/admin/edit_school.html'

                form = objectForm(
                    initial = {
                        'schoolid': myobject.schoolid,
                        'schooldisplayname': myobject.schooldisplayname,
                        'schoolabbreviation': myobject.schoolabbreviation,
                        'address': myobject.address,
                        'city': myobject.city,
                        'department': myobject.department,
#                         'datausepolicyfileid':myobject.datausepolicyfileid,
#                         'guardianapprovalpolicy':myobject.guardianapprovalpolicy.get('requiredfields') if myobject.guardianapprovalpolicy else None
                    }
                )

                # Reward formset - Merge available rewards with current school rewards
                rewards = Reward.objects.get_rewards()
                schoolrewards = SchoolReward.objects.get_school_rewards(schoolid=myobject.schoolid)
                schoolreward_data = []
                
                for reward in rewards:
                    
                    # Get corresponding school reward
                    myschoolreward = get_matching_item(schoolrewards,'rewardid',reward.rewardid)
                    
                    schoolreward_data.append(
                        {
                            'selected':True if myschoolreward else False, # Mark as selected if exists corresponding school reward
                            'rewardid':reward.rewardid,
                            'vendor':reward.vendor,
                            'rewardcategorydisplayname':reward.rewardcategorydisplayname,
                            'rewarddisplayname':reward.rewarddisplayname,
                            'rewarddescription':reward.rewarddescription,
                            'rewardvalue': getattr(myschoolreward,'rewardvalue',reward.rewardvalue), # Overwrite with any school-specific values
                        }
                    )

                # Calendar formset
                schoolcalendar = SchoolCalendar.objects.get_school_calendars(schoolid=myobject.schoolid)
                schoolcalendar_data = []
                
                for calendaritem in schoolcalendar:
                    
                    schoolcalendar_data.append(
                        {
                            'selected':True,
                            'itemdate':calendaritem.itemdate,
                            'itemtype':calendaritem.itemtype,
                            'itemdescription':calendaritem.itemdescription,
                            'itemnotes': calendaritem.itemnotes, # Overwrite with any school-specific values
                        }
                    )
                    
                # Populate evaluation formset with initial data
                schoolrewardformset = SchoolRewardFormSet(initial=schoolreward_data)
                schoolcalendarformset = SchoolCalendarFormSet(initial=schoolcalendar_data)

                context.update({
                    'value': myobject.schoolid, # Can possibly remove this one
                    'schoolid': myobject.schoolid,
                    'form': form, 
                    'schoolrewardformset': schoolrewardformset,
                    'schoolcalendarformset': schoolcalendarformset
                })

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
                        'emailaddress': myobject.emailaddress,
                        'profilepictureid': myobject.profilepictureid,
                    }
                )
            
            elif(objecttype == 'reward'):
                form = objectForm(
                    initial = {
                        'rewardid': myobject.rewardid,
                        'vendor': myobject.vendor,
                        'rewardcategory': myobject.rewardcategory,
                        'rewarddisplayname': myobject.rewarddisplayname,
                        'rewarddescription': myobject.rewarddescription,
                        'rewardvalue': myobject.rewardvalue,
                    }
                )
                
        # Handle off-case for invalid object id
        else:
            return redirect_home()
        
    return render(request, form_template, {'form': form, 'objecttype':objecttype, **context})

@check_authorization
def get_contract(request, contractid):
    mycontract = Contract.objects.get(contractid=contractid)

    # Make sure contract exists
    if(mycontract):
        # Check contract is not a draft and user has access
        if(mycontract.contractstatus != 'D' and (request.user.userid in (mycontract.get_users())) or request.user.is_admin): # TO-DO: Check permissions 
            mycontract.contractvalidperiod_disp = display_timestamp_range(mycontract.contractvalidperiod) # Format for display
            classinfo = Class.objects.get(classid=mycontract.classid)
            
            # Prepare context info
            context = {
                'record':mycontract,
                'objecttype':'contract', # Used for contract button links
                'classinfo':classinfo,
                'displayinfo': {
                    'buttonsize':'', # Contract button size
                    'displaytextflag':False # Hide info text
                }
            } 
        
            return render(request, 'wakemeup/contract/detail.html', context)

    # Contract doesn't exist or is a "Draft"
    return redirect_home()
        
@check_authorization
def list_contract(request):
    
    # Determine which contracts to display
    if request.user.is_admin: # TO-DO: Update for permissions check
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

@check_authorization
def create_user(request):
    
    if request.method == 'POST':
        # Go home if user clicks cancel
        if("submit_cancel" in request.POST):
            return redirect_home()
        
        # Bind form
        form = SignupForm(request.POST, request=request)

        if form.is_valid():

            # Store variables to reuse
            username = form.cleaned_data.get('username')
            mypassword = form.cleaned_data.get('password1')

            # Generate password (if not provided)
            if(not mypassword):
                raw_password = get_user_model().objects.make_random_password()
            else:
                raw_password = mypassword

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

            # Format password output string to display on confirmation screen
            if(not myemailaddress or not mypassword):
                conf_password_display = raw_password
            else:
                conf_password_display = None

            # Create new user
            newuser = get_user_model().objects.create_user(
                password = raw_password, 
                schoolid = form.cleaned_data.get('schoolid'),
                username = username,
                usertype = form.cleaned_data.get('usertype'),
                firstname = form.cleaned_data.get('firstname'),
                lastname = form.cleaned_data.get('lastname'),
#                 defaultsignaturescanfile = form.cleaned_data.get('defaultsignaturescanfile'),
                emailaddress = myemailaddress,
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
                             'Algunas notas:\n\n' + \
                             '- el nombre de usuario y la contrase' + mychr('n') + 'a son sensibles a min' + mychr('u') + 'sculos/may' + mychr('u') + 'sculos\n' + \
                             '- para cambiar su contrase' + mychr('n') + 'a, inicie una sesi' + mychr('o') + 'n y haga clic en "Mi Cuenta --> Herramientas"' + '\n' + \
                             '- esta aplicaci' + mychr('o') + 'n se ve mejor usando la ' + mychr('u') + 'ltima versi' + mychr('o') + 'n de Google Chrome con JavaScript activado\n\n' + \
                             'Bienvenidos!' + '\n\n' + \
                             'Duitama Colegio Project'
            )

            # Go back to index page
            return render(request, 'wakemeup/admin/create_user_confirmation.html', {'userinfo':newuser, 'conf_password_display':conf_password_display})
    else:
        # Return empty form
        form = SignupForm(request=request)
        
    return render(request, 'wakemeup/admin/create_user.html', {'form': form})

def reset_password(email, from_email, template='registration/password_reset_email.html'):
    form = PasswordResetForm({'email':email})
    return form.save(from_email=from_email, email_template_name=template)