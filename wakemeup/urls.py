from django.urls import re_path
from . import views

app_name = 'wakemeup' # qualifies url pattern names with 'wakemeup' namespace (i.e. 'wakemeup:create_contract')
urlpatterns = [

    # Index (i.e. /wakemeup)
    re_path(r'^$', views.index, name="index"),

    # Contract
    re_path(r'^contract/$', views.list_contract, name="list_contract"),
    re_path(r'^contract/(?P<contractid>(\d+))/detail$', views.get_contract, name="get_contract"),
    re_path(r'^contract/(?P<contractid>(\d+|new))$', views.create_contract, name="create_contract"),

    # Admin
    re_path(r'^admin/(?P<objecttype>(school|class|teacher|reward))(/)?$', views.list_object, name="list_object"), # Object list
    re_path(r'^admin/(?P<objecttype>(school|class|teacher|reward))/(?P<objectid>\d+)$', views.edit_object, name="edit_object"), # Edit object
    re_path(r'^admin/(?P<objecttype>(school|class|reward))/(?P<objectid>new)$', views.edit_object, name="edit_object"), # New object
    re_path(r'^admin/(?P<objecttype>(school|class|teacher|reward|contract))/(?P<objectid>\d+)/delete$', views.delete_object, name="delete_object"), # Delete object    

    # General
    re_path(r'^(?P<objecttype>(school|class|teacher|reward))(/)?$', views.list_object, name="list_object_general"), # Object list (non-admin)

    re_path(r'^admin/tools$', views.execute_admintools, name="execute_admintools"),
    re_path(r'^admin/edit_permissions', views.edit_permissions, name="edit_permissions"),
    re_path(r'^admin/manage_program', views.manage_program, name="manage_program"),

    # User 
    re_path(r'^admin/create_user', views.create_user, name="create_user"),
    re_path(r'^myaccount', views.myaccount, name="myaccount"),

    # Calendar
    re_path(r'^calendar/', views.get_calendar, name='get_calendar'),

    # Files
    re_path(r'^files$', views.list_file, name="list_file"),
    re_path(r'^files/edit/(?P<fileid>(bulk))?$$', views.edit_file, name="edit_file_bulk"),
    re_path(r'^files/edit/(?P<fileid>(\d+|new))$', views.edit_file, name="edit_file"),
    re_path(r'^files/download/(?P<fileid>\d+)$', views.get_file, name='get_file'), # File download
    
    # Misc
    re_path(r'^admin/img/(?P<objecttype>(teacher))/(?P<objectid>\d+)/preview$', views.preview_image, name="preview_image"), # Image preview
    re_path(r'^about$', views.about, name='about'),
    re_path(r'^howtoparticipate$', views.howtoparticipate, name='howtoparticipate'),

    # Ajax
    re_path(r'^ajax/load-classes/', views.load_classes, name='ajax_load_classes'),
    re_path(r'^ajax/load-teachers/', views.load_teachers, name='ajax_load_teachers'),
    re_path(r'^ajax/load-rewards/', views.load_rewards, name='ajax_load_rewards'),
    
    re_path(r'^ajax/manage-user-display/', views.manage_user_display, name='ajax_manage_user_display'),
    re_path(r'^ajax/addreward/', views.addreward, name='ajax_add_reward'),

    # Default (catch all)    
    re_path(r'.*', views.index, name="default"),
]