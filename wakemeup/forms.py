from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import get_user_model

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from django.forms.widgets import HiddenInput

class LoginForm(AuthenticationForm):
    def __init__ (self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        
    username = forms.CharField(label="Username", required=True)
    password = forms.CharField(
        label="Password", required=True, widget=forms.PasswordInput
    )

    helper = FormHelper()
    helper.form_method = 'POST'
    helper.form_tag = False # Prevent <form> tags from being generated
    helper.add_input(Submit('login', 'login', css_class='btn-primary'))

class SignupForm(UserCreationForm):
    username = forms.CharField(label=' Username (or e-mail)', max_length=50)
    firstname = forms.CharField(label='First name', max_length=100)
    lastname = forms.CharField(label='Last name', max_length=100)
    usertype = forms.ChoiceField(label='User type',choices=get_user_model().usertype_choices)
    emailaddress = forms.EmailField(label='Email address', max_length=250, required=False)
    userrole = forms.CharField(initial='U', widget=HiddenInput) # Default new users to "User" role

    helper = FormHelper()
    helper.form_method = 'POST'
#     helper.form_tag = False # Prevent <form> tags from being generated
    helper.add_input(Submit('login', 'Add', css_class='btn-primary'))

    class Meta:
        model = get_user_model()
        fields = ('username','usertype','firstname','lastname','emailaddress','password1','password2')

class SchoolForm(forms.Form):

    schoolid = forms.IntegerField(
        label='School Id', 
        required=False, 
        widget=forms.HiddenInput()
    )
    schooldisplayname = forms.CharField(
        label='Display name',
        max_length=100
    )
    address = forms.CharField(
        label='Address',
        max_length=100
    )
    city = forms.CharField(
        label='City',
        max_length=100
    )
    department = forms.CharField(
        label='Department',
        max_length=100
    )
    

