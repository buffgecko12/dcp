from django.conf.urls import url
from . import views

app_name= 'wakemeup' # qualifies url pattern names with 'wakemeup' namespace (i.e. 'wakemeup:create_contract')
urlpatterns = [

    # Index (i.e. /wakemeup)
    url(r'^$', views.index, name="index"),
    
    # Contract
    url(r'^contract/new$', views.create_contract, name="create_contract"),
    
    # Admin
    url(r'^admin/edit_school', views.add_school, name="edit_school"),
    url(r'^admin/edit_class', views.add_school, name="edit_class"),
    url(r'^admin/edit_teacher', views.add_school, name="edit_teacher"),
    url(r'^admin/edit_student', views.add_school, name="edit_student"),
    
]