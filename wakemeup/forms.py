from django.urls import reverse
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import get_user_model

from crispy_forms.helper import FormHelper
from crispy_forms.layout import *
from crispy_forms.bootstrap import FormActions, TabHolder, Tab, PrependedText, InlineRadios, InlineCheckboxes
from django.forms.widgets import HiddenInput

from .models.environment import School, Class, Teacher, TeacherBudget, Student
from .models.contract import Contract, ContractInfo, Reward, ContractParty

import datetime

from users.models import UserBadge

from lib.UsefulFunctions.stringUtils import *

DEFAULT_FORM_CLASS = 'form-horizontal'
DEFAULT_LABEL_CLASS = 'col-sm-3'
DEFAULT_FIELD_CLASS = 'col-sm-9'
DEFAULT_FORM_METHOD = 'POST'

def validate_emailaddress(userid, emailaddress):
    
    # Try to lookup user with matching email address
    try:
        useremail = get_user_model().objects.get(userid=userid).emailaddress
    except get_user_model().DoesNotExist:
        useremail = None

    # Ignore validation if e-mail address is unchanged or current user does not have e-mail specified (i.e. new user)
    if(useremail == emailaddress or not useremail):
       return emailaddress
    else:

        # Check to see if any users already exist with this email as a username
        emailmatch = get_user_model().objects.get_user_auth(emailaddress=emailaddress)
        usernamematch = get_user_model().objects.get_user_auth(username=emailaddress)
        
        # If email is already in use, raise an error
        if emailmatch or usernamematch:
            raise forms.ValidationError('Este correo ya esta en uso.')
    
        return emailaddress

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
    
def getAdminFormActions(cancel_url = 'wakemeup:index', cancel_context="", cancel_type="link"):
    return FormActions(
        # Cancel button (don't change the "cancel" id; used by javascript)
        Submit('submit_cancel','Cancelar', css_class='btn btn-secondary', css_id='cancel') if cancel_type == "button" else
        HTML("""<a class="btn btn-secondary" href="{% url '""" + cancel_url + """' """ + cancel_context + """ %}">Cancelar</a> """),

        # Submit button
        Submit('submit_next','Enviar', css_id='next'),
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
        setFormHelper(self.helper, label_class = 'col-sm-4', field_class = 'col-sm-8')
        
        # Set form layout
        self.helper.layout = Layout(
            Fieldset(
                'Iniciar sesi&#243;n',
                Field('username',css_class='w-75'),
                Field('password',css_class='w-75'),
            ),
            FormActions(
                Submit('login', 'Iniciar', css_class='btn-primary'),
                HTML("<br><br><p><a href=""{% url 'password_reset' %}"">&#191;Olvid&#243; su contrase&#241;a?</a></p>")
            ),
            Hidden('next',reverse('wakemeup:index'))
        )

class SignupForm(UserCreationForm):

    # Hidden teacheruserid
    teacheruserid = forms.IntegerField(required=False, widget=forms.HiddenInput(), initial=0) # value 0 = no teacher

    # Define form fields
    username = forms.CharField(label='Nombre de usuario (o correo)', max_length=50)
    firstname = forms.CharField(label='Primer nombre', max_length=100)
    lastname = forms.CharField(label='Apellido', max_length=100)
    usertype = forms.ChoiceField(label='Tipo de usuario',choices=get_user_model().usertype_choices)
    schoolid = forms.ChoiceField(label='Colegio', widget=forms.Select, required=False)
    classid = forms.CharField(label='Curso', widget=forms.Select, required=False)
    emailaddress = forms.EmailField(label='Correo', max_length=250, required=False)
    userrole = forms.CharField(initial='U', widget=HiddenInput) # Default new users to "User" role

    # Define constructor
    def __init__(self, *args, **kwargs):
        
        # Extract "request" parameter
        request = kwargs.pop('request')
        
        # Call base class constructor (i.e. SignupForm)
        super(SignupForm, self).__init__(*args, **kwargs)

        # Teachers can only add students
        if(request.user.usertype == "TR"):
            myschoolid = request.user.schoolid # Can only add students to their own school
            
            self.fields['teacheruserid'].initial = request.user.userid
            self.fields['usertype'].choices = [("ST","Estudiante")]
            self.fields['usertype'].initial = "ST"
            self.fields['usertype'].disabled = True
            self.fields['classid'].required=True
            
            self.fields['schoolid'].initial = myschoolid
            self.fields['schoolid'].disabled = True
        else:
            myschoolid = None
            
        self.fields['schoolid'].choices = [("0","-- Escoger colegio --")] + School.objects.school_choices(schoolid=myschoolid)
            
        # Set helper properties
        self.helper = FormHelper()
        self.helper.form_method = DEFAULT_FORM_METHOD

        self.helper.layout = Layout(
            Fieldset(
                'Crear/editar usuario',
                'teacheruserid',
                'username',
                'usertype',
                'schoolid',
                'classid',
                'firstname',
                'lastname',
                'emailaddress',
                'password1',
                'password2',
                'userrole'
            ),
            getAdminFormActions()
        )

    # Specify model and which fields to include in form
    class Meta:
        model = get_user_model()
        fields = ('teacheruserid','username','usertype','schoolid','classid','firstname','lastname','emailaddress','password1','password2','userrole')

    # Make sure email address does not already exist
    def clean_emailaddress(self):
        return validate_emailaddress(self.cleaned_data.get("userid"), self.cleaned_data.get("emailaddress"))

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

    # Store original data use policy fileid
    datausepolicyfileid = forms.IntegerField(required=False, widget=forms.HiddenInput())

    # Define form fields
    schoolid = forms.IntegerField(label='Codigo de colegio', required=False, widget=forms.HiddenInput())
    schooldisplayname = forms.CharField(label='Nombre para mostrar',max_length=100)
    schoolabbreviation = forms.CharField(label='Abreviatura', required=False, max_length=25)
    address = forms.CharField(label='Direcci' + mychr('o') + 'n',max_length=100)
    city = forms.CharField(label='Ciudad',max_length=100)
    department = forms.CharField(label='Departamento',max_length=100)
    
    datausepolicyfile = forms.FileField(label='Politica de uso de datos', required=False)

    # Guardian approval policy
    guardianapprovalpolicy = forms.MultipleChoiceField(
        required=False, 
        label='Politica de aprobaci' + mychr('o') + 'n de tutor',
        choices = [
            ("idfullname","Nombre de tutor"),
            ("idnumber","Numero de cedula"),
            ("idissuelocation","Lugar de expedici" + mychr('o') + "n"),
            ("idissuedate","Fecha de expedici" + mychr('o') + "n")
        ]
    )

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
                'datausepolicyfileid',
                'schoolid',
                'schooldisplayname',
                'schoolabbreviation',
                'address',
                'city',
                'department',
                'datausepolicyfile',
                InlineCheckboxes('guardianapprovalpolicy'),
            ),
            getAdminFormActions(cancel_url = 'wakemeup:admin_list', cancel_context='objecttype="school"')
        )

    def clean_guardianapprovalpolicy(self):
        return self.cleaned_data.get('guardianapprovalpolicy')

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
            getAdminFormActions(cancel_url = 'wakemeup:admin_list', cancel_context='objecttype="class"')
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
#    phonenumber = forms.CharField(max_length=25,label='Tel' + mychr('e') + 'fono', required=False)
    emailaddress = forms.EmailField(label='Correo', max_length=250, required=False)
#     defaultsignaturescanfile = forms.FileField(label='Firma', required=False)
#     profilepictureid = forms.IntegerField(label='Avatar', required=False)

    # Make sure email address does not already exist
    def clean_emailaddress(self):
        return validate_emailaddress(self.cleaned_data.get("teacheruserid"), self.cleaned_data.get("emailaddress"))
        
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
 #               'phonenumber',
#                 'profilepictureid',
                'defaultsignaturescanfile',
            ),
            getAdminFormActions(cancel_url = 'wakemeup:admin_list', cancel_context='objecttype="teacher"')
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
#    phonenumber = forms.CharField(max_length=25,label='Tel' + mychr('e') + 'fono', required=False)    
    emailaddress = forms.EmailField(label='Correo', max_length=250, required=False)
    defaultsignaturescanfile = forms.FileField(label='Firma', required=False)
#     profilepictureid = forms.IntegerField(label='Avatar', required=False)

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
#                'phonenumber',
#                 'profilepictureid',
                'defaultsignaturescanfile',
            ),
            getAdminFormActions(cancel_url = 'wakemeup:admin_list', cancel_context='objecttype="student"')
        )

    # Make sure email address does not already exist
    def clean_emailaddress(self):
        return validate_emailaddress(self.cleaned_data.get("studentuserid"), self.cleaned_data.get("emailaddress"))

    # Specify model
    class Meta:
        model = Student
        fields = ('studentuserid','schoolid','classid','firstname','lastname','emailaddress')

# TO-DO: Combine this with TeacherForm & StudentForm
class MyUserForm(forms.Form):

    # Define form fields
    username = forms.CharField(label="Nombre de usuario", max_length=50)
    userid = forms.IntegerField(widget=forms.HiddenInput)
    schoolid = forms.ChoiceField(label='Colegio')

    firstname = forms.CharField(max_length=100,label='Primer nombre')
    lastname = forms.CharField(max_length=100,label='Apellido(s)')
#    phonenumber = forms.CharField(max_length=25,label='Tel' + mychr('e') + 'fono', required=False)    
    emailaddress = forms.EmailField(label='Correo', max_length=250, required=False)
#     defaultsignaturescanfile = forms.FileField(label='Firma', required=False)
    profilepictureid = forms.IntegerField(label='Avatar', required=False)

    def __init__ (self, *args, **kwargs):

        # Extract request info
        request = kwargs.pop("request")

        # Call base class constructor (i.e. Teacher Form)
        super(MyUserForm, self).__init__(*args, **kwargs)

        # Set form helper properties
        self.helper = FormHelper()
        setFormHelper(self.helper)
        self.helper.form_tag = False

        # Display username, but don't allow edits
        self.fields['username'].initial=request.user.username
        self.fields['username'].disabled=True

        # Teachers can only add students
        if(not request.user.is_admin()):
            myschoolid = request.user.schoolid # Can only add students to their own school
            self.fields['schoolid'].initial = myschoolid
            self.fields['schoolid'].disabled = True
            self.fields['schoolid'].widget=forms.HiddenInput()
            
            # Disable additional fields for students
            if(request.user.usertype == "ST"):
                self.fields['firstname'].initial = request.user.firstname
                self.fields['firstname'].disabled = True
                
                self.fields['lastname'].initial = request.user.lastname
                self.fields['lastname'].disabled = True
        else:
            myschoolid = None
            
        self.fields['schoolid'].choices = [("0",'-- Escoger colegio --')] + School.objects.school_choices(schoolid=myschoolid)
        self.fields['profilepictureid'].choices=get_user_model().objects.get_profile_picture_choices(userid=request.user.userid)
        
        # Set form layout
        self.helper.layout = Layout(
            'userid',
            'username',
            'schoolid',
            'firstname',
            'lastname',
            'emailaddress',
#            'phonenumber',
#             'defaultsignaturescanfile',
            InlineRadios('profilepictureid', template = 'wakemeup/admin/profilepicture.html'),
            getAdminFormActions()
        )

    # Make sure email address does not already exist
    def clean_emailaddress(self):
        return validate_emailaddress(self.cleaned_data.get("userid"), self.cleaned_data.get("emailaddress"))

    # Specify model
    class Meta:
        model = get_user_model()
        fields = ('userid','username','schoolid','firstname','lastname','emailaddress','profilepictureid')

class RewardForm(forms.Form):

    # Define form fields
    rewardid = forms.IntegerField(widget=forms.HiddenInput,required=False)

    rewarddisplayname = forms.CharField(max_length=100,label='Premio')
    rewarddescription = forms.CharField(max_length=500,label='Descripci' + mychr('o') + 'n', widget=forms.Textarea(attrs={'rows':4}))
    rewardvalue = forms.IntegerField(label='Valor')

    def __init__ (self, *args, **kwargs):

        cancel_type = kwargs.pop('cancel_type', None)

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
            getAdminFormActions(cancel_url = 'wakemeup:admin_list', cancel_context='objecttype="reward"', cancel_type=cancel_type)
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
    contractvalidperiod = forms.CharField(label='Plazo', widget=forms.TextInput(attrs={'class':'daterangeinputfieldempty','placeholder':'MM/DD/YYYY - MM/DD/YYYY'}))
    revisiondeadlinets = forms.DateField(label='Fecha tope para revisar', widget=forms.DateInput(attrs={'class':'dateinputfield','placeholder':'MM/DD/YYYY'}))
    contractstatus = forms.CharField(max_length=1,label='Estatus', widget=forms.HiddenInput, required=False)

    # Fields used for javascript and form navigation between pages
    initialbudget = forms.IntegerField(widget=forms.HiddenInput, required=False)
    initialcontractvalue = forms.IntegerField(widget=forms.HiddenInput, required=False)

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
        revisionflag = kwargs.pop("revisionflag", None)

        # Call base class constructor (i.e. Teacher Form)
        super(ContractForm, self).__init__(*args, **kwargs)
        
        if(contractid != "new"):
            mycontractinfo = ContractInfo.objects.get(contractid)
            mybudget = TeacherBudget.objects.get(mycontractinfo.teacheruserid).availablebudget
            myinitialcontractvalue = mycontractinfo.contractvalue
        else:
            mycontractinfo = None
            myteacherbudget = TeacherBudget.objects.get(teacheruserid = request.user.userid)
            myinitialcontractvalue = 0

            # Lookup default budget for teacher
            if(myteacherbudget):
                mybudget = myteacherbudget.availablebudget
            else:
                mybudget = 0

        # Set form helper properties
        self.helper = FormHelper()
        setFormHelper(self.helper)
        self.helper.form_tag = False # Disable auto-generation of <form> tags
        self.fields['initialbudget'].initial = mybudget
        self.fields['initialcontractvalue'].initial = myinitialcontractvalue or 0
        
        # Disable fields when in revision mode
        if(revisionflag):
            self.fields['revisiondeadlinets'].widget.attrs['readonly'] = True
            self.fields['classid'].widget.attrs['readonly'] = True
            self.fields['teacheruserid'].widget.attrs['readonly'] = True
            self.fields['revisiondeadlinets'].widget.attrs['class'] = '' # Reset CSS class so datepicker doesn't open
        
        # Set form layout
        self.helper.layout = Layout(
            'contractid',
            'contractstatus',
            'contracttype',
            'initialcontractvalue',
            'initialbudget',
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
                HTML("""<a class="btn btn-secondary" id="submit_cancel" href="{% url 'wakemeup:index' %}">Cancelar</a> """),
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
#     partyapprovalsignature = forms.FileField(label='Firma', required=False) # Approval signature scan file

    def __init__ (self, *args, **kwargs):

        request = kwargs.pop('request')
        contractid = kwargs.pop('contractid')

        # Call base class constructor (i.e. Teacher Form)
        super(ContractPartyAcceptForm, self).__init__(*args, **kwargs)

        # Set form helper properties
        self.helper = FormHelper()
        setFormHelper(self.helper, label_class = 'col-sm-5', field_class = 'col-sm-7')

        # Set form layout
        self.helper.layout = Layout(
            HTML('<legend>Acuerdo</legend><hr class="separator">'),
            'contractid',
            'preferredgoalid',
            'partyuserid',
        )
        
        # Get additional fields per school's guardian approval policy
        myclass = Class.objects.get(classid=Contract.objects.get(contractid=contractid).classid)

        if(myclass):
            myschool = School.objects.get(schoolid=myclass.schoolid)
            
            if(myschool.guardianapprovalpolicy):
                approvalfields = myschool.guardianapprovalpolicy.get('requiredfields')
                
                if(approvalfields):
                    myfieldset = Fieldset('Aprobaci' + mychr('o') + 'n de tutor')
                    
                    # Create fields
                    for field in approvalfields:
                        if(field == "idfullname"):
                            self.fields['idfullname'] = forms.CharField(max_length=250, label='Nombre de tutor', widget=forms.TextInput())
                        elif(field == "idnumber"):
                            self.fields['idnumber'] = forms.IntegerField(label='No. de cedula', widget=forms.TextInput())
                        elif(field == "idissuelocation"):
                            self.fields['idissuelocation'] = forms.CharField(max_length=250, label='Lugar de expedici' + mychr('o') + 'n')
                        elif(field == "idissuedate"):
                            self.fields['idissuedate'] = forms.CharField(
                                label='Fecha de expedici' + mychr('o') + 'n', 
                                widget=forms.DateInput(attrs={'class':'dateinputfield','placeholder':'DD/MM/YYYY'})
                            )

                        # Add field to fieldset
                        myfieldset.append(field)
    
                    # Add fieldset to layout
                    self.helper.layout.append(myfieldset)
                    self.helper.layout.append(HTML('<hr class="separator">'))

        # Add admin buttons
        self.helper.layout.append(
            HTML('Yo, {{user.firstname }} {{ user.lastname }}, acepto los terminos del contrato como escrito.  Una vez enviada, mi elecci&#243;n no se puede cambiar.<br><br>')
        )
        self.helper.layout.append(getAdminFormActions(cancel_type="button"))
        
    class Meta:
        model = Contract
        fields = ('contractid','preferredgoalid','partyuserid')

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
    rewardinfo_label = 'Opciones de premio<small><i> <br>Al cumplir con ' + chr(233) + 'xito la meta, cada participante podr' + chr(225) + ' escoger un premio de esta lista</i></small>'
    maxnumreward_label = 'Max. n' + mychr('u') + 'mero de premios<small><i> <br><b>Opcional:</b> El m' + mychr('a') + 'ximo n'  + mychr('u') + 'mero de premios disponible para lograr esta meta (vac&#237;o = sin l' + mychr('i') + 'mite m' + mychr('a') + 'ximo)</i></small>'

    # Fields used for javascript and form navigation between pages
    contractid = forms.IntegerField(widget=forms.HiddenInput, required=False)    
    initialbudget = forms.IntegerField(widget=forms.HiddenInput, required=False)
    numparticipants = forms.IntegerField(widget=forms.HiddenInput, required=False)
    initialcontractvalue = forms.IntegerField(widget=forms.HiddenInput, required=False)

    e_acceptedflag = forms.BooleanField(widget=forms.HiddenInput, required=False)
    m_acceptedflag = forms.BooleanField(widget=forms.HiddenInput, required=False)
    d_acceptedflag = forms.BooleanField(widget=forms.HiddenInput, required=False)

    e_goalid = forms.IntegerField(widget=forms.HiddenInput, required=False)
    e_goaldescription = forms.CharField(max_length=500,label=goaldescription_label, widget=forms.Textarea(attrs={'rows':4}), required=False)
    e_rewardinfo = forms.CharField(label=rewardinfo_label, widget=forms.SelectMultiple, required=False)
    e_maxnumrewards = forms.IntegerField(label=maxnumreward_label, required=False)

    m_goalid = forms.IntegerField(widget=forms.HiddenInput, required=False)
    m_goaldescription = forms.CharField(max_length=500,label=goaldescription_label, widget=forms.Textarea(attrs={'rows':4}), required=False)
    m_rewardinfo = forms.CharField(label=rewardinfo_label, widget=forms.SelectMultiple, required=False)
    m_maxnumrewards = forms.IntegerField(label=maxnumreward_label, required=False)

    d_goalid = forms.IntegerField(widget=forms.HiddenInput, required=False)
    d_goaldescription = forms.CharField(max_length=500,label=goaldescription_label, widget=forms.Textarea(attrs={'rows':4}), required=False)
    d_rewardinfo = forms.CharField(label=rewardinfo_label, widget=forms.SelectMultiple, required=False)
    d_maxnumrewards = forms.IntegerField(label=maxnumreward_label, required=False)

    def clean_e_maxnumrewards(self):
        mynumrewards = int(self.cleaned_data.get('e_maxnumrewards') or 0)
        mycontractpartycount = self.cleaned_data.get('numparticipants')
        
        if not (mynumrewards > mycontractpartycount):
            return self.cleaned_data.get('e_maxnumrewards')
        else:
            raise forms.ValidationError('El n' + mychr('u') + 'mero de premios (' + str(mynumrewards) + ') no puede superar el n' + mychr('u') + 'mero de participantes (' + str(mycontractpartycount) + ')')

    def clean_m_maxnumrewards(self):
        mynumrewards = int(self.cleaned_data.get('m_maxnumrewards') or 0)
        mycontractpartycount = self.cleaned_data.get('numparticipants')
        
        if not (mynumrewards > mycontractpartycount):
            return self.cleaned_data.get('m_maxnumrewards')
        else:
            raise forms.ValidationError('El n' + mychr('u') + 'mero de premios (' + str(mynumrewards) + ') no puede superar el n' + mychr('u') + 'mero de participantes (' + str(mycontractpartycount) + ')')

    def clean_d_maxnumrewards(self):
        mynumrewards = int(self.cleaned_data.get('d_maxnumrewards') or 0)
        mycontractpartycount = self.cleaned_data.get('numparticipants')
        
        if not (mynumrewards > mycontractpartycount):
            return self.cleaned_data.get('d_maxnumrewards')
        else:
            raise forms.ValidationError('El n' + mychr('u') + 'mero de premios (' + str(mynumrewards) + ') no puede superar el n' + mychr('u') + 'mero de participantes (' + str(mycontractpartycount) + ')')

    def __init__ (self, *args, **kwargs):

        # Extract contractid
        contractid = kwargs.pop("contractid")
        revisionflag = kwargs.pop("revisionflag", None)
        
        # Call base class constructor (i.e. Teacher Form)
        super(ContractGoalsForm, self).__init__(*args, **kwargs)
        mycontractinfo = ContractInfo.objects.get(contractid)
        
        # Set form helper properties
        self.helper = FormHelper()
        setFormHelper(self.helper)
        self.helper.form_tag = False # Disable auto-generation of <form> tags
        self.fields['initialbudget'].initial = TeacherBudget.objects.get(mycontractinfo.teacheruserid).availablebudget
        self.fields['numparticipants'].initial = mycontractinfo.numparticipants # Get number of participants (used to calculate budget)
        self.fields['initialcontractvalue'].initial = mycontractinfo.contractvalue or 0 # Get number of participants (used to calculate budget)

        # Get and set max number of rewards
        mycontractpartycount = mycontractinfo.numparticipants
        maxnumrewardswidget = forms.TextInput(attrs={'min':0,'max': mycontractpartycount,'type': 'number'})

        self.fields['e_maxnumrewards'].widget=maxnumrewardswidget
        self.fields['m_maxnumrewards'].widget=maxnumrewardswidget
        self.fields['d_maxnumrewards'].widget=maxnumrewardswidget

            
        # Set form layout
        self.helper.layout = Layout(
            'contractid',
            'initialbudget',
            'initialcontractvalue',
            'numparticipants',
            TabHolder(
                Tab(
                    'F' + mychr('a') + 'cil',
                    'e_acceptedflag',
                    'e_goalid',
                    'e_goaldescription',
                    'e_rewardinfo',
                    Field('e_maxnumrewards', css_class='w-25'),
                ),
                Tab(
                    'Media',
                    'm_acceptedflag',
                    'm_goalid',
                    'm_goaldescription',
                    'm_rewardinfo',
                    Field('m_maxnumrewards', css_class='w-25'),
                ),
                Tab(
                    'Dif' + mychr('i') + 'cil',
                    'd_acceptedflag',
                    'd_goalid',
                    'd_goaldescription',
                    'd_rewardinfo',
                    Field('d_maxnumrewards', css_class='w-25'),
                )
            ),
            FormActions(
                HTML("""<a class="btn btn-secondary" id="submit_cancel" href="{% url 'wakemeup:index' %}">Cancelar</a> """),
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
        revisionflag = kwargs.pop("revisionflag", None)
        
        #Call base class constructor
        super(ContractSubmitForm, self).__init__(*args, **kwargs)

        # Set form helper properties
        self.helper = FormHelper()
        setFormHelper(self.helper)

        # Set form layout
        self.helper.layout = Layout(
            'contractid',
        )

        # Add revision field (if required)
        if(revisionflag):
            self.fields['revisiondescription'] = forms.CharField(
                label='<i>Descripci' + mychr('o') + 'n de los cambios al contrato original</i>', 
                max_length=500, 
                widget=forms.Textarea(attrs={"rows":"5","cols":"20"}),
                required=False
            )
            
            self.helper.layout.append('revisiondescription')

        myformactions = FormActions(
                HTML("""<a class="btn btn-secondary" href="{% url 'wakemeup:index' %}">Cancelar</a> """),
                Submit('submit_next','Enviar'),
#                 Submit('submit_previous','Previo',css_class='btn btn-info'),
                HTML("""<a class="btn btn-info" href="{% url '""" + 'wakemeup:create_contract_goals' + """' """ + 'contractid=' + str(contractid) + """ %}">Previo</a> """),
            )

        # Add discard button for revisions
        if(revisionflag):
            myformactions.append(
                Submit('submit_discard','Descartar', css_class='btn btn-danger')
            )

        # Add form action buttons
        self.helper.layout.append(myformactions)