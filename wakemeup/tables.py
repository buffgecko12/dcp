import django_tables2 as tables
from django_tables2.utils import A # alias for accessor
from wakemeup.models.school import *
from wakemeup.models.program import *
from user.models.user import UserReputationEvent, UserBadge

from lib.UsefulFunctions.dateUtils import display_timestamp_range, display_timestamp
from lib.UsefulFunctions.stringUtils import mychr
from django.urls import reverse

EMPTY_TEXT = 'No hay registros.'

def getManageButtons(accessor = None, kwargs = None):
    return tables.TemplateColumn(
        template_name='wakemeup/admin/fields/manage_buttons.html',
        extra_context=kwargs,
        verbose_name='',
        accessor=A(accessor)
    )    

def get_table_attrs(textcenterflag = None, nowrapflag = None):
    attrs = {}
    
    if(textcenterflag):
        attrs['th'] = {'style':'text-align:center'}
        attrs['td'] = {'style':'text-align:center'}
    if(nowrapflag):
        attrs['td'] = {'style':'white-space:nowrap'}

    return attrs

class SchoolsTable(tables.Table):

    objectid = 'schoolid'

#     datausepolicyfileid = tables.TemplateColumn(
#         template_name='wakemeup/admin/fields/db_file.html',
# #         extra_context=kwargs,
#         verbose_name='Politica de uso de datos',
#         accessor=A(objectid)
#     )
# 
#     guardianapprovalpolicy = tables.TemplateColumn(
#         template_name='wakemeup/admin/fields/guardian_policy.html',
# #         extra_context=kwargs,
#         verbose_name='Politica de aprobaci' + mychr('o') + 'n de tutor',
#         accessor=A(objectid)
#     )

    manage_buttons = getManageButtons(accessor=objectid)
    
    class Meta:
        model = School
        empty_text = EMPTY_TEXT
        fields = ('schoolabbreviation','schooldisplayname','address','city','department')
        
class ClassesTable(tables.Table):

    objectid = 'classid'

    manage_buttons = getManageButtons(accessor=objectid)

    teacherdisplayname = tables.Column(verbose_name="Docente")

    class Meta:
        model = Class
        empty_text = EMPTY_TEXT
        fields = ('schoolabbreviation','gradelevel','classdisplayname','teacherdisplayname')

class TeachersTable(tables.Table):

    objectid = 'teacheruserid'
    
    kwargs={
        'objecttype': 'teacher',
        'objectid': A(objectid)
    }

    userdisplayname = tables.Column(verbose_name="Docente")

#     defaultsignaturescanfile = tables.TemplateColumn(
#         template_name='wakemeup/admin/fields/display_image.html',
#         extra_context=kwargs,
#         verbose_name='Firma',
#         accessor=A(objectid)
#     )

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
        fields = ('userdisplayname','emailaddress','schooldisplayname','classinfo')

class RewardsTable(tables.Table):

    objectid = 'rewardid'

    rewardvalue = tables.TemplateColumn(
        template_name='wakemeup/admin/fields/currency_field.html',
        verbose_name='Valor',
    )
    
    manage_buttons = getManageButtons(accessor=objectid)

    class Meta:
        model = Reward
        fields = ('rewardcategorydisplayname','vendor','rewarddisplayname','rewarddescription','rewardvalue')
        empty_text = EMPTY_TEXT

class ContractsTable(tables.Table):

    global get_rowlink

    objectid = 'contractid'

    kwargs={
        'objecttype':'contract', 
        'objectid': A(objectid),
        'displayinfo': {
            'buttonsize':'btn-xs', # Contract button size
            'displaytextflag': True # Target page
        }
    }

    contractstatus = tables.TemplateColumn(
        template_name='wakemeup/contract/include/contractstatus.html',
        verbose_name='Estatus',
        accessor=A(objectid)
    )    

    manage_buttons = tables.TemplateColumn(
        template_name='wakemeup/admin/fields/contract_buttons.html',
        extra_context=kwargs,
        verbose_name='Gesti' + mychr('o') + 'n',
        accessor=A(objectid)
    )    

    def render_contractvalidperiod(self, value):
        return display_timestamp(value.lower) + "-\n" + display_timestamp(value.upper)
    
    def render_teacheruserid(self, record):
        return record.teacherfirstname + ' ' + record.teacherlastname

    def render_revisiondeadlinets(self, value):
        return display_timestamp(value)

    def get_rowlink(record):
        if(record.contractstatus == "D"):
            return reverse('wakemeup:create_contract', kwargs={'contractid':record.contractid})
        else:
            return reverse('wakemeup:get_contract', kwargs={'contractid':record.contractid})
    
    teacheruserid = tables.Column(verbose_name="Docente")
    goalinfo = tables.TemplateColumn(template_name='wakemeup/admin/fields/contract_goals.html', verbose_name='Metas')
    partyuserinfo = tables.TemplateColumn(template_name='wakemeup/admin/fields/contract_parties.html', verbose_name='Participantes')
    
    class Meta:
        model = Contract
        fields = ('contractid','contractname','classdisplayname','teacheruserid','contractvalidperiod','revisiondeadlinets','contractstatus','goalinfo','partyuserinfo','manage_buttons')
        empty_text = EMPTY_TEXT
        
        attrs = {
            'class':'table',
            'th':{'style':'white-space:nowrap'}
        }
        
        row_attrs = {
            'class': "clickable-row mouseicon small",
            'data-href': lambda record: get_rowlink(record),
            'style': "cursor: pointer;"
        }
        
class UserReputationEventsTable(tables.Table):

    eventts = tables.DateTimeColumn(attrs=get_table_attrs(nowrapflag=True),verbose_name="Fecha")
    pointvalue = tables.Column(attrs=get_table_attrs(textcenterflag=True),verbose_name="Puntos")

    class Meta:
        model = UserReputationEvent
        fields = ('eventts','pointvalue','eventdisplayname')
        empty_text = EMPTY_TEXT

        row_attrs = {
            'class': "small",
        }

class UserBadgesTable(tables.Table):

    badgeachievedts = tables.DateTimeColumn(attrs=get_table_attrs(nowrapflag=True),verbose_name="Fecha")
    badgedisplayname = tables.Column(attrs=get_table_attrs(nowrapflag=True),verbose_name="Titulo")

    mybadge = tables.TemplateColumn(
        template_name='wakemeup/admin/fields/badge.html',
        verbose_name='Nivel',
        attrs = get_table_attrs(textcenterflag=True)
    )    

    avatar = tables.TemplateColumn(
        template_name='wakemeup/admin/fields/avatar.html',
        verbose_name='Avatar',
        attrs = get_table_attrs(textcenterflag=True)
    )

    class Meta:
        model = UserBadge
        fields = ('badgeachievedts', 'mybadge', 'badgedisplayname', 'badgedescription')
        empty_text = EMPTY_TEXT
        row_attrs={"class":"small"}