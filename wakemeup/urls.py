from django.conf.urls import url
from . import views

app_name= 'wakemeup' # qualifies url pattern names with 'itemdb' namespace (i.e. 'itemdb:iteminfo')
urlpatterns = [

    # Index (i.e. /wakemeup)
    url(r'^$', views.index, name="index"),
    url(r'^contract/new$', views.create_contract, name="create_contract"),
]