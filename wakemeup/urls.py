from django.conf.urls import url
from django.contrib.auth import views as auth_views
from . import views
from .forms import LoginForm

app_name= 'wakemeup' # qualifies url pattern names with 'wakemeup' namespace (i.e. 'wakemeup:create_contract')
urlpatterns = [

    # Index (i.e. /wakemeup)
    url(r'^$', views.index, name="index"),

    # Contract
    url(r'^contract/(?P<contractid>(\d+|new))$', views.create_contract, name="create_contract"),

    # Admin
    url(r'^admin/(?P<objecttype>(school|class|teacher|student))(/)?$', views.admin_list, name="admin_list"), # Object list
    url(r'^admin/(?P<objecttype>(school|class|teacher|student))/(?P<objectid>\d+)$', views.edit_object, name="edit_object"), # Edit object
    url(r'^admin/(?P<objecttype>(school|class))/(?P<objectid>new)$', views.edit_object, name="edit_object"), # New object
    url(r'^admin/(?P<objecttype>(school|class|teacher|student))/(?P<objectid>\d+)/delete$', views.delete_object, name="delete_object"), # Delete object    
    
    # User 
    url(r'^login/$', auth_views.LoginView.as_view(
            template_name = 'login.html', 
            authentication_form=LoginForm
        )
        , name="login"),
    url(r'^logout/$', auth_views.LogoutView.as_view(), name="logout"),
    url(r'^admin/add_user', views.add_user, name="add_user"),

    # Misc
    url(r'^admin/img/(?P<objecttype>(teacher|student))/(?P<objectid>\d+)/preview$', views.preview_image, name="preview_image"), # Image preview

    # Sample ajax URL
    url(r'^ajax/load-classes/', views.load_classes, name='ajax_load_classes'),

    # Default (catch all)    
    url(r'.*', views.index, name = "default"),

]