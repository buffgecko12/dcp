import django_tables2 as tables
from django_tables2.utils import A # alias for accessor
from .models.environment import School, Class, Teacher, Student
from .models.contract import Contract, Reward
from users.models import UserReputationEvent, UserBadge

from lib.UsefulFunctions.dateUtils import display_timestamp_range, display_timestamp
from django.urls import reverse

EMPTY_TEXT = 'No hay registros.'

def getManageButtons(accessor = None, kwargs = None):
    return tables.TemplateColumn(
        template_name='wakemeup/admin/fields/manage_buttons.html',
        extra_context=kwargs,
        verbose_name='',
        accessor=A(accessor)
    )    

class SchoolsTable(tables.Table):

    objectid = 'schoolid'

    manage_buttons = getManageButtons(accessor=objectid)
    
    class Meta:
        model = School
        empty_text = EMPTY_TEXT
        exclude = ('schoolid')
        
class ClassesTable(tables.Table):

    objectid = 'classid'

    manage_buttons = getManageButtons(accessor=objectid)

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

    manage_buttons = getManageButtons(accessor=objectid)
    
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

    manage_buttons = getManageButtons(accessor=objectid)

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
    
    manage_buttons = getManageButtons(accessor=objectid)

    class Meta:
        model = Reward
        exclude = ('rewardid','createdbyuserid')
        empty_text = EMPTY_TEXT

class ContractsTable(tables.Table):

    global get_rowlink

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

    def get_rowlink(record):
        if(record.contractstatus == "D"):
            return reverse('wakemeup:create_contract', kwargs={'contractid':record.contractid})
        else:
            return reverse('wakemeup:contract_detail', kwargs={'contractid':record.contractid})
    
    teacheruserid = tables.Column(verbose_name="Docente")
    goalinfo = tables.TemplateColumn(template_name='wakemeup/admin/fields/contract_goals.html', verbose_name='Metas')
    partyuserinfo = tables.TemplateColumn(template_name='wakemeup/admin/fields/contract_parties.html', verbose_name='Participantes')
    
    class Meta:
        model = Contract
        exclude = ('contracttype','classid','guardianapprovalflag','contractapprovalts','revisiondescription','revisionapprovalts','revisiondeadlinets','studentleaderrequirements','teacherrequirements','studentrequirements','contractscanfile','teacherfirstname','teacherlastname')
        empty_text = EMPTY_TEXT
        
        row_attrs = {
            'class': "clickable-row mouseicon small",
            'data-href': lambda record: get_rowlink(record),
            'style': "cursor: pointer;"
        }
        
class UserReputationEventsTable(tables.Table):

    class Meta:
        model = UserReputationEvent
        sequence = ('eventts','pointvalue','eventdisplayname')
        exclude = ('eventid','userid','sourceeventid','contractid')
        empty_text = EMPTY_TEXT

class UserBadgesTable(tables.Table):

    class Meta:
        model = UserBadge
        sequence = ('badgeachievedts', 'badgelevel', 'badgedisplayname')
        exclude = ('badgeid','userid','badgeshortname')
        empty_text = EMPTY_TEXT
