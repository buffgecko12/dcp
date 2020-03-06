from django.conf.urls import url
from . import views

app_name = 'wakemeup' # qualifies url pattern names with 'wakemeup' namespace (i.e. 'wakemeup:create_contract')
urlpatterns = [

    # Index (i.e. /wakemeup)
    url(r'^$', views.index, name="index"),

    # Contract
    url(r'^contract/$', views.list_contract, name="list_contract"),
    url(r'^contract/(?P<contractid>(\d+))/detail$', views.get_contract, name="get_contract"),
    url(r'^contract/(?P<contractid>(\d+|new))$', views.create_contract, name="create_contract"),

    # Admin
    url(r'^admin/(?P<objecttype>(school|class|teacher|student|reward))(/)?$', views.list_object, name="list_object"), # Object list
    url(r'^admin/(?P<objecttype>(school|class|teacher|student|reward))/(?P<objectid>\d+)$', views.edit_object, name="edit_object"), # Edit object
    url(r'^admin/(?P<objecttype>(school|class|reward))/(?P<objectid>new)$', views.edit_object, name="edit_object"), # New object
    url(r'^admin/(?P<objecttype>(school|class|teacher|student|reward|contract|usergroup))/(?P<objectid>\d+)/delete$', views.delete_object, name="delete_object"), # Delete object    

    # User 
    url(r'^admin/create_user', views.create_user, name="create_user"),
    url(r'^myaccount', views.myaccount, name="myaccount"),

    # Misc
    url(r'^admin/img/(?P<objecttype>(teacher|student))/(?P<objectid>\d+)/preview$', views.preview_image, name="preview_image"), # Image preview
    url(r'^admin/file/(?P<fileid>\d+)$', views.download_file_fromdb, name='download_file_fromdb'), # File download
    url(r'^about$', views.about, name='about'),

    # Ajax
    url(r'^ajax/load-classes/', views.load_classes, name='ajax_load_classes'),
    url(r'^ajax/load-teachers/', views.load_teachers, name='ajax_load_teachers'),
    url(r'^ajax/load-rewards/', views.load_rewards, name='ajax_load_rewards'),
    
    url(r'^ajax/manage-user-display/', views.manage_user_display, name='ajax_manage_user_display'),
    url(r'^ajax/addreward/', views.addreward, name='ajax_add_reward'),

    # Default (catch all)    
    url(r'.*', views.index, name = "default"),
]