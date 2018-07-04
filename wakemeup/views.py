from django.shortcuts import render
from django.contrib.auth import get_user_model

from .forms import SignupForm, SchoolForm, ClassForm, TeacherForm, StudentForm, ContractForm
from .models.environment import School, Class, Teacher, Student
from .models.contract import Contract, ContractParty

from django_tables2 import RequestConfig
from .tables import SchoolsTable, ClassesTable, TeachersTable, StudentsTable

from lib.UsefulFunctions.imgUtils import renderImageFromDb
from lib.UsefulFunctions.dateUtils import format_timestamp_range
from lib.UsefulFunctions.dataUtils import convert_array_string_to_int
from django.http import HttpResponse

import psycopg2
import json

from django.shortcuts import redirect

view_permissions = {
    'admin_list': {
        'school':{'userrole':['S','A'], 'usertype':[]},
        'class':{'userrole':['S','A'], 'usertype':[]},
        'teacher':{'userrole':['S','A'], 'usertype':['TR']},
        'student':{'userrole':['S','A'], 'usertype':['ST']},
    },
    'delete_object': {
        'school': {'userrole':['S','A'], 'usertype':[]},
        'class': {'userrole':['S','A'], 'usertype':[]},
        'teacher': {'userrole':['S','A'], 'usertype':[]},
        'student': {'userrole':['S','A'], 'usertype':[]},
    },
    'edit_object': {
        'school':{'userrole':['S','A'], 'usertype':[]},
        'class':{'userrole':['S','A'], 'usertype':[]},
        'teacher':{'userrole':['S','A'], 'usertype':['TR']},
        'student':{'userrole':['S','A'], 'usertype':['ST']},
    },
    'create_contract': {
        'all': {'userrole':['S','A'], 'usertype':['TR']},
    },
    'add_user': {
        'all': {'userrole':['S'], 'usertype':[]},
    },
}

def check_permissions(view):
    viewname = view.__name__
    
    def view_wrapper(*args, **kwargs):

        # Set objecttype
        if('objecttype' in kwargs):
            objecttype = kwargs['objecttype']
        else:
            objecttype = 'all'

        myuser = args[0].user

        # Check user permissions
        if myuser.is_authenticated:
            if (
                myuser.userrole in view_permissions[viewname][objecttype]['userrole'] or 
                myuser.usertype in view_permissions[viewname][objecttype]['usertype']
            ):
                # Valid permission - continue
                return view(*args, **kwargs)

        # Invalid permission - redirect to homepage
        return redirect('wakemeup:index')
    
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
    
    return render(request, 'wakemeup/admin/teacher_dropdown_list_options.html', {'teachers': teachers, 'teacheruserid':teacheruserid})

def load_classes(request):
    contractid = request.GET.get('contractid') # Check for existing contract
    teacheruserid = request.GET.get('teacheruserid') # Check selected teacher

    classid = None

    # If existing contract, use existing data
    if(contractid):
        mycontract = Contract.objects.get(contractid=contractid)
        classid = mycontract.classid
        teacheruserid = mycontract.teacheruserid

        classes = Class.objects.get_classes(classid=classid, schoolid=None, teacheruserid = teacheruserid)
        
    # Lookup teacher classes
    elif teacheruserid:
        classes = Class.objects.get_classes(classid=classid, schoolid=None, teacheruserid = teacheruserid)
    else:
        classes = []

    return render(request, 'wakemeup/admin/class_dropdown_list_options.html', {'classes': classes, 'classid': classid})

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

    return render(request, 'wakemeup/admin/student_dropdown_list_options.html', {'students': students})

def convert_string_array(mystring):
    result = []

    try:
        myarray_string = mystring.split(',') # Try to split string into an array
    except:
        myarray_string = list(map(int, mystring)) # Convert string array into into array
    
    for myvalue in myarray_string:
        try:
            myvalue = int(myvalue) # Check if value is integer
            result.append(myvalue) # Add value to new array
        except:
            pass # Don't append value

    return result

def subtract_arrays(original, current):
    result = []
        
    original_items = convert_string_array(original)
    current_items = convert_string_array(current)
    result = [myitem for myitem in original_items if myitem not in current_items]

    return result

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

@check_permissions
def delete_object(request, objecttype, objectid):

    if(request.method == 'POST'):
        
        if(objecttype == 'school'):
            myobject = School.objects.get(objectid)
            
        elif(objecttype == 'class'):
            myobject = Class.objects.get(objectid)
        
        elif(objecttype == 'teacher'):
            myobject = Teacher.objects.get(objectid)
        
        elif(objecttype == 'student'):
            myobject = Student.objects.get(objectid)
        
        if(myobject):
            myobject.delete()

    return admin_list(request, objecttype = objecttype)

def index(request):
    return render(request, 'wakemeup/index.html')

@check_permissions
def create_contract(request, contractid):
    # PROCESS FORM
    if request.method == "POST":
        # Create form instance (bind data to form)
        form = ContractForm(request.POST, request=request)

        if(form.is_valid()):

            mycontract = Contract(
                contractid = form.cleaned_data.get('contractid'),
                teacheruserid = form.cleaned_data.get('teacheruserid'),
                classid = form.cleaned_data.get('classid'),
                contracttype = form.cleaned_data.get('contracttype'),
                contractvalidperiod = format_timestamp_range(form.cleaned_data.get('contractvalidperiod'),'%d/%m/%Y'),
                revisiondeadlinets = form.cleaned_data.get('revisiondeadlinets'),
                contractstatus = form.cleaned_data.get('contractstatus'),
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
            return redirect('wakemeup:index')
#             return admin_list(request, objecttype = objecttype)   
     
    # CREATE FORM (NEW OBJECT)
    elif(contractid == 'new'):
        form = ContractForm(request=request, initial={'contractstatus':'D'})
        
    # CREATE FORM (EXISTING OBJECT)
    else:
        # Lookup object
        mycontract = Contract.objects.get(contractid=contractid)

        # Create form
        if(mycontract):
            
            # Format valid period
            contractvalidperiod = str(mycontract.contractvalidperiod.lower.strftime("%d/%m/%Y")) + ' - ' + \
                                  str(mycontract.contractvalidperiod.upper.strftime("%d/%m/%Y"))
            
            form = ContractForm(request=request,
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
                
        # Handle off-case for invalid object id
        else:
            form = ContractForm(request=request)
        
    return render(request, 'wakemeup/edit_contract.html', {'form': form})

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
        objectSet = TeachersTable(Teacher.objects.all())
    elif objecttype == 'student':
        objectSet = StudentsTable(Student.objects.all())
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
    elif objecttype == 'student':
        objectForm = StudentForm
    else:
        pass

    # Lookup form's base class
    objectClass = objectForm.Meta.model

    # PROCESS FORM
    if request.method == 'POST':
        
        # Create form instance (bind data to form)
        form = objectForm(request.POST, request.FILES)
        
        if form.is_valid():
            
            # Read signature scan file
            if(request.FILES.get('defaultsignaturescanfile')):
                myfile = request.FILES.get('defaultsignaturescanfile')
                mydatafile = myfile.read()
            else:
                mydatafile = None
            
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
                
                # Read signature scan file
                if(request.FILES.get('defaultsignaturescanfile')):
                    myfile = request.FILES.get('defaultsignaturescanfile')
                    mydatafile = myfile.read()
                else:
                    mydatafile = None
                
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

            # Save object
            myobject.save()

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
                
        # Handle off-case for invalid object id
        else:
            form = objectForm()
        
    return render(request, 'wakemeup/admin/edit_form.html', {'form': form})

@check_permissions
def add_user(request):
    
    if request.method == 'POST':
        form = SignupForm(request.POST)

        if form.is_valid():

            # Store variables to reuse
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')

            # Create new user
            get_user_model().objects.create_user(
                raw_password, 
                username,
                form.cleaned_data.get('usertype'),
                form.cleaned_data.get('firstname'),
                form.cleaned_data.get('lastname'),
                form.cleaned_data.get('defaultsignaturescanfile'),
                form.cleaned_data.get('phonenumber'),
                form.cleaned_data.get('emailaddress'),
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