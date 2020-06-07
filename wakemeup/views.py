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
from lib.UsefulFunctions.httpUtils import *
from lib.UsefulFunctions.miscUtils import get_school_year
from lib.UsefulFunctions.stringUtils import *
from lib.UsefulFunctions.fileUtils import get_file_name_info
from lib.UsefulFunctions.googleUtils import GoogleDrive, GoogleCalendar

from django_tables2 import RequestConfig

import psycopg2

from wakemeup.tables import *
from wakemeup.forms import *
from wakemeup.models.school import *
from wakemeup.models.program import *
from wakemeup.models.environment import *
from user.models.user import UserReputationEvent, UserBadge, UserNotification
from user.models.authorization import *

DEFAULT_SCHOOL_YEAR = get_school_year()

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
            
        elif(view_action in ("edit", "execute")):
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
            if(view_action in ('list','get','edit','create','execute','delete')):
                myobject = Object.objects.get_object_by_name(objectname=kwargs.get('objecttype') or view_object) # business object
            else:
                myobject = Object.objects.get_object_by_name(objectname=viewname) # view

            # Check valid object
            if(myobject):

                # Check user has requested access to object
                if (myuser.check_access(objectid=myobject.objectid, objectclass=myobject.objectclass, requestedaccesslevel=myrequestedaccesslevel)):

                    # Valid permission - continue
                    return view(*args, **kwargs)
        else:
            # Not authenticated - redirect to login page
            return redirect('login')
        
        # Not authorized - redirect to homepage (TO-DO: Create "not authorized" page)
        return redirect_home()

    # Return view
    return view_wrapper

# Get relative root directory for files
def get_rootdir(request, gd_locator, programname='incentive'): # TO-DO: Fix hardcoded
    if request.user.is_admin():
        gd_locator = get_gd_locator('programs_base')
        programname = None
        
    return File.objects.lookup_fileid_gd(gd_locator=gd_locator, programname=programname)

# Check if form is being saved
def check_saveform(request):
    return True if request.method == "POST" and not request.POST.get('source') else False

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

@check_authorization
def execute_admintools(request):

    # Handle link redirect
    if check_saveform(request):
        action = request.POST.get('action')
        
        if action == "drivesync":
            gd = GoogleDrive()
            gd.sync()
            
    return HttpResponse("Success")

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

def redirect_referer(request):
    return redirect(request.META['HTTP_REFERER']) if request.META.get('HTTP_REFERER') else redirect_home()

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

    context = {'request': request}
    
    if request.method == "POST":

        auth = request.user.get_site_auth().myaccount

        # Bind form data
        form = MyAccountForm(request.POST, request.FILES, context=context)

        if(form.is_valid()):
            
            # Create user object
            myuser = get_user_model()(
                userid = form.cleaned_data.get('userid'),
                schoolid = form.cleaned_data.get('schoolid'),
                firstname = form.cleaned_data.get('firstname'),
                lastname = form.cleaned_data.get('lastname'),
                emailaddress = form.cleaned_data.get('emailaddress'),
                profilepictureid = form.cleaned_data.get('profilepictureid'),
                sharedaccountflag = form.cleaned_data.get('sharedaccountflag'),
            )

            # Save user
            if not auth.profile.disable:
                myuser.save_user()

    else:
        myuser = get_user_model().objects.get(userid=request.user.userid)
        
        if(myuser):
            form = MyAccountForm(initial=vars(myuser), context=context)
            
        # Return empty form
        else:
            form = MyAccountForm(context=context)

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

@check_authorization
def get_calendar(request):

    program = Program.objects.get(programname='incentive', schoolyear=DEFAULT_SCHOOL_YEAR, schoolid=request.user.schoolid) # TO-DO: Fix for variables (schoolid, schoolyear, programname)
    events = GoogleCalendar().get_events(calendarid=program.calendarid) if getattr(program, 'calendarid', None) else None
    
    context = {
        'program':program,
        'events':events
    }
    
    return render(request, 'wakemeup/calendar/index.html', context)

@check_authorization
def list_file(request):

    filetype = request.GET.get('filetype')
    filefilter = {}
    
    # Program filters
    if filetype == "interview":
        filecategory = ['IVV','IVT']
    elif filetype == "report":
        filecategory = ['RTY','RT','SVT','SVS']
    elif filetype == "video":
        filecategory = ['VW']
    elif filetype == "form":
        filecategory = ['CTF']
    elif filetype == "letter":
        filecategory = ['LTI','LTT']
    else:
        filecategory = None

    if filecategory:
        filefilter.update({'filecategory': filecategory})

    hierarchyflag = True if not filefilter else False

    fileparams = {
        'filecategory': filecategory,
        'relativeroot': get_rootdir(request=request, gd_locator=get_gd_locator('program_base'), programname='incentive'),
        'objectpermissionsflag': request.user.is_admin(),
        'hierarchyflag': hierarchyflag
        }

#     context = {'files':request.user.get_files(hierarchyflag=True, objectpermissionsflag=request.user.is_admin(), relativeroot=get_rootdir(request=request, gd_locator=get_gd_locator('program_base'), programname='incentive'))}
    context = {'files':request.user.get_files(**fileparams), "filefilter": filefilter, 'iconsize': 36 if not hierarchyflag else None, 'icontileflag': False if not filefilter else True}
    return render(request, 'wakemeup/files/list_file.html', context)

@check_authorization
def edit_file(request, fileid=None):

    fileid = request.POST.get('fileid', None)

    context = {'fileid':fileid}

    # Set correct template
    if(fileid =="bulk" or not fileid):
        form_template = 'wakemeup/files/edit_file_bulk.html'
        context.update({'files':request.user.get_files(hierarchyflag=True, objectpermissionsflag=request.user.is_admin(), relativeroot=get_rootdir(request=request, gd_locator=get_gd_locator('program_base')))})
    else:
        form_template = 'wakemeup/files/edit_file.html'

    # SAVE FILE
    if check_saveform(request):
        
        # Single file
        if fileid != "bulk":
            
            # Bind form data
            form = FileForm(request.POST, request.FILES, context={"request": request})
    
            if(form.is_valid()):
    
                # Connect to Google Drive
                gd = GoogleDrive(permissions=['write'])
                
                # Get program info
                myprogramname = form.cleaned_data.get('programname') or None
                myuserid = form.cleaned_data.get('userid') or None
                myschoolyear = form.cleaned_data.get('schoolyear') or None
                myschoolid = form.cleaned_data.get('schoolid') or None
    
                myfileclass = form.cleaned_data.get('fileclass')
                myfilecategory = form.cleaned_data.get('filecategory')
                myaccessroles = form.cleaned_data.get('accessroles')
                
                filetypes = Category.objects.get_categories(categoryclass='contractfile' if myfileclass == "CT" else "programfile" if myfileclass == "PG" else "")
                
                # Get user upload directory or use default (programname, school year); otherwise GD will default to "root"
                myuserprogram = UserProgram.objects.get(userid=myuserid, programname=myprogramname, schoolyear=myschoolyear, schoolid=myschoolid, uploaddirflag=True) # Create upload dir
                uploaddir = getattr(myuserprogram, 'uploaddirectoryid_gd', None) or \
                            File.objects.lookup_fileid_gd(gd_locator=get_gd_locator('program_uploads_base'), schoolyear=myschoolyear, programname=myprogramname)
    
                # Loop through files
                files = [request.FILES.get('file[%d]' % i)
                     for i in range(0, len(request.FILES))]
    
                for myfile in files:
                    file_metadata = {
                        'name': myfile.name,
                        'originalFilename': myfile.name,
                        'description':'Archivo subido por ' + request.user.userdisplayname,
                        'parents':[uploaddir] if uploaddir else None,
                        'properties':{
                            'userid':myuserid,
                            'uploaduserdisplayname': request.user.userdisplayname,
                            'uploaduserid':request.user.userid,
                            'programname':myprogramname
                        }
                    }
    
                    # Build GD file
                    gd_file = {
                        'gd': gd,
                        'metadata':file_metadata,
                        'filedata':myfile,
                    }
    
                    # Create file in repository
                    newfile = File(
                        fileclass = form.cleaned_data.get('fileclass'),
                        filecategory = myfilecategory,
                        schoolyear = myschoolyear,
                        schoolid = myschoolid,
                        fileURL=form.cleaned_data.get('url'),
                        contractid = form.cleaned_data.get('contractid'),
                        filedescription = form.cleaned_data.get('filedescription')
                    ).save(gd_file=gd_file)
                    
                    # Save ACLs for file
                    RoleACL().save(
                        acllist=[{"roleid":myrole, "aclinfo":[{"objectid":newfile['fileid'], "objectclass":'FL', "accesslevel":4}]} for myrole in myaccessroles]
                    )
                    
        # Bulk files
        else:
            form = FileFormBulk(request.POST, context={'request': request})

            if(form.is_valid()):
                accessroles = form.cleaned_data.pop('accessroles')
                filelist = request.POST.getlist('filelist')
                formdata = form.cleaned_data

                fileinfo = {}
                acllist = []
                
                filelist = convert_string_array(filelist)
                
                # Prepare fileinfo
                for key, value in formdata.items():
                    
                    # Look for "checkbox" fields
                    if(key[-9:] == "_checkbox"):
                        myfield = key[:-9]
                        selected = formdata[key]
                        
                        # Copy selected attribute to new dictionary
                        if selected:
                            try:
                                fileinfo[myfield] = formdata[myfield] if formdata[myfield] else None
                            except:
                                pass

                # Loop through files in file list
                for myrole in accessroles:
                    acllist.append(
                        {
                            "roleid": myrole, 
                            "aclinfo": [{"objectid": myfileid, "objectclass":'FL', "accesslevel":4} for myfileid in filelist]
                        } 
                    )

                # Update file info
                File.objects.update_attributes(fileid=filelist, fileinfo=fileinfo, acllist=acllist)

    # CREATE NEW
    elif fileid == "new":
        form = FileForm(initial=request.POST, context={'request': request}) # Pass any post data (i.e. from links)

    # UPDATE EXISTING FILE
    elif(fileid):
        
        fileid = int(fileid)
        myfile = File.objects.get(fileid=fileid)
        
        # Create form
        if(myfile):
            form = FileForm(initial=vars(myfile), context={'request': request})
                
        # Handle off-case for invalid object id
        else:
            return redirect_home()

    # UPDATE FILES (BULK)
    else:
        form = FileFormBulk(initial=request.POST, context={'request': request})

    return render(request, form_template, {'form': form, **context})

@check_authorization
def get_file(request, fileid):
    
    fileid = int(fileid)
    
    myfile = File.objects.get(fileid)
    myuser = request.user

    forcedownload = True if request.GET.get('forcedownload', 'true').lower() == "true" else False # Force download if not specified
    exporttype = request.GET.get('exporttype', None)

    if myfile:
        
        # Check if user has download access to this file
        hasfileaccess = myuser.check_access(objectid=myfile.fileid, objectclass='FL', requestedaccesslevel=4, objectpermissionsflag=request.user.is_admin())
        
        if hasfileaccess:
            if myfile.filesource == 'GD':
                
                # Regular file
                if not myfile.shortcutdetails:
                    myfileid = myfile.alternatefileid
                    
                # Shortcut - Point to target file
                else:
                    myfileid = myfile.shortcutdetails['targetId']
                
                # Export file - Google Drive
                gd = GoogleDrive()
                mymimetype = get_mimetype(exporttype)
                myfileextension = exporttype if mymimetype else myfile.fileextension
                mycontenttype = mymimetype or myfile.filetype # Handle case of export
                
                myfile.filedata = gd.download_file(fileid=myfileid, mimetype=mymimetype)
                myfile.filename = (myfile.filename or '') + (('.' + myfileextension if myfileextension else ''))

                if not myfile.filesize:
                    myfile.filesize = len(myfile.filedata)

#                 myfileurl = gd.get_file_weblink(fileid=myfile.alternatefileid)
#                 return redirect(myfileurl)

            elif myfile.filesource == 'DB':
                myfile.filename = myfile.filename + myfile.fileextension

            return getFileResponse(filedata=myfile.filedata, filename=myfile.filename, filesize=myfile.filesize, contenttype=mycontenttype, forcedownload=forcedownload)
        
    # File does not exist or user has no access - return to refering page
    return redirect_referer(request)

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
            if(mycontract.teacheruserid == request.user.userid or request.user.is_admin()): # TO-DO: Update to check permissions

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

            return HttpResponse("Incentivo guardado.")
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
                
                # Validate calendar form
                calendarform = SchoolCalendarForm(request.POST)

                if calendarform.is_valid():
                    myschool = objectClass(
                        schoolid = form.cleaned_data.get('schoolid'),
                        schooldisplayname = form.cleaned_data.get('schooldisplayname'),
                        schoolabbreviation = form.cleaned_data.get('schoolabbreviation'),
                        address = form.cleaned_data.get('address'),
                        city = form.cleaned_data.get('city'),
                        department = form.cleaned_data.get('department'),
                    )
    
                    # Extract program info
                    myprogram = Program.objects.get(programname='incentive', schoolyear=DEFAULT_SCHOOL_YEAR, schoolid=form.cleaned_data.get('schoolid')) # TO-DO: Fix hard-coded programname
    
                    if myprogram:
                        if not myprogram.programdetails:
                            myprogram.programdetails = {} 
                            
                        myprogram.programdetails.setdefault('google', {}).setdefault('calendar', {})['id'] = calendarform.cleaned_data.get('calendarid') 
    
                    schoolrewardformset = SchoolRewardFormSet(request.POST)
    
                    context.update({ # TO-DO: Not sure if needed?
                        'schoolrewardformset':schoolrewardformset,
                        'schoolcalendarform':calendarform
                    })
                    
                    if schoolrewardformset.is_valid():
                        schoolreward_data = []
                        
                        # Loop through formset
                        for myform in schoolrewardformset:
    
                            if(myform.cleaned_data.get('selected')):
                                schoolreward_data.append({
                                    'rewardid': myform.cleaned_data.get('rewardid'),
                                    'rewardvalue': myform.cleaned_data.get('rewardvalue'),
                                })
    
                        # Save school info
                        myschool.save(**kwargs)
                        myprogram.save()
                        SchoolReward(schoolid=myschool.schoolid).save(rewardinfo=to_json(schoolreward_data))

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
            kwargs = {
                'schoolrewardformset':SchoolRewardFormSet(initial=Reward.objects.get_rewards()),
            }

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
                    }
                )

                calendarform = SchoolCalendarForm(initial={'calendarid': Program.objects.get(programname='incentive', schoolyear=DEFAULT_SCHOOL_YEAR, schoolid=myobject.schoolid).calendarid}) # TO-DO: Fix hard-coded programname

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

                # Populate evaluation formset with initial data
                schoolrewardformset = SchoolRewardFormSet(initial=schoolreward_data)

                context.update({
                    'value': myobject.schoolid, # Can possibly remove this one
                    'schoolid': myobject.schoolid,
                    'form': form, 
                    'schoolrewardformset': schoolrewardformset,
                    'calendarform': calendarform
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
def edit_permissions(request):
    
    # Placeholder
    return redirect_home()

@check_authorization
def get_contract(request, contractid):
    mycontract = Contract.objects.get(contractid=contractid)

    # Make sure contract exists
    if(mycontract):
        # Check contract is not a draft and user has access
        if(mycontract.contractstatus != 'D' and (request.user.userid in (mycontract.get_users())) or request.user.is_admin()): # TO-DO: Check permissions 
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
    if request.user.is_admin(): # TO-DO: Update for permissions check
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
            myschoolid = form.cleaned_data.get('schoolid')
            myprogramname = form.cleaned_data.get('programname')
            myschoolyear = form.cleaned_data.get('schoolyear')

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
                schoolid = myschoolid,
                username = username,
                usertype = form.cleaned_data.get('usertype'),
                firstname = form.cleaned_data.get('firstname'),
                lastname = form.cleaned_data.get('lastname'),
#                 defaultsignaturescanfile = form.cleaned_data.get('defaultsignaturescanfile'),
                emailaddress = myemailaddress,
                sharedaccountflag = form.cleaned_data.get('sharedaccountflag')
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

            if(myschoolid and myprogramname and myschoolyear):
                
                # Register user for programs
                for year in myschoolyear:
                    UserProgram(userid=newuser.userid, programname=myprogramname, schoolid=myschoolid, schoolyear=year).save()
                    
                    # Add user to roles
                    for myschool in (0, myschoolid):
                        Role(
                            roleid=Program.objects.get(programname=myprogramname, schoolid=myschoolid, schoolyear=year).defaultroleid
                        ).modify_role_item(userid=newuser.userid)
                
            # Go back to index page
            return render(request, 'wakemeup/admin/create_user_confirmation.html', {'userinfo':newuser, 'conf_password_display':conf_password_display})
    else:
        # Return empty form
        form = SignupForm(request=request)
        
    return render(request, 'wakemeup/admin/create_user.html', {'form': form})

def reset_password(email, from_email, template='registration/password_reset_email.html'):
    form = PasswordResetForm({'email':email})
    return form.save(from_email=from_email, email_template_name=template)