from django.urls import reverse
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import get_user_model
from django.forms.widgets import HiddenInput

from crispy_forms.helper import FormHelper
from crispy_forms.layout import *
from crispy_forms.bootstrap import FormActions, TabHolder, Tab, PrependedText, InlineRadios, InlineCheckboxes

from wakemeup.models.school import *
from wakemeup.models.program import *
from wakemeup.models.environment import *
from user.models.authorization import Role

from lib.UsefulFunctions.miscUtils import *

import datetime
from lib.UsefulFunctions.stringUtils import *

DEFAULT_SCHOOL_YEAR = get_school_year()

DEFAULT_FORM_CLASS = 'form-horizontal'
DEFAULT_LABEL_CLASS = 'col-sm-4'
DEFAULT_FIELD_CLASS = 'col-sm-8'
DEFAULT_FORM_METHOD = 'POST'

class ChoiceFieldNoValidation(forms.ChoiceField):
    def validate(self, value):
        pass

def validate_emailaddress(userid, emailaddress):
    
    # Try to lookup user with matching email address
    try:
        myuser = get_user_model().objects.get(userid=userid)
        useremail = myuser.emailaddress
        username = myuser.username
        
    except get_user_model().DoesNotExist:
        useremail = None
        username = None

    # Ignore validation if e-mail address is unchanged or the same as the username
    if(userid and (useremail == emailaddress or username == emailaddress)):
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
        HTML("""<a class="btn btn-secondary disable-link" href="{% url '""" + cancel_url + """' """ + cancel_context + """ %}">Cancelar</a> """),

        # Submit button
        Submit('submit_next','Enviar', css_id='next'),
    )
    
def set_dropdown_choices(form, fieldname, categoryclass=None, selectflag=True, objectid=None, programname=None, extraargs=None):
    choices = [("0","-- Escoger --")] if selectflag else []
    
    if(fieldname =='schoolid'):
        choices += (School.objects.get_school_options(schoolid=objectid)) 
        
    if(fieldname =='schoolyear'):
        choices += (UserProgram.objects.get_programyear_options(programname=programname, schoolid=objectid, schoolyear=None)) 
        
    elif(fieldname == 'accessroles'):
        choices += Role.objects.get_role_options(roleid=objectid, **extraargs)
        
    elif(fieldname == 'profilepictureid'):
        choices += get_user_model().objects.get_profile_picture_options(userid=objectid)
        
    else:
        choices += (Category.objects.get_category_options(categoryclass = categoryclass or fieldname))

    form.fields[fieldname].choices = choices

class UploadFileForm(forms.Form):
    
    schoolid = forms.ChoiceField(widget=forms.Select,label='Colegio')
    schoolyear = forms.ChoiceField(widget=forms.Select,initial=DEFAULT_SCHOOL_YEAR,label='A' + mychr('n') + 'o')
    filetype = forms.ChoiceField(widget=forms.Select,label='Tipo de archivo')
    accessroles = forms.MultipleChoiceField(label='Acceso', widget=forms.SelectMultiple(attrs={'size':'10'}))
    
    def __init__ (self, *args, **kwargs):

        # Extract "request" parameter
        request = kwargs.pop('request', None)
        programname = kwargs.pop('request', None)

        super(UploadFileForm, self).__init__(*args, **kwargs)

        # Populate initial drop-downs
        set_dropdown_choices(self,fieldname='schoolid',programname=programname)
        set_dropdown_choices(self,fieldname='schoolyear',programname=programname) # TO-DO Update to use AJAX based on schoolid
        set_dropdown_choices(self,fieldname='filetype',categoryclass='contractfile')
        set_dropdown_choices(self,fieldname='accessroles',selectflag=False, extraargs={'roleclass':['US']})
        
        if(not request.user.is_admin):
            self.fields['schoolid'] = forms.IntegerField(widget=forms.HiddenInput, initial=request.user.schoolid)
            self.fields['schoolyear'] = forms.IntegerField(widget=forms.HiddenInput)

        self.fields['accessroles'].initial = Role.objects.get(name='Public').roleid

        # Set helper properties
        self.helper = FormHelper() 
        setFormHelper(self.helper)
        self.helper.form_tag = False
        
        # Set form layout
        self.helper.layout = Layout(
            Fieldset(
                'Subir archivos',
                'schoolid',
                'schoolyear',
                'filetype',
                'accessroles',
#                 Div(css_class='dropzone', css_id='id_dropzone'),
                HTML('<br>'),
#                 getAdminFormActions(),
            )
        )

    # Specify model
    class Meta:
        model = File

class LoginForm(AuthenticationForm):

    # Define form fields
    username = forms.CharField(label="Nombre de usuario (o correo)", required=True)
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

    # Define form fields
    username = forms.CharField(label='Nombre de usuario (o correo)', max_length=50)
    firstname = forms.CharField(label='Nombre(s)', max_length=100)
    lastname = forms.CharField(label='Apellido(s)', max_length=100)
    usertype = forms.ChoiceField(label='Tipo de usuario')
    schoolid = forms.ChoiceField(label='Colegio', widget=forms.Select, required=False)
    classid = forms.CharField(label='Curso(s)', widget=forms.SelectMultiple, required=False)
    emailaddress = forms.EmailField(label='Correo', max_length=250, required=False)

    # Define constructor
    def __init__(self, *args, **kwargs):
        
        # Extract "request" parameter
        request = kwargs.pop('request')
        
        myschoolid=request.user.schoolid or None
        
        # Call base class constructor (i.e. SignupForm)
        super(SignupForm, self).__init__(*args, **kwargs)

        # Populate usertype drop-down
        set_dropdown_choices(self,fieldname='usertype')
        set_dropdown_choices(self,fieldname='schoolid')

        # Set password fields as optional
        self.fields['password1'].required=False
        self.fields['password2'].required=False

        self.fields['schoolid'].initial=myschoolid
            
        # Set helper properties
        self.helper = FormHelper()
        setFormHelper(self.helper)
        self.helper.form_tag = False

        # Set form layout
        self.helper.layout = Layout(
            Fieldset(
                'Crear Usuario',
                'username',
                'usertype',
                'schoolid',
                'classid',
                'firstname',
                'lastname',
                'emailaddress',
                'password1',
                'password2',
            ),
            getAdminFormActions()
        )

    # Specify model and which fields to include in form
    class Meta:
        model = get_user_model()
        fields = ('username','usertype','schoolid','classid','firstname','lastname','emailaddress','password1','password2')

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

class RewardForm(forms.Form):

    # Define form fields
    rewardid = forms.IntegerField(widget=forms.HiddenInput,required=False)

    rewardcategory = forms.ChoiceField(required=True,label='Categor' + mychr('i') + 'a')
    vendor = forms.CharField(max_length=100,label='Vendedor')
    rewarddisplayname = forms.CharField(max_length=100,label='Premio')
    rewarddescription = forms.CharField(max_length=500,label='Descripci' + mychr('o') + 'n', widget=forms.Textarea(attrs={'rows':4}))
    rewardvalue = forms.IntegerField(label='Valor',localize=True)

    def __init__ (self, *args, **kwargs):

        # Extract extra info
        cancel_type = kwargs.pop('cancel_type', None)
        request = kwargs.pop("request",None)

        # Call base class constructor (i.e. Teacher Form)
        super(RewardForm, self).__init__(*args, **kwargs)
        
        # Set form helper properties
        self.helper = FormHelper()
        setFormHelper(self.helper)
        self.helper.form_tag = False
        
        # Set drop-down options
        set_dropdown_choices(self,fieldname='rewardcategory', categoryclass='reward')
        
        # Set form layout
        self.helper.layout = Layout(
            Fieldset(
                'Crear / Editar premio',
                'rewardcategory',
                'vendor',
                'rewardid',
                'rewarddisplayname',
                'rewarddescription',
                PrependedText('rewardvalue', '$'),
            ),
            getAdminFormActions(cancel_url = 'wakemeup:list_object', cancel_context='objecttype="reward"', cancel_type=cancel_type)
        )

    # Specify model
    class Meta:
        model = Reward
        fields = ('rewardcategory','vendor','rewardid','rewarddisplayname','rewarddescription','rewardvalue')

class SchoolForm(forms.Form):

    # Store original data use policy fileid
#     datausepolicyfileid = forms.IntegerField(required=False, widget=forms.HiddenInput())

    # Define form fields
    schoolid = forms.IntegerField(label='Codigo de colegio', required=False, widget=forms.HiddenInput())
    schooldisplayname = forms.CharField(label='Nombre para mostrar',max_length=100)
    schoolabbreviation = forms.CharField(label='Abreviatura', required=False, max_length=25)
    address = forms.CharField(label='Direcci' + mychr('o') + 'n',max_length=100)
    city = forms.CharField(label='Ciudad',max_length=100)
    department = forms.CharField(label='Departamento',max_length=100)
    
#     # Guardian approval policy
#     guardianapprovalpolicy = forms.MultipleChoiceField(
#         required=False, 
#         label='Politica de aprobaci' + mychr('o') + 'n de tutor',
#         choices = [
#             ("idfullname","Nombre de tutor"),
#             ("idnumber","Numero de cedula"),
#             ("idissuelocation","Lugar de expedici" + mychr('o') + "n"),
#             ("idissuedate","Fecha de expedici" + mychr('o') + "n")
#         ]
#     )

    # Define constructor
    def __init__ (self, *args, **kwargs):

        # Extract request info
        request = kwargs.pop("request",None)
        
        # Call base class constructor (i.e. School Form)
        super(SchoolForm, self).__init__(*args, **kwargs)
        
        # Set form helper properties
        self.helper = FormHelper()
        setFormHelper(self.helper)
        self.helper.form_tag = False
        
        # Set form layout
        self.helper.layout = Layout(
#             'Crear/editar colegio',
            Fieldset(
                None,
#                 'datausepolicyfileid',
                'schoolid',
                'schooldisplayname',
                'schoolabbreviation',
                'address',
                'city',
                'department',
#                 'datausepolicyfile',
#                         InlineCheckboxes('guardianapprovalpolicy'),
            ),
#             getAdminFormActions(cancel_url = 'wakemeup:list_object', cancel_context='objecttype="school"')
        )

#     def clean_guardianapprovalpolicy(self):
#         return self.cleaned_data.get('guardianapprovalpolicy')

    # Specify model
    class Meta:
        model = School

class SchoolRewardForm(forms.Form):

    # Define form fields
    rewardid = forms.IntegerField(widget=forms.HiddenInput)

    selected = forms.BooleanField(required=False,label=' ')
    rewardcategorydisplayname = forms.CharField(required=False,max_length=100,label='Categor' + mychr('i') + 'a',widget=forms.TextInput(attrs={'textonly':True}))
    vendor = forms.CharField(required=False,label='Vendedor',widget=forms.TextInput(attrs={'textonly':True}))
    rewarddisplayname = forms.CharField(required=False,label='Premio',widget=forms.TextInput(attrs={'textonly':True}))
    rewarddescription = forms.CharField(required=False,label='Descripci' + mychr('o') + 'n',widget=forms.TextInput(attrs={'textonly':True}))
    rewardvalue = forms.IntegerField(widget=forms.NumberInput,required=True,label='Valor',localize=True)

    def __init__ (self, *args, **kwargs):
        super(SchoolRewardForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.template = 'wakemeup/admin/edit_inline_formset.html'
        self.helper.field_template = 'bootstrap3/field.html'

    # Specify model
    class Meta:
        model = SchoolReward

class SchoolCalendarForm(forms.Form):

    # Define form fields
    selected = forms.BooleanField(required=False,label=' ',initial=True)
    
    itemdate = forms.DateField(label='Fecha',widget=forms.DateInput(attrs={'class':'dateinputfield','placeholder':'MM/DD/YYYY'}))
    itemtype = forms.ChoiceField(required=True,label='Categor' + mychr('i') + 'a')
    itemdescription = forms.CharField(required=False,widget = forms.TextInput(attrs={'textonly':True}))
    itemnotes = forms.CharField(required=False,max_length=500,label='Notas', widget=forms.Textarea(attrs={'rows':1}))

    def __init__ (self, *args, **kwargs):
        super(SchoolCalendarForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.template = 'wakemeup/admin/edit_inline_formset.html'
        self.helper.field_template = 'bootstrap3/field.html'

        set_dropdown_choices(self,fieldname='itemtype',categoryclass='calendar')
        
    # Specify model
    class Meta:
        model = SchoolCalendar

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
        label='Nombre',
        max_length=100
    )
    
    gradelevel = forms.IntegerField(label='Grado', max_value=12, min_value=1)

    # Define constructor
    def __init__ (self, *args, **kwargs):

        # Extract request info
        request = kwargs.pop("request",None)

        # Call base class constructor (i.e. School Form)
        super(ClassForm, self).__init__(*args, **kwargs)
        
        # Set drop-downs
        set_dropdown_choices(self,fieldname='schoolid',selectflag=False)
        
        # Set form helper properties
        self.helper = FormHelper()
        setFormHelper(self.helper)
        self.helper.form_tag = False

        # Hide fields (if teacher)
        if(request.user.usertype == "TR"):
            myschoolid = Teacher.objects.get(teacheruserid = request.user.userid).schoolid
            self.fields['schoolid'] = forms.IntegerField(widget=forms.HiddenInput, initial=myschoolid)
            self.fields['gradelevel'].widget.attrs['readonly'] = True
            self.fields['classdisplayname'].widget.attrs['readonly'] = True
                    
        # Set form layout
        self.helper.layout = Layout(
            Fieldset(
                'Crear / Editar curso',
                'classid',
                'schoolid',
                Field('classdisplayname', css_class='w-50'),
                Field('gradelevel', css_class='w-50'),
            ),
#             Fieldset(
#                 """Grupos de estudiante <span id="add_usergroup"><a href="#"><i class="fas fa-plus-circle" style="font-size:1.125em;vertical-align:middle"></i></a></span>""",
#                 HTML("""{% if classid != "new" %} {% load django_tables2 %}{% render_table studentgroups %} {% endif %}"""),
#             ),
            getAdminFormActions(cancel_url = 'wakemeup:list_object', cancel_context='objecttype="class"') if not request.user.usertype == "TR" else None
        )

    # Specify model
    class Meta:
        model = Class

class MyUserForm(forms.Form):

    # Define form fields
    username = forms.CharField(label="Nombre de usuario", max_length=50)
    userid = forms.IntegerField(widget=forms.HiddenInput)
    schoolid = forms.ChoiceField(label='Colegio')

    firstname = forms.CharField(max_length=100,label='Primer nombre')
    lastname = forms.CharField(max_length=100,label='Apellido(s)')
    emailaddress = forms.EmailField(label='Correo', max_length=250, required=False)
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
        self.fields['username'].widget.attrs['readonly'] = True

        # Teachers can only add students
        if(not request.user.is_admin()):
            myschoolid = request.user.schoolid # Can only add students to their own school
            self.fields['schoolid'].initial = myschoolid
            self.fields['schoolid'].disabled = True
            self.fields['schoolid'].widget=forms.HiddenInput()
        else:
            myschoolid = None

        # Set drop-downs
        set_dropdown_choices(self,fieldname='schoolid',objectid=myschoolid)
        set_dropdown_choices(self,fieldname='profilepictureid',objectid=request.user.userid,selectflag=False)
        
        # Set form layout
        self.helper.layout = Layout(
            'userid',
            'username',
            'schoolid',
            'firstname',
            'lastname',
            'emailaddress',
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

class ContractForm(forms.Form):

    contractid = forms.IntegerField(widget=forms.HiddenInput, required=False)
    contractname = forms.CharField(label='Actividad',max_length=100)
    teacheruserid = forms.CharField(label='Docente', widget=forms.Select)
    classid = forms.CharField(label='Curso', widget=forms.Select)
    contracttype = forms.CharField(max_length=1,label='Tipo de contrato',widget=forms.HiddenInput, required=False)
    partyuserinfo = forms.CharField(label='Participantes', widget=forms.SelectMultiple)
    contractvalidstartdate = forms.DateField(label='Desde',widget=forms.DateInput(attrs={'class':'dateinputfield','placeholder':'MM/DD/YYYY'}))
    contractvalidenddate = forms.DateField(label='Hasta',widget=forms.DateInput(attrs={'class':'dateinputfield','placeholder':'MM/DD/YYYY'}))
    revisiondeadlinets = forms.DateField(label='', widget=forms.DateInput(attrs={'placeholder':'MM/DD/YYYY'}))
    contractstatus = forms.CharField(max_length=1,label='Estatus', widget=forms.HiddenInput, required=False)

    # Fields used for javascript and form navigation between pages
    initialbudget = forms.IntegerField(widget=forms.HiddenInput, required=False)
    initialcontractvalue = forms.IntegerField(widget=forms.HiddenInput, required=False)

    def clean(self):
        mycontractvalidstartdate = self.cleaned_data.get('contractvalidstartdate')
        mycontractvalidenddate = self.cleaned_data.get('contractvalidenddate')
        myrevisiondeadlinets = self.cleaned_data.get('revisiondeadlinets')

        # Only proceed if valid data provided
        if(mycontractvalidstartdate and mycontractvalidenddate and myrevisiondeadlinets):
            if(not mycontractvalidstartdate <= mycontractvalidenddate):
                msg = "La fecha de fin debe ser despu" + mychr('e') + "s de la fecha de inicio"
                self.add_error('contractvalidstartdate', msg)
    
            if(not mycontractvalidstartdate <= myrevisiondeadlinets <= mycontractvalidenddate):
                msg = "La fecha tope para revisar debe ser entre del plazo del contrato"
                self.add_error('revisiondeadlinets', msg)
    
            # Calculate contract revision cutoff
            contract_length = mycontractvalidenddate - mycontractvalidstartdate
            contractrevision_cutoff = mycontractvalidstartdate + (contract_length * .85)
            
            if(not myrevisiondeadlinets <= contractrevision_cutoff):
                msg = "La fecha tope para revisar debe ser " + str(contractrevision_cutoff) + " o antes"
                self.add_error('revisiondeadlinets',msg)

    def __init__ (self, *args, **kwargs):

        # Extract request argument
        request = kwargs.pop("request")
        contractid = kwargs.pop("contractid")

        # Call base class constructor (i.e. Teacher Form)
        super(ContractForm, self).__init__(*args, **kwargs)
        
        if(contractid != "new"):
            mycontractinfo = ContractInfo.objects.get(contractid)
            mybudget = UserProgram.objects.get(userid=mycontractinfo.teacheruserid,programname='incentive').availablebudget # TO-DO: Pass in correct schoolid
            myinitialcontractvalue = mycontractinfo.contractvalue
        else:
            mycontractinfo = None
            myteacherbudget = UserProgram.objects.get(userid=request.user.userid,programname='incentive') # TO-DO: Pass in correct schoolid
            myinitialcontractvalue = 0

            # Lookup default budget for teacher
            if(myteacherbudget):
                mybudget = myteacherbudget.availablebudget
            else:
                mybudget = 0

        # Set form helper properties
        self.helper = FormHelper()
        setFormHelper(self.helper, label_class = 'col-sm-3', field_class = 'col-sm-9')
        self.helper.form_tag = False # Disable auto-generation of <form> tags
        self.fields['initialbudget'].initial = mybudget
        self.fields['initialcontractvalue'].initial = myinitialcontractvalue or 0
        
        # If user is teacher, hide teacher field
        if(request.user.usertype == "TR"):
            self.fields['teacheruserid'] = forms.IntegerField(widget=forms.HiddenInput, initial=request.user.userid)
        
        # Set form layout
        self.helper.layout = Layout(
            'contractid',
            'contractname',
            'contractstatus',
            'contracttype',
            'initialcontractvalue',
            'initialbudget',
            Fieldset(
                'Participantes',
                'teacheruserid',
                Field('classid',css_class='w-50'),
                'partyuserinfo',
            ),
            Fieldset(
                'Fechas',
                Div(
                    Div(HTML('Plazo'), css_class='col-sm-3'),
                    Div('contractvalidstartdate', css_class='col'),
                    Div('contractvalidenddate', css_class='col'),
                    css_class='row',
                ),
                Div(
                    Div(HTML('Fecha tope para revisar*<br><div id="revisiondeadlinets_info"></div>'), css_class='col-sm-3'),
                    Div('revisiondeadlinets', css_class='col-sm-6'),
                    css_class='row',
                )
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
        fields = ('contractid','contractname','teacheruserid','classid','partyuserinfo','contractvalidstartdate','contractvalidenddate','revisiondeadlinets','contractstatus','contracttype')

class ContractPartyRewardForm(forms.Form):

    contractid = forms.IntegerField(widget=forms.HiddenInput)
    partyuserid = forms.IntegerField(widget=forms.HiddenInput)
    goalid = forms.IntegerField(widget=forms.HiddenInput)

    partyuserfullname = forms.CharField(label="Nombre",max_length=500,required=False)
    rewardid = ChoiceFieldNoValidation(label="Incentivo", required=False)
    rewarddeliveredflag = forms.BooleanField(label='Entregado', required=False)
    actualrewardvalue = forms.IntegerField(label="Costo real", required=False, widget=forms.NumberInput())

    def __init__ (self, *args, **kwargs):

        initialdata = kwargs.get("initial",{})
        rewardoptions = [("0","-- Escoger incentivo --")]
        rewardid = initialdata.get('rewardid')
        
        ContractReward.objects.get_contract_reward_options(contractid=3) # TO-DO: Check why this is hard-coded

        # Call base class constructor (i.e. Teacher Form)
        super(ContractPartyRewardForm, self).__init__(*args, **kwargs)

        if(initialdata):
            for rewardoption in initialdata.get('rewardoptions'):
                rewardoptions.append((rewardoption['rewardid'], rewardoption['rewarddisplayname']))
                
            if(rewardid):
                self.fields['rewardid'].initial = rewardid

        # Populate reward drop-down
        self.fields['rewardid'].choices = rewardoptions

        # Set form helper properties
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_class = 'form-inline'
        self.helper.template = 'wakemeup/contract/evaluate_contract_inline_formset.html'

    class Meta:
        model = ContractPartyReward