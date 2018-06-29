import django_tables2 as tables
from django_tables2.utils import A # alias for accessor
from .models.environment import School, Class, Teacher, Student

EMPTY_TEXT = 'No hay registros.'

'''
class DeleteColumn(tables.TemplateColumn):
    def __init__(self, *args, **kwargs):
        super(DeleteColumn, self).__init__(*args, **kwargs)
        
        self.template_name='wakemeup/admin/delete_link.html'
        self.verbose_name=''    
'''

def getDeleteColumn(accessor, kwargs):
    return tables.TemplateColumn(
        template_name='wakemeup/admin/delete_link.html',
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

class UsersTable(tables.Table):

    # Define constructor    
#     def __init__(self, *args, **kwargs):
#         pass
#         # Call base table class constructor
#         super(UsersTable, self).__init__(data = kwargs['data'])
# 
#         objectid = kwargs['objectid']
#         objecttype = kwargs['objecttype']
# 
#         # Create base attributes
#         self.objectid = objectid
#         self.objecttype = objecttype
#         
#         self.mykwargs={
#             'objecttype': objecttype,
#             'objectid': A(objectid)
#         }

    class Meta:
        empty_text = EMPTY_TEXT

class TeachersTable(tables.Table):

    objectid = 'teacheruserid'
    
    kwargs={
        'objecttype': 'teacher',
        'objectid': A(objectid)
    }

    defaultsignaturescanfile = tables.TemplateColumn(
        template_name='wakemeup/admin/display_image.html',
        extra_context=kwargs,
        verbose_name='Firma',
        accessor=A(objectid)
    )

    classinfo = tables.TemplateColumn(
        template_name='wakemeup/admin/teacher_classes.html',
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

class StudentsTable(UsersTable):

    # Call UsersTable constructor
    def __init__(self, *args, **kwargs):
        super(StudentsTable, self).__init__(*args, **kwargs)

    objectid = 'studentuserid'
    
    kwargs={
        'objecttype': 'student',
        'objectid': A(objectid)
    }

    defaultsignaturescanfile = tables.TemplateColumn(
        template_name='wakemeup/admin/display_image.html',
        extra_context=kwargs,
        verbose_name='Firma',
        accessor=A(objectid)
    )

    classinfo = tables.TemplateColumn(
        template_name='wakemeup/admin/teacher_classes.html',
        extra_context=kwargs,
        verbose_name='Cursos',
        accessor=A('classinfo')
    )    

    edit_link = getEditColumn(objectid, kwargs)
    delete_link = getDeleteColumn(objectid, kwargs)

    class Meta(UsersTable.Meta):
        model = Student
        exclude = ('studentuserid','reputationvalue','schoolid','classid')
        sequence = ('firstname','lastname','emailaddress','phonenumber','defaultsignaturescanfile','schooldisplayname')
