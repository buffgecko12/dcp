from django.shortcuts import render
from django.contrib.auth import get_user_model

from .forms import SignupForm, SchoolForm, ClassForm, TeacherForm, StudentForm
from .models.environment import School, Class, Teacher, Student

from django_tables2 import RequestConfig
from .tables import SchoolsTable, ClassesTable, TeachersTable, StudentsTable

from django.views.generic import DeleteView

from lib.UsefulFunctions.imgUtils import renderImageFromDb
from django.http import HttpResponse

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

def delete_object(request, objecttype, objectid):
    if(request.method == 'POST'):
        
        if(objecttype == 'school'):
            myobject = School.objects.get(objectid)
            
        elif(objecttype == 'class'):
            myobject = Class.objects.get(objectid)
        
        elif(objecttype == 'teacher'):
            myobject = Class.objects.get(objectid)
        
        elif(objecttype == 'student'):
            myobject = Class.objects.get(objectid)
        
        if(myobject):
            myobject.delete()

    return admin_list(request, objecttype)

def index(request):
    return render(request, 'wakemeup/index.html')

def create_contract(request):
    return render(request, 'wakemeup/create_contract.html')

# Admin
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

    # If POST request, process form data
    if request.method == 'POST':
        
        # Create form instance (bind data to form)
        form = objectForm(request.POST)
        
        if form.is_valid():
            # Create new object
            if(objecttype == 'school'):
                myobject = objectClass(
                    schoolid = form.cleaned_data['schoolid'],
                    schooldisplayname = form.cleaned_data['schooldisplayname'],
                    address = form.cleaned_data['address'],
                    city = form.cleaned_data['city'],
                    department = form.cleaned_data['department'],
                )

            elif(objecttype == 'class'):
                myobject = objectClass(
                    classid = form.cleaned_data['classid'],
                    schoolid = form.cleaned_data['schoolid'],
                    classdisplayname = form.cleaned_data['classdisplayname'],
                )
                
                students = form.cleaned_data['students']

                # Assign students to class
                if(students):
                    for mystudent in students:
                        newstudent = Student(mystudent,myobject.classid)
                        newstudent.save()
            
            elif(objecttype == 'teacher'):
                pass
            
            elif(objecttype == 'student'):
                pass

            # Save object
            myobject.save()

            # Return to main page
            return admin_list(request, objecttype)

    # Create blank form for new object
    elif(objectid == 'new'):
        form = objectForm()

    else:
        # Lookup object
        myobject = objectClass.objects.get(objectid)
        
        # Create new form
        if(myobject):
            if(objecttype == 'school'):
                form = objectForm(
                    initial = {
                        'schoolid': myobject.schoolid,
                        'schooldisplayname': myobject.schooldisplayname,
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
                pass
            
            elif(objecttype == 'student'):
                pass
                
        # Handle off-case for invalid object id
        else:
            form = objectForm()
        
    return render(request, 'wakemeup/admin/add_form.html', {'form': form})

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
        
    return render(request, 'wakemeup/admin/add_form.html', {'form': form})