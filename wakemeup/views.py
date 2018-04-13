from django.shortcuts import render

from .forms import SchoolForm
from .models.environment import School

def index(request):
    return render(request, 'wakemeup/index.html')

def create_contract(request):
    return render(request, 'wakemeup/create_contract.html')

# User
def login(request):
    return render(request, 'login.html')

# Admin
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
        
    return render(request, 'wakemeup/admin/editschool.html', {'form': form})

def edit_class(request):
    pass

def edit_teacher(request):
    pass

def edit_student(request):
    pass