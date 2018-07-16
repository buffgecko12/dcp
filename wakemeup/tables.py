import django_tables2 as tables
from django_tables2.utils import A # alias for accessor
from .models.environment import School, Class, Teacher, Student
from .models.contract import Contract, Reward

from lib.UsefulFunctions.dateUtils import display_timestamp_range, display_timestamp

EMPTY_TEXT = 'No hay registros.'

'''
class DeleteColumn(tables.TemplateColumn):
    def __init__(self, *args, **kwargs):
        super(DeleteColumn, self).__init__(*args, **kwargs)
        
        self.template_name='wakemeup/admin/fields/delete_button.html'
        self.verbose_name=''    
'''

def getDeleteColumn(accessor, kwargs):
    return tables.TemplateColumn(
        template_name='wakemeup/admin/fields/delete_button.html',
        extra_context=kwargs,
        verbose_name='',
        accessor=accessor
    )    

def getEditColumn(accessor, kwargs):
    return tables.LinkColumn(
        viewname='wakemeup:edit_object',
        kwargs=kwargs,
        verbose_name='',
        text='Editar',
        accessor=accessor
    )

class SchoolsTable(tables.Table):

    objectid = 'schoolid'

    kwargs={
        'objecttype':'school', 
        'objectid': A(objectid)
    }

    # Generate admin columns
    edit_link = getEditColumn(objectid, kwargs)
    delete_link = getDeleteColumn(objectid, kwargs)
    
    class Meta:
        model = School
        empty_text = EMPTY_TEXT
        exclude = ('schoolid')
        
class ClassesTable(tables.Table):

    objectid = 'classid'

    kwargs={
        'objecttype': 'class', 
        'objectid': A(objectid)
    }

    edit_link = getEditColumn(objectid,kwargs)
    delete_link = getDeleteColumn(objectid, kwargs)

    class Meta:
        model = Class
        empty_text = EMPTY_TEXT
        exclude = ('schoolid','classid')

class TeachersTable(tables.Table):

    objectid = 'teacheruserid'
    
    kwargs={
        'objecttype': 'teacher',
        'objectid': A(objectid)
    }

    defaultsignaturescanfile = tables.TemplateColumn(
        template_name='wakemeup/admin/fields/display_image.html',
        extra_context=kwargs,
        verbose_name='Firma',
        accessor=A(objectid)
    )

    classinfo = tables.TemplateColumn(
        template_name='wakemeup/admin/fields/teacher_classes.html',
        extra_context=kwargs,
        verbose_name='Cursos',
        accessor=A('classinfo')
    )    

    edit_link = getEditColumn(objectid, kwargs)
    delete_link = getDeleteColumn(objectid, kwargs)
    
    class Meta:
        model = Teacher
        empty_text = EMPTY_TEXT
        exclude = ('teacheruserid','reputationvalue','schoolid')
        sequence = ('firstname','lastname','emailaddress','phonenumber','defaultsignaturescanfile','schooldisplayname','classinfo')

class StudentsTable(tables.Table):

    objectid = 'studentuserid'
    
    kwargs={
        'objecttype': 'student',
        'objectid': A(objectid)
    }

    defaultsignaturescanfile = tables.TemplateColumn(
        template_name='wakemeup/admin/fields/display_image.html',
        extra_context=kwargs,
        verbose_name='Firma',
        accessor=A(objectid)
    )

    classinfo = tables.TemplateColumn(
        template_name='wakemeup/admin/fields/teacher_classes.html',
        extra_context=kwargs,
        verbose_name='Curso',
        accessor=A('classinfo')
    )

    edit_link = getEditColumn(objectid, kwargs)
    delete_link = getDeleteColumn(objectid, kwargs)

    class Meta:
        model = Student
        exclude = ('studentuserid','reputationvalue','schoolid','classid')
        sequence = ('firstname','lastname','emailaddress','phonenumber','defaultsignaturescanfile','schooldisplayname')
        empty_text = EMPTY_TEXT

class RewardsTable(tables.Table):

    objectid = 'rewardid'

    rewardvalue = tables.TemplateColumn(
        template_name='wakemeup/admin/fields/currency_field.html',
        verbose_name='Valor',
    )
    
    kwargs={
        'objecttype': 'reward',
        'objectid': A(objectid)
    }

    edit_link = getEditColumn(objectid, kwargs)
    delete_link = getDeleteColumn(objectid, kwargs)

    class Meta:
        model = Reward
        exclude = ('rewardid','createdbyuserid')
        empty_text = EMPTY_TEXT

class ContractsTable(tables.Table):

    objectid = 'contractid'

    kwargs={
        'objecttype':'contract', 
        'objectid': A(objectid)
    }

    manage_buttons = tables.TemplateColumn(
        template_name='wakemeup/admin/fields/contract_buttons.html',
        extra_context=kwargs,
        verbose_name='',
        accessor=A(objectid)
    )    

    def render_contractvalidperiod(self, value):
        return display_timestamp_range(value)
    
    def render_teacheruserid(self, record):
        return record.teacherfirstname + ' ' + record.teacherlastname

    def render_revisiondeadlinets(self, value):
        return display_timestamp(value)

    def render_contractstatus(self, value):
        status_dict = {'P':'Pendiente','D':'Borrador','A':'Activo','C':'Completo'}
        return status_dict[value]

    teacheruserid = tables.Column(verbose_name="Docente")
    goalinfo = tables.TemplateColumn(template_name='wakemeup/admin/fields/contract_goals.html', verbose_name='Metas')
    partyuserinfo = tables.TemplateColumn(template_name='wakemeup/admin/fields/contract_parties.html', verbose_name='Participantes')
    
    class Meta:
        model = Contract
        exclude = ('contracttype','classid','guardianapprovalflag','contractapprovalts','revisiondescription','revisionapprovalts','revisiondeadlinets','studentleaderrequirements','teacherrequirements','studentrequirements','contractscanfile','teacherfirstname','teacherlastname')
        empty_text = EMPTY_TEXT