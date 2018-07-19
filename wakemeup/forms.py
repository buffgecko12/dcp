from django.urls import reverse
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import get_user_model

from crispy_forms.helper import FormHelper
from crispy_forms.layout import *
from crispy_forms.bootstrap import FormActions, TabHolder, Tab, PrependedText
from django.forms.widgets import HiddenInput

from .models.environment import School, Class, Teacher, TeacherBudget, Student
from .models.contract import Contract, ContractGoal, ContractInfo, Reward

from django.contrib.postgres.forms import RangeWidget

import datetime

from lib.UsefulFunctions.stringUtils import *

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
    
def getAdminFormActions(objecttype):
    return FormActions(
        Submit('submit_cancel','Cancelar', css_class='btn btn-secondary', css_id='cancel'), # Don't change the "cancel" id, it's used by javascript (i.e. reward modal)
        Submit('submit_next','Siguiente', css_id='next'),
    )
    
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
                HTML("<br><br><p><a href=""{% url 'password_reset' %}"">&#191;Olvid&#243; su contrase&#241;a?</a></p>")
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
                'Crear/editar usuario',
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
                Submit('login', 'Enviar', css_class='btn-primary')
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
        emailmatch = get_user_model().objects.get_user_auth(emailaddress=emailaddress)
        usernamematch = get_user_model().objects.get_user_auth(username=emailaddress)
        
        # If email is already in use, raise an error
        if emailmatch or usernamematch:
            raise forms.ValidationError('Este correo ya esta en uso.')

        return emailaddress

    # Make sure email address does not already exist
    def clean_username(self):
        # Get the email
        username = self.cleaned_data.get('username')

        # Check to see if any users already exist with this e-mail / username
        usernamematch = get_user_model().objects.get_user_auth(username=username)
        emailmatch = get_user_model().objects.get_user_auth(emailaddress=username)

        # If username is already in use, raise an error
        if usernamematch or emailmatch:
            raise forms.ValidationError('Este nombre de usuario / correo ya esta en uso.')
        
        return username

class SchoolForm(forms.Form):

    # Define form fields
    schoolid = forms.IntegerField(label='Codigo de colegio', required=False, widget=forms.HiddenInput())
    schooldisplayname = forms.CharField(label='Nombre para mostrar',max_length=100)
    schoolabbreviation = forms.CharField(label='Abreviatura', required=False, max_length=25)
    address = forms.CharField(label='Direcci' + mychr('o') + 'n',max_length=100)
    city = forms.CharField(label='Ciudad',max_length=100)
    department = forms.CharField(label='Departamento',max_length=100)

    # Define constructor
    def __init__ (self, *args, **kwargs):

        # Call base class constructor (i.e. School Form)
        super(SchoolForm, self).__init__(*args, **kwargs)
        
        # Set form helper properties
        self.helper = FormHelper()
        setFormHelper(self.helper)
        self.helper.form_tag = False
        
        # Set form layout
        self.helper.layout = Layout(
            Fieldset(
                'Crear/editar colegio',
                'schoolid',
                'schooldisplayname',
                'schoolabbreviation',
                'address',
                'city',
                'department',
            ),
            getAdminFormActions('school'),
        )

    # Specify model
    class Meta:
        model = School

class ClassForm(forms.Form):

    # Define form fields
    classid = forms.IntegerField(
        label='Codigo de curso', 
        required=False, 
        widget=forms.HiddenInput()
    )

    # Drop-down (populate choices in constructor)
    schoolid = forms.ChoiceField(
        label='Colegio', 
    )

    classdisplayname = forms.CharField(
        label='Nombre para mostrar',
        max_length=100
    )
    
    # Add multiple select field for list of students in class
    students = forms.MultipleChoiceField(
        label='Estudiantes no asignados',
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    # Define constructor
    def __init__ (self, *args, **kwargs):

        # Call base class constructor (i.e. School Form)
        super(ClassForm, self).__init__(*args, **kwargs)
        
        # Get dynamic fields
        self.fields['schoolid'].choices = School.objects.school_choices()
        self.fields['students'].choices = Student.objects.student_choices(classid=0)
        
        # Set form helper properties
        self.helper = FormHelper()
        setFormHelper(self.helper)
        self.helper.form_tag = False
        
        # Set form layout
        self.helper.layout = Layout(
            Fieldset(
                'Crear/editar curso',
                'classid',
                'schoolid',
                'classdisplayname',
                'students',
            ),
            getAdminFormActions('class')
        )

    # Specify model
    class Meta:
        model = Class
        exclude = ('schooldisplayname')

class TeacherForm(forms.Form):

    # Define form fields
    teacheruserid= forms.IntegerField(
        label='Codigo de docente', 
        required=False, 
        widget=forms.HiddenInput()
    )

    # Drop-down (populate choices in constructor)
    schoolid = forms.ChoiceField(label='Colegio')

    # Add multiple select field for list of students in class
    currentclasses = forms.MultipleChoiceField(
        label='Cursos',
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    firstname = forms.CharField(max_length=100,label='Primer nombre')
    lastname = forms.CharField(max_length=100,label='Apellido(s)')
    phonenumber = forms.CharField(max_length=25,label='Tel' + mychr('e') + 'fono', required=False)    
    emailaddress = forms.CharField(max_length=250,label='Correo', required=False)
    defaultsignaturescanfile = forms.FileField(label='Firma', required=False)
        
    # Define constructor
    def __init__ (self, *args, **kwargs):

        # Call base class constructor (i.e. Teacher Form)
        super(TeacherForm, self).__init__(*args, **kwargs)
        
        # Update field attributes
        self.fields['schoolid'].choices = School.objects.school_choices()
        self.fields['currentclasses'].choices = Class.objects.class_choices(schoolid = None) # TO-DO: Fix this to look up values based on schoolid form field

        # Set form helper properties
        self.helper = FormHelper()
        setFormHelper(self.helper)
        self.helper.form_tag = False
        
        # Set form layout
        self.helper.layout = Layout(
            Fieldset(
                'Editar docente',
                'teacheruserid',
                'schoolid',
                'currentclasses',
                'firstname',
                'lastname',
                'emailaddress',
                'phonenumber',
                'defaultsignaturescanfile',
            ),
            getAdminFormActions('teacher')
        )
    
    # Specify model
    class Meta:
        model = Teacher
        exclude = ('reputationvalue','schooldisplayname')

class StudentForm(forms.Form):

    # Define form fields
    studentuserid = forms.IntegerField(widget=forms.HiddenInput)

    # Drop-down (populate choices in constructor)
    schoolid = forms.ChoiceField(label='Colegio')
    classid = forms.ChoiceField(label='Curso')

    firstname = forms.CharField(max_length=100,label='Primer nombre')
    lastname = forms.CharField(max_length=100,label='Apellido(s)')
    phonenumber = forms.CharField(max_length=25,label='Tel' + mychr('e') + 'fono', required=False)    
    emailaddress = forms.CharField(max_length=250,label='Correo', required=False)
    defaultsignaturescanfile = forms.FileField(label='Firma', required=False)

    def __init__ (self, *args, **kwargs):

        # Call base class constructor (i.e. Teacher Form)
        super(StudentForm, self).__init__(*args, **kwargs)
        
        # Update field attributes
        self.fields['schoolid'].choices = School.objects.school_choices()
        self.fields['classid'].choices = Class.objects.class_choices(schoolid = None) # TO-DO: Update to include correct schoolid value

        # Set form helper properties
        self.helper = FormHelper()
        setFormHelper(self.helper)
        self.helper.form_tag = False
        
        # Set form layout
        self.helper.layout = Layout(
            Fieldset(
                'Editar estudiante',
                'studentuserid',
                'schoolid',
                'classid',
                'firstname',
                'lastname',
                'emailaddress',
                'phonenumber',
                'defaultsignaturescanfile',
            ),
            getAdminFormActions('student')
        )

    # Specify model
    class Meta:
        model = Student
        fields = ('studentuserid','schoolid','classid','firstname','lastname','phonenumber','emailaddress')

class RewardForm(forms.Form):

    # Define form fields
    rewardid = forms.IntegerField(widget=forms.HiddenInput,required=False)

    rewarddisplayname = forms.CharField(max_length=100,label='Premio')
    rewarddescription = forms.CharField(max_length=500,label='Descripci' + mychr('o') + 'n', widget=forms.Textarea(attrs={'rows':4}))
    rewardvalue = forms.IntegerField(label='Valor')

    def __init__ (self, *args, **kwargs):

        # Call base class constructor (i.e. Teacher Form)
        super(RewardForm, self).__init__(*args, **kwargs)
        
        # Set form helper properties
        self.helper = FormHelper()
        setFormHelper(self.helper)
        self.helper.form_tag = False
        
        # Set form layout
        self.helper.layout = Layout(
            Fieldset(
                'Editar premio',
                'rewardid',
                'rewarddisplayname',
                'rewarddescription',
                PrependedText('rewardvalue', '$'),
            ),
            getAdminFormActions('reward')
        )

    # Specify model
    class Meta:
        model = Reward
        fields = ('rewardid','rewarddisplayname','rewarddescription','rewardvalue')

class ContractForm(forms.Form):

    contractid = forms.IntegerField(widget=forms.HiddenInput, required=False)
    teacheruserid = forms.CharField(label='Docente', widget=forms.Select)
    classid = forms.CharField(label='Curso', widget=forms.Select)
    contracttype = forms.CharField(max_length=1,label='Tipo de contrato',widget=forms.HiddenInput, required=False)
    partyuserinfo = forms.CharField(label='Participantes', widget=forms.SelectMultiple)
    contractvalidperiod = forms.CharField(label='Plazo', widget=forms.TextInput(attrs={'class':'daterangeinputfieldempty'}))
    revisiondeadlinets = forms.DateField(label='Fecha tope para revisar', widget=forms.DateInput(attrs={'class':'dateinputfield'}))
    contractstatus = forms.CharField(max_length=1,label='Estatus', widget=forms.HiddenInput, required=False)

    # Fields used for javascript and form navigation between pages
    initialbudget = forms.IntegerField(widget=forms.HiddenInput, required=False)
    maxrewardvalue = forms.IntegerField(widget=forms.HiddenInput, required=False)

    def clean_contractvalidperiod(self):
        contractvalidperiod = self.cleaned_data.get("contractvalidperiod")
        contractvalidperiod_array = contractvalidperiod.split(" - ")
        
        try:
            startdate = datetime.datetime.strptime(contractvalidperiod_array[0],'%d/%m/%Y')
            enddate = datetime.datetime.strptime(contractvalidperiod_array[1],'%d/%m/%Y')
        except ValueError:
            raise forms.ValidationError("Formato invalido.  Por favor utilizar este formato: DD/MM/YYYY - DD/MM/YYYY")
    
        if(startdate > enddate):
            raise forms.ValidationError("La fecha de inico debe ser antes de la fecha de termino.")
    
        return contractvalidperiod_array

    def __init__ (self, *args, **kwargs):

        # Extract request argument
        request = kwargs.pop("request")
        contractid = kwargs.pop("contractid")

        # Call base class constructor (i.e. Teacher Form)
        super(ContractForm, self).__init__(*args, **kwargs)
        
        if(contractid != "new"):
            mycontractinfo = ContractInfo.objects.get(contractid)
            mybudget = TeacherBudget.objects.get(mycontractinfo.teacheruserid).availablebudget
            mymaxrewardvalue = mycontractinfo.maxrewardvalue
        else:
            mymaxrewardvalue = 0
            myteacherbudget = TeacherBudget.objects.get(teacheruserid = request.user.userid)

            # Lookup default budget for teacher
            if(myteacherbudget):
                mybudget = myteacherbudget.availablebudget
            else:
                mybudget = 0

        # Set form helper properties
        self.helper = FormHelper()
        setFormHelper(self.helper)
        self.helper.form_tag = False # Disable auto-generation of <form> tags
        self.fields['initialbudget'].initial = mybudget # TO-DO: Fix this!!
        self.fields['maxrewardvalue'].initial = mymaxrewardvalue # Get number of participants (used to calculate budget)
        
        # Set form layout
        self.helper.layout = Layout(
            'contractid',
            'contractstatus',
            'contracttype',
            'initialbudget',
            'maxrewardvalue',
            Fieldset(
                'Participantes',
                'teacheruserid',
                'classid',
                'partyuserinfo',
            ),
            Fieldset(
                'Fechas',
                'contractvalidperiod',
                'revisiondeadlinets',
            ),
            FormActions(
                Submit('submit_cancel','Cancelar', css_class='btn btn-secondary', css_id='submit_cancel'),
                Submit('submit_next','Siguiente', css_id='submit_next'),
                Div(
                    HTML('<span id="id_availablebudget"></span>'), 
                    css_class='float-right'
                )
            )
        )

    class Meta:
        model = Contract
        fields = ('contractid','teacheruserid','classid','partyuserinfo','contractvalidperiod','revisiondeadlinets','contractstatus','contracttype')

class ContractPartyAcceptForm(forms.Form):

    contractid = forms.IntegerField(widget=forms.HiddenInput)
    partyuserid = forms.IntegerField(widget=forms.HiddenInput)
    preferredgoalid = forms.IntegerField(widget=forms.HiddenInput)
    partyapprovalsignature = forms.FileField(label='Firma', required=False) # Approval signature scan file

    def __init__ (self, *args, **kwargs):

        # Call base class constructor (i.e. Teacher Form)
        super(ContractPartyAcceptForm, self).__init__(*args, **kwargs)
        
        # Set form helper properties
        self.helper = FormHelper()
        setFormHelper(self.helper)
        
        # Set form layout
        self.helper.layout = Layout(
            'contractid',
            'preferredgoalid',
            'partyuserid',
            'partyapprovalsignature',
            FormActions(
                Submit('submit_cancel','Cancelar', css_class='btn btn-secondary', css_id='submit_cancel'),
                Submit('submit_next','Enviar', css_id='submit_next'),
            )
        )

    class Meta:
        model = Contract
        fields = ('contractid','preferredgoalid','partyuserid','partyapprovalsignature')

# Main contract goal form
class ContractGoalsForm(forms.Form):

    def clean(self):
        
        # Call parent form's validation
        cleaned_data = super(ContractGoalsForm, self).clean()

        # Check for partially specified goals
        if (cleaned_data.get("e_goaldescription") and not cleaned_data.get("e_rewardinfo")) or \
           (cleaned_data.get("e_rewardinfo") and not cleaned_data.get("e_goaldescription")):
            self.add_error('e_goaldescription', "Por favor verificar la meta f" + mychr('a') + "cil")

        if (cleaned_data.get("m_goaldescription") and not cleaned_data.get("m_rewardinfo")) or \
           (cleaned_data.get("m_rewardinfo") and not cleaned_data.get("m_goaldescription")):
            self.add_error('m_goaldescription', "Por favor verificar la meta media")

        if (cleaned_data.get("d_goaldescription") and not cleaned_data.get("d_rewardinfo")) or \
           (cleaned_data.get("d_rewardinfo") and not cleaned_data.get("d_goaldescription")):
            self.add_error('d_goaldescription', "Por favor verificar la meta dific" + mychr('i') + "l")

        # Verify that at least one goal has been filled out correctly
        if not(cleaned_data.get("e_goaldescription") and cleaned_data.get("e_rewardinfo")) and \
           not(cleaned_data.get("m_goaldescription") and cleaned_data.get("m_rewardinfo")) and \
           not(cleaned_data.get("d_goaldescription") and cleaned_data.get("d_rewardinfo")):
            
            raise forms.ValidationError("Por favor especificar al menos una meta.")

    goaldescription_label = 'Descripci' + mychr('o') + 'n<br><small><i>Una descripci' + mychr('o') + 'n detallada con instrucciones claras para c' + chr(243) + 'mo medir ' + chr(233) + 'xito</i></small>'
    rewardinfo_label = 'Opciones de premio<small><i> <button type="button" class="btn btn-primary btn-sm" data-toggle="modal" data-target="#addRewardModal">A' + chr(241) + 'adir</button><br>Al cumplir con ' + chr(233) + 'xito la meta, cada participante podr' + chr(225) + ' escoger un premio de esta lista</i></small>'

    # Fields used for javascript and form navigation between pages
    contractid = forms.IntegerField(widget=forms.HiddenInput, required=False)    
    initialbudget = forms.IntegerField(widget=forms.HiddenInput, required=False)
    numparticipants = forms.IntegerField(widget=forms.HiddenInput, required=False)

    e_goalid = forms.IntegerField(widget=forms.HiddenInput, required=False)
    e_goaldescription = forms.CharField(max_length=500,label=goaldescription_label, widget=forms.Textarea(attrs={'rows':4}), required=False)
    e_rewardinfo = forms.CharField(label=rewardinfo_label, widget=forms.SelectMultiple, required=False)

    m_goalid = forms.IntegerField(widget=forms.HiddenInput, required=False)
    m_goaldescription = forms.CharField(max_length=500,label=goaldescription_label, widget=forms.Textarea(attrs={'rows':4}), required=False)
    m_rewardinfo = forms.CharField(label=rewardinfo_label, widget=forms.SelectMultiple, required=False)

    d_goalid = forms.IntegerField(widget=forms.HiddenInput, required=False)
    d_goaldescription = forms.CharField(max_length=500,label=goaldescription_label, widget=forms.Textarea(attrs={'rows':4}), required=False)
    d_rewardinfo = forms.CharField(label=rewardinfo_label, widget=forms.SelectMultiple, required=False)

    def __init__ (self, *args, **kwargs):

        # Extract contractid
        contractid = kwargs.pop("contractid")
        
        # Call base class constructor (i.e. Teacher Form)
        super(ContractGoalsForm, self).__init__(*args, **kwargs)
        mycontractinfo = ContractInfo.objects.get(contractid)
        
        # Set form helper properties
        self.helper = FormHelper()
        setFormHelper(self.helper)
        self.helper.form_tag = False # Disable auto-generation of <form> tags
        self.fields['initialbudget'].initial = TeacherBudget.objects.get(mycontractinfo.teacheruserid).availablebudget
        self.fields['numparticipants'].initial = mycontractinfo.numparticipants # Get number of participants (used to calculate budget)
        
        # Set form layout
        self.helper.layout = Layout(
            'contractid',
            'initialbudget',
            'numparticipants',
            TabHolder(
                Tab(
                    'F' + mychr('a') + 'cil',
                    'e_goalid',
                    'e_goaldescription',
                    'e_rewardinfo',
                ),
                Tab(
                    'Media',
                    'm_goalid',
                    'm_goaldescription',
                    'm_rewardinfo',
                ),
                Tab(
                    'Dif' + mychr('i') + 'cil',
                    'd_goalid',
                    'd_goaldescription',
                    'd_rewardinfo',
                )
            ),
            FormActions(
                Submit('submit_cancel','Cancelar', css_class='btn btn-secondary', css_id='submit_cancel'),
                Submit('submit_next','Siguiente', css_id='submit_next'),
                Submit('submit_previous','Previo', css_class='btn btn-info', css_id='submit_previous'),
                Div(
                    HTML('<span id="id_availablebudget"></span>'), 
                    css_class='float-right'
                )
            )
        )

class ContractSubmitForm(forms.Form):
    
    contractid = forms.IntegerField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):
        
        contractid = kwargs.pop("contractid")
        
        #Call base class constructor
        super(ContractSubmitForm, self).__init__(*args, **kwargs)
        
        # Set form helper properties
        self.helper = FormHelper()
        setFormHelper(self.helper)
        
        # Set form layout
        self.helper.layout = Layout(
            'contractid',
            FormActions(
                Submit('submit_cancel','Cancelar',css_class='btn btn-secondary'),
                Submit('submit_next','Enviar'),
                Submit('submit_previous','Previo',css_class='btn btn-info'),
            )
        )
