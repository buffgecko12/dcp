from django.conf.urls import url
from django.contrib.auth import views as auth_views
from . import views
from .forms import LoginForm

app_name= 'wakemeup' # qualifies url pattern names with 'wakemeup' namespace (i.e. 'wakemeup:create_contract')
urlpatterns = [

    # Index (i.e. /wakemeup)
    url(r'^$', views.index, name="index"),
    
    # Contract
    url(r'^contract/new$', views.create_contract, name="create_contract"),
    
    # Admin
    url(r'^admin/edit_school', views.edit_school, name="edit_school"),
    url(r'^admin/edit_class', views.edit_class, name="edit_class"),
    url(r'^admin/edit_teacher', views.edit_teacher, name="edit_teacher"),
    url(r'^admin/edit_student', views.edit_student, name="edit_student"),

    # User 
    url(r'^login/$', auth_views.LoginView.as_view(
            template_name = 'login.html', 
            authentication_form=LoginForm
        )
        , name="login"),
    
    url(r'^logout/$', auth_views.LogoutView.as_view(), name="logout"),
    url(r'^admin/add_user', views.add_user, name="add_user"),
    
]