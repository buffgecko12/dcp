from django import forms
from django.contrib.auth.forms import AuthenticationForm

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, ButtonHolder, Submit

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
    

