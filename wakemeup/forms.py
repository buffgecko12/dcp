from django.urls import reverse
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import get_user_model

from crispy_forms.helper import FormHelper
from crispy_forms.layout import *
from crispy_forms.bootstrap import FormActions
from django.forms.widgets import HiddenInput

DEFAULT_FORM_CLASS = 'form-horizontal'
DEFAULT_LABEL_CLASS = 'col-sm-3'
DEFAULT_FIELD_CLASS = 'col-sm-9'
DEFAULT_FORM_METHOD = 'POST'

def setFormHelper(
    myFormHelper, 
    form_method = DEFAULT_FORM_METHOD, # Use defaults if no values are specified
    form_class = DEFAULT_FORM_CLASS, 
    label_class = DEFAULT_LABEL_CLASS, 
    field_class = DEFAULT_FIELD_CLASS
):
    myFormHelper.form_method = form_method

    # Set CSS properties
    myFormHelper.form_class = form_class
    myFormHelper.label_class = label_class
    myFormHelper.field_class = field_class
    
class LoginForm(AuthenticationForm):

    # Define form fields
    username = forms.CharField(label="Nombre de usuario", required=True)
    password = forms.CharField(label="Contrase&#241;a", required=True, widget=forms.PasswordInput)

    # Define constructor
    def __init__ (self, *args, **kwargs):
        # Call base class constructor (i.e. AuthenticationForm)
        super(LoginForm, self).__init__(*args, **kwargs)

        # Set helper properties
        self.helper = FormHelper() 
        setFormHelper(self.helper)
        
        # Set form layout
        self.helper.layout = Layout(
            Fieldset(
                'Iniciar sesi&#243;n',
                'username',
                'password'
            ),
            FormActions(
                Submit('login', 'Iniciar', css_class='btn-primary'),
#                 HTML('<br><br><p><a href="#">&#191;Olvidaste tu contrase&#241;a?</a></p>')
            ),
            Hidden('next',reverse('wakemeup:index'))
        )

class SignupForm(UserCreationForm):
    
    # Define form fields
    username = forms.CharField(label='Nombre de usuario (o correo)', max_length=50)
    firstname = forms.CharField(label='Primer nombre', max_length=100)
    lastname = forms.CharField(label='Apellido', max_length=100)
    usertype = forms.ChoiceField(label='Tipo de usuario',choices=get_user_model().usertype_choices)
    emailaddress = forms.EmailField(label='Correo', max_length=250, required=False)
    userrole = forms.CharField(initial='U', widget=HiddenInput) # Default new users to "User" role

    # Define constructor
    def __init__(self, *args, **kwargs):
        # Call base class constructor (i.e. SignupForm)
        super(SignupForm, self).__init__(*args, **kwargs)
        
        # Set helper properties
        self.helper = FormHelper()
        self.helper.form_method = DEFAULT_FORM_METHOD

        self.helper.layout = Layout(
            Fieldset(
                'Crear usuario',
                'username',
                'usertype',
                'firstname',
                'lastname',
                'emailaddress',
                'password1',
                'password2',
                'userrole'
            ),
            FormActions(
                Submit('login', 'Crear', css_class='btn-primary')
            )
        )

    # Specify model and which fields to include in form
    class Meta:
        model = get_user_model()
        fields = ('username','usertype','firstname','lastname','emailaddress','password1','password2','userrole')

    # Make sure email address does not already exist
    def clean_emailaddress(self):
        # Get the email
        emailaddress = self.cleaned_data.get('emailaddress')

        # Check to see if any users already exist with this email as a username.
        match = get_user_model().objects.get_user_auth(emailaddress=emailaddress)
        
        # Unable to find a user, this is fine
        if not match:
            return emailaddress

        # A user was found with this as a username, raise an error.
        raise forms.ValidationError('Este correo ya esta en uso.')

class SchoolForm(forms.Form):

    # Define form fields
    schoolid = forms.IntegerField(
        label='Codigo de colegio', 
        required=False, 
        widget=forms.HiddenInput()
    )
    schooldisplayname = forms.CharField(
        label='Nombre para mostrar',
        max_length=100
    )
    address = forms.CharField(
        label='Direcci' + chr(243) + 'n',
        max_length=100
    )
    city = forms.CharField(
        label='Ciudad',
        max_length=100
    )
    department = forms.CharField(
        label='Departamento',
        max_length=100
    )

    # Define constructor
    def __init__ (self, *args, **kwargs):

        # Call base class constructor (i.e. School Form)
        super(SchoolForm, self).__init__(*args, **kwargs)
        
        # Set form helper properties
        self.helper = FormHelper()
        setFormHelper(self.helper)
        
        # Set form layout
        self.helper.layout = Layout(
            Fieldset(
                'Crear colegio',
                'schoolid',
                'schooldisplayname',
                'address',
                'city',
                'department',
            ),
            FormActions(
                Submit('crear','Crear'),
                Reset('reset','Borrar')
            )
        )