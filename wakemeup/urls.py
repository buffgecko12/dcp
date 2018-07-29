from django.conf.urls import url
from . import views

app_name= 'wakemeup' # qualifies url pattern names with 'wakemeup' namespace (i.e. 'wakemeup:create_contract')
urlpatterns = [

    # Index (i.e. /wakemeup)
    url(r'^$', views.index, name="index"),

    # Contract
    url(r'^contract/$', views.contract_list, name="contract_list"),
    url(r'^contract/(?P<contractid>(\d+))/detail$', views.contract_detail, name="contract_detail"),
    url(r'^contract/accept$', views.contract_accept, name="contract_accept"),
    url(r'^contract/(?P<contractid>(\d+|new))$', views.create_contract, name="create_contract"),
    url(r'^contract/(?P<contractid>(\d+))/goals$', views.create_contract_goals, name="create_contract_goals"),
    url(r'^contract/(?P<contractid>(\d+))/submit$', views.create_contract_submit, name="create_contract_submit"),

    # Admin
    url(r'^admin/(?P<objecttype>(school|class|teacher|student|reward))(/)?$', views.admin_list, name="admin_list"), # Object list
    url(r'^admin/(?P<objecttype>(school|class|teacher|student|reward))/(?P<objectid>\d+)$', views.edit_object, name="edit_object"), # Edit object
    url(r'^admin/(?P<objecttype>(school|class|reward))/(?P<objectid>new)$', views.edit_object, name="edit_object"), # New object
    url(r'^admin/(?P<objecttype>(school|class|teacher|student|reward|contract))/(?P<objectid>\d+)/delete$', views.delete_object, name="delete_object"), # Delete object    

    # User (TO-DO: Move to root)    
    url(r'^admin/add_user', views.add_user, name="add_user"),
    url(r'^myaccount', views.myaccount, name="myaccount"),

    # Misc
    url(r'^admin/img/(?P<objecttype>(teacher|student))/(?P<objectid>\d+)/preview$', views.preview_image, name="preview_image"), # Image preview

    # Ajax URLs
    url(r'^ajax/load-classes/', views.load_classes, name='ajax_load_classes'),
    url(r'^ajax/load-students/', views.load_students, name='ajax_load_students'),
    url(r'^ajax/load-teachers/', views.load_teachers, name='ajax_load_teachers'),
    url(r'^ajax/load-rewards/', views.load_rewards, name='ajax_load_rewards'),
    url(r'^ajax/manage-user-display/', views.manage_user_display, name='ajax_manage_user_display'),

    url(r'^ajax/addreward/', views.addreward, name='ajax_add_reward'),

    # Default (catch all)    
    url(r'.*', views.index, name = "default"),

]