from django.urls import reverse
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import get_user_model
from django.forms.widgets import HiddenInput, CheckboxSelectMultiple

from crispy_forms.helper import FormHelper
from crispy_forms.layout import *
from crispy_forms.bootstrap import FormActions, TabHolder, Tab, PrependedText, InlineRadios, InlineCheckboxes

from wakemeup.models.school import *
from wakemeup.models.program import *
from wakemeup.models.environment import *
from user.models.authorization import Role

from lib.UsefulFunctions.miscUtils import *
from lib.UsefulFunctions.stringUtils import *

from dotmap import DotMap

BOOLEAN_CHOICES = ((True, 'S' + mychr('i')), (False, 'No'))
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

def get_field_with_checkbox(field):
    mydiv = Div(
               Div(field + '_checkbox', css_class='col-sm-1 my-auto'),
               Div(field, css_class='col-sm-11 my-auto'),
               css_class='row'
        )
    
    return mydiv

def set_dropdown_choices(form, fieldname, categoryclass=None, selectflag=True, lookupargs={}, ignoredefaultsflag=False, sortflag=True, **kwargs):
    choices = [("","-- Escoger --")] if selectflag else []

    if ignoredefaultsflag:
        lookupargs['schoolyear'] = lookupargs.get('schoolyear') or None

    if fieldname =='userid':
        choices += (Program.objects.get_program_options(idfield=fieldname, displayfield='userdisplayname', **lookupargs))
        
    if fieldname =='schoolid':
        choices += (Program.objects.get_program_options(idfield=fieldname, displayfield='schoolabbreviation', **lookupargs))

    if fieldname in ('schoolyear', 'sourceyear'):
        if kwargs.get('expandedflag') == True:
            choices += (Program.objects.get_year_options(startoffset=3, endoffset=3, programrangeflag=True)) # Expanded program years
        else:
            choices += (Program.objects.get_program_options(idfield='schoolyear', **lookupargs)) # Program years

    elif fieldname == 'accessroles':
        choices += Role.objects.get_role_options(**lookupargs)
        
    elif fieldname == 'profilepictureid':
        choices += get_user_model().objects.get_profile_picture_options(**lookupargs)

    elif fieldname == 'programname':
        choices += (Program.objects.get_program_options(idfield=fieldname, **lookupargs))

    else:
        choices += (Category.objects.get_category_options(categoryclass = categoryclass or fieldname))

    # Sort
    if sortflag:
        choices = sorted(choices.copy(), key=lambda x: x[1]) # Sort using second element in tuple

    form.fields[fieldname].choices = choices

def set_initial_value(form, fieldname, default=None):
    form.fields[fieldname].initial = form.fields[fieldname].initial or default

def setup_field(form, fieldname, dropdown=None, default=None):
    if dropdown:
        set_dropdown_choices(form=form, fieldname=fieldname, **dropdown if not dropdown == "default" else {})
        
    set_initial_value(form=form, fieldname=fieldname, default=default)

def setup_fields(form, fieldinfo):
    for fieldname, fieldinfo in fieldinfo.items():
        setup_field(form=form, fieldname=fieldname, dropdown=fieldinfo.get('dropdown'), default=fieldinfo.get('default'))

def set_field_size(field, size=''):
    fieldclass = ' form-control' + ('-' + size) if size else ()

    if not isinstance(field, Field):
        myfield = Field(field, css_class=fieldclass)
    else:
        myfield = field.css_class + fieldclass

    return myfield

# Base form
class MyForm(forms.Form):
    
    config = {}
    readonly = False
    
    def __init__(self, *args, **kwargs):

        # Extract context variables        
        self.context = kwargs.pop('context', {})
        self.request = self.context.get('request', {})
        self.initialvalues = kwargs.get('initial', {})
        self.programname = kwargs.get('programname', {})
        
        super(MyForm, self).__init__(*args, **kwargs)

    def configure(self):
        myconfig = DotMap(self.config)
        
        # Configure fields
        for field, fieldinfo in myconfig.get('fields').items():            
            myfield = self.fields[field]
            
            if fieldinfo.initial:
                myfield.initial = fieldinfo.initial
                
            if fieldinfo.readonly:
                myfield.widget.attrs.update({'readonly':True})
                
            if fieldinfo.hidden:
                myfield.widget = forms.HiddenInput()
                
            if fieldinfo.dropdown:
                info = fieldinfo.dropdown
                set_dropdown_choices(self, fieldname=field, lookupargs=info.lookupargs, selectflag=info.selectflag, sortflag=info.sortflag)

        # Make all fields read-only
        if(self.readonly):
            for field in self.fields:
                self.fields[field].widget.attrs.update({'readonly':True})

class FileForm(MyForm):

    # Program info
    fileid = forms.CharField(widget=forms.HiddenInput, required=False)
    userid = forms.ChoiceField(required=False, label='Usuario')
    programname = forms.ChoiceField(label='Programa')
    schoolid = forms.ChoiceField(label='Colegio', required=False)
    schoolyear = forms.ChoiceField(label='A' + mychr('n') + 'o', required=False)
    
    # File info
    fileclass = forms.ChoiceField(label='Clase')
    contractid = forms.TypedChoiceField(label='Contrato', required=False, empty_value=None)
    filecategory = forms.ChoiceField(label='Tipo de archivo')
    filedescription = forms.CharField(max_length=500, label='Descripci' + mychr('o') + 'n', widget=forms.Textarea(attrs={'rows':4}), required=False)
    accessroles = forms.MultipleChoiceField(label='Acceso', widget=forms.SelectMultiple(attrs={'size':'8'}), required=False)
    url = forms.URLField(label='URL', required=False)
    
    def __init__ (self, *args, **kwargs):
        super(FileForm, self).__init__(*args, **kwargs)

        request = self.request

        # Extract programname (if specified)
        initialvalues = kwargs.get('initial', {})
        programname = initialvalues.get('programname')

        # Hide admin fields
        if not request.user.is_admin():
            self.fields['userid'] = forms.IntegerField(widget=forms.HiddenInput)
            self.fields['programname'].widget = forms.HiddenInput()
            self.fields['schoolid'].widget=forms.HiddenInput()
            self.fields['schoolyear'].widget = forms.HiddenInput()
            self.fields['accessroles'].widget = forms.HiddenInput()

        dropdownoptions = {'userflag':False, 'schoolid':None, 'programname': None, 'schoolyear':None} if request.user.is_admin() else \
                          {'userflag':True, 'schoolid':request.user.schoolid, 'programname': programname}

        # Initialize fields (TO-DO: Update to use AJAX based on schoolid)
        fieldinfo = {
            'schoolid':     {'dropdown':{'lookupargs':{**dropdownoptions}}, 'default':request.user.schoolid},
            'schoolyear':   {'dropdown':{'lookupargs':{**dropdownoptions}}, 'default':DEFAULT_SCHOOL_YEAR},
            'programname':  {'dropdown':{'categoryclass':'program', 'lookupargs':{**dropdownoptions}}},
            'userid':       {'dropdown':{'lookupargs':{'programname':programname, 'userflag':True}}, 'default':request.user.userid},
            'filecategory': {'dropdown':{'categoryclass':'programfile'}},
            'fileclass':    {'dropdown':'default'},
            'accessroles':  {'dropdown':{'lookupargs':{'roleclass':['US']}, 'selectflag':False}, 'default':Role.objects.get(name='Public').roleid if request.user.is_admin() else ''},
        }
        
        setup_fields(self, fieldinfo)
        
        # Set helper properties
        self.helper = FormHelper() 
        setFormHelper(self.helper)
        self.helper.form_tag = False
        
        # Set form layout
        self.helper.layout = Layout(
            Fieldset(
                'Programa',
                Div(
                    Div(set_field_size('programname','sm'), css_class='col-sm-6'),
                    Div(set_field_size('schoolyear','sm'), css_class='col-sm-6'),
                    css_class='row'
                ),
                Div(
                    Div(set_field_size('schoolid','sm'), css_class='col-sm-6'),
                    Div(set_field_size('userid','sm'), css_class='col-sm-6'),
                    css_class='row'
                ),
            HTML('<hr class="separator">'),
            ) if request.user.is_admin() else Div('programname','schoolyear','schoolid','userid'), # Only show for admin
            Fieldset(
                'General',
                'fileid',
                'fileclass',
#                 'contractid',
                'filecategory',
                'filedescription',
                'accessroles',
#                 Div(css_class='dropzone', css_id='id_dropzone'),
                HTML('<hr class="separator">'),
                Fieldset(
                    'Archivos',
                    'url',
                    HTML('<br>'),
    #                 getAdminFormActions(),
                ) if request.user.is_admin() else None
            )
        )

    # Specify model
    class Meta:
        model = File

class FileFormBulk(FileForm):

#     filelist = forms.MultipleChoiceField(label='Archivos', widget=CheckboxSelectMultiple)
    
    def __init__(self, *args, **kwargs):
        super(FileFormBulk, self).__init__(*args, **kwargs)

        self.fields['fileid'].initial = 'bulk'

        # Generate checkbox field for each form field
        for myfield in list(self.fields):
            self.fields[myfield].required = False
            self.fields['{field}_checkbox'.format(field=myfield)] = forms.BooleanField(required=False, label='')

        # Set form layout
        self.helper.layout = Layout(
            Fieldset(
                'Programa',
                'fileid',
                get_field_with_checkbox('programname'),
                get_field_with_checkbox('schoolyear'),
                get_field_with_checkbox('schoolid'),
                get_field_with_checkbox('userid'),
                HTML('<hr class="separator">'),
            ) if self.request.user.is_admin() else Div('programname','schoolyear','schoolid','userid'), # Only show for admin
            Fieldset(
                'General',
                get_field_with_checkbox('fileclass'),
#                 get_field_with_checkbox('contractid'),
                get_field_with_checkbox('filecategory'),
                get_field_with_checkbox('filedescription'),
                get_field_with_checkbox('accessroles'),
            ),
            getAdminFormActions()
        )
        self.helper.label_class += ' my-auto'

class LoginForm(AuthenticationForm):

    # Define form fields
    username = forms.CharField(label="Nombre de usuario", required=True)
#     username = forms.CharField(label="Nombre de usuario (o correo)", required=True)
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
        )

class SignupForm(UserCreationForm):

    # Define form fields
    username = forms.CharField(label='Nombre de usuario (o correo)', max_length=50)
    firstname = forms.CharField(label='Nombre(s)', max_length=100)
    lastname = forms.CharField(label='Apellido(s)', max_length=100)
    usertype = forms.ChoiceField(label='Tipo de usuario')
    schoolid = forms.TypedChoiceField(label='Colegio', widget=forms.Select, required=False, coerce=int, empty_value=None)
    classid = forms.CharField(label='Curso(s)', widget=forms.SelectMultiple, required=False)
    emailaddress = forms.EmailField(label='Correo', max_length=250, required=False)
    sharedaccountflag = forms.ChoiceField(label='Cuenta compartida', required=True, choices=BOOLEAN_CHOICES, initial=False)

    # Program info
    programname = forms.ChoiceField(label='Programa', widget=forms.Select, required=False)
    schoolyear = forms.MultipleChoiceField(label='A' + mychr('n') + 'o', widget=forms.SelectMultiple, required=False)

    # Define constructor
    def __init__(self, *args, **kwargs):
        
        # Extract "request" parameter
        request = kwargs.pop('request')
        
        myschoolid=request.user.schoolid or None
        
        # Call base class constructor (i.e. SignupForm)
        super(SignupForm, self).__init__(*args, **kwargs)

        # Populate usertype drop-down
        set_dropdown_choices(self,fieldname='usertype')
        set_dropdown_choices(self,fieldname='schoolid', ignoredefaultsflag=True)
        set_dropdown_choices(self,fieldname='programname',lookupargs={'schoolid':0, 'excludegeneralflag':False}, ignoredefaultsflag=True)
        set_dropdown_choices(self,fieldname='schoolyear', selectflag=False, ignoredefaultsflag=True)

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
                'programname',
                'schoolyear',
                'password1',
                'password2',
                'sharedaccountflag'
            ),
            getAdminFormActions()
        )

    # Specify model and which fields to include in form
    class Meta:
        model = get_user_model()
        fields = ('username','usertype','schoolid','classid','firstname','lastname','emailaddress','password1','password2','sharedaccountflag')

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
    rewarddisplayname = forms.CharField(max_length=100,label='Incentivo')
    rewarddescription = forms.CharField(max_length=500,label='Descripci' + mychr('o') + 'n', widget=forms.Textarea(attrs={'rows':4}))
    rewardvalue = forms.IntegerField(label='Valor',localize=True, required=False)

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
                'Crear / Editar incentivo',
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
    rewarddisplayname = forms.CharField(required=False,label='Incentivo',widget=forms.TextInput(attrs={'textonly':True}))
    rewarddescription = forms.CharField(required=False,label='Descripci' + mychr('o') + 'n',widget=forms.TextInput(attrs={'textonly':True}))
    rewardvalue = forms.IntegerField(widget=forms.NumberInput,required=False,label='Valor',localize=True)

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
    
    calendarid = forms.CharField(required=False, label='URL de calendario')

    def __init__ (self, *args, **kwargs):
        super(SchoolCalendarForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False
        
class SchoolCalendarForm_set(forms.Form):

    # Define form fields
    selected = forms.BooleanField(required=False,label=' ',initial=True)
    
    itemdate = forms.DateField(label='Fecha',widget=forms.DateInput(attrs={'class':'dateinputfield','placeholder':'MM/DD/YYYY'}))
    itemtype = forms.ChoiceField(required=True,label='Categor' + mychr('i') + 'a')
    itemdescription = forms.CharField(required=False,widget = forms.TextInput(attrs={'textonly':True}))
    itemnotes = forms.CharField(required=False,max_length=500,label='Notas', widget=forms.Textarea(attrs={'rows':1}))

    def __init__ (self, *args, **kwargs):
        super(SchoolCalendarForm_set, self).__init__(*args, **kwargs)

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

class MyAccountForm(MyForm):

    # Define form fields
    username = forms.CharField(label="Nombre de usuario", max_length=50)
    userid = forms.IntegerField(widget=forms.HiddenInput)
    schoolid = forms.ChoiceField(label='Colegio')

    firstname = forms.CharField(max_length=100,label='Primer nombre')
    lastname = forms.CharField(max_length=100,label='Apellido(s)')
    emailaddress = forms.EmailField(label='Correo', max_length=250, required=False)
    profilepictureid = forms.IntegerField(label='Avatar', required=False)

    sharedaccountflag = forms.BooleanField(label='Cuenta compartida', required=False, initial=False)

    def __init__ (self, *args, **kwargs):
        super(MyAccountForm, self).__init__(*args, **kwargs)
        myuser = self.request.user

        # Configure form based on user
        if(myuser):
            myschoolid = {'initial': myuser.schoolid, 'readonly': True} if not myuser.is_admin() else {}
            myschoolid.update({'dropdown':{'lookupargs':{'schoolid': None if myuser.is_admin() else myuser.schoolid, 'userflag':True}}})
    
            # Configure fields
            self.readonly = True if myuser.sharedaccountflag else False
            self.config.update({
                'fields': {
                    'sharedaccountflag': {'hidden': True if not myuser.is_admin() else False},
                    'username': {'initial': myuser.username, 'readonly': True},
                    'schoolid': myschoolid,
                    'profilepictureid': {'hidden': True if myuser.sharedaccountflag else False, 'dropdown': {'lookupargs':{'userid':myuser.userid}, 'selectflag': False, 'sortflag': False}}
                }})
            
            self.configure()

        # Set form helper properties
        self.helper = FormHelper()
        setFormHelper(self.helper)
        self.helper.form_tag = False

        # Set form layout
        self.helper.layout = Layout(
            'userid',
            'username',
            'schoolid',
            'firstname',
            'lastname',
            'emailaddress',
            'sharedaccountflag',
            InlineRadios('profilepictureid', template='wakemeup/admin/profilepicture.html'),
            getAdminFormActions() if not self.readonly else None
        )

    # Make sure email address does not already exist
    def clean_emailaddress(self):
        return validate_emailaddress(self.cleaned_data.get("userid"), self.cleaned_data.get("emailaddress"))

    # Specify model
    class Meta:
        model = get_user_model()
        fields = ('userid','username','schoolid','firstname','lastname','emailaddress','sharedaccountflag','profilepictureid')

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

class CopyProgramForm(MyForm):

    # General info
    programname = forms.ChoiceField(label='Programa')
    schoolid = forms.MultipleChoiceField(label='Colegio', widget=forms.SelectMultiple(attrs={'size':'4'}), required=False)
    schoolyear = forms.TypedChoiceField(label='A' + mychr('n') + 'o nuevo', coerce=int, empty_value=None)
    sourceyear = forms.TypedChoiceField(label='A' + mychr('n') + 'o para copiar', required=False, coerce=int, empty_value=None)

    # Copy options
    exactsourceyearflag = forms.BooleanField(required=False, label='A' + mychr('n') + 'o para copiar tiene que coincidir exactamente')
    createdriveflag = forms.BooleanField(required=False, label='Crear carpeta nueva en Google Drive')
    createcalendarflag = forms.BooleanField(required=False, label='Crear calendario nuevo')
    createdefaultroleflag = forms.BooleanField(required=False, label='Crear rol predeterminado de programa', initial=True)
    copyusersflag = forms.BooleanField(required=False, label='Copiar usuarios', initial=True)
    copyrewardsflag = forms.BooleanField(required=False, label='Copiar incentivos', initial=True)

    def __init__ (self, *args, **kwargs):
        super(CopyProgramForm, self).__init__(*args, **kwargs)

        dropdownoptions = {'userflag':False, 'schoolid':None, 'programname': None, 'schoolyear':None}

        # Initialize fields (TO-DO: Update to use AJAX based on schoolid)
        fieldinfo = {
            'programname':  {'dropdown':{'categoryclass':'program', 'lookupargs':{**dropdownoptions}}},
            'schoolid':     {'dropdown':{'lookupargs':{**dropdownoptions}, 'selectflag':False}},
            'schoolyear':   {'dropdown':{'lookupargs':{**dropdownoptions}, 'expandedflag':True}, 'default':DEFAULT_SCHOOL_YEAR + 1}, # Expanded year list
            'sourceyear':   {'dropdown':{'lookupargs':{**dropdownoptions}}, 'default':DEFAULT_SCHOOL_YEAR}, # default = most recent year
        }
        
        setup_fields(self, fieldinfo)
        
        # Set helper properties
        self.helper = FormHelper() 
        setFormHelper(self.helper)

        # Set form layout
        self.helper.layout = Layout(
            Fieldset(
                'General',
                'programname',
                'schoolid',
                'sourceyear',
                'schoolyear',
            ),
            Fieldset(
                'Opciones de copiar',
                'createdriveflag',
                'createcalendarflag',
                'createdefaultroleflag',
                'copyusersflag',
                'copyrewardsflag',
                'exactsourceyearflag',
                getAdminFormActions(),
            )
        )
