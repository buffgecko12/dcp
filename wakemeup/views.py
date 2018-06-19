from django.shortcuts import render
from django.contrib.auth import get_user_model

from .forms import SchoolForm, SignupForm
from .models.environment import School

def index(request):
    return render(request, 'wakemeup/index.html')

def create_contract(request):
    return render(request, 'wakemeup/create_contract.html')

# Admin
def admin_list(request, list_type):
    print(list_type)
    return index(request)

def edit_school(request):

    # If POST request, process form data
    if request.method == 'POST':
        
        # Create form instance (bind data to form)
        form = SchoolForm(request.POST)
        
        if form.is_valid():
            # Create new school object
            myschool = School(
                None, 
                form.cleaned_data['schooldisplayname'],
                form.cleaned_data['address'],
                form.cleaned_data['city'],
                form.cleaned_data['department']
            )

            # Save school
            myschool.save()

            # Redirect to new URL

    # Otherwise, create blank form
    else:
        form = SchoolForm()
        
    return render(request, 'wakemeup/admin/add_form.html', {'form': form})

def edit_class(request):
    pass

def edit_teacher(request):
    pass

def edit_student(request):
    pass

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