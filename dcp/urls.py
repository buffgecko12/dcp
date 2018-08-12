"""dcp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf.urls import url, include
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView

from wakemeup.forms import LoginForm

urlpatterns = [
#     path('admin/', admin.site.urls),
    url('^wakemeup/', include('wakemeup.urls', namespace='wakemeup'), name='index'),
    url(r'^login/$', auth_views.LoginView.as_view( # Catch login before default url
            template_name = 'registration/login.html', 
            authentication_form=LoginForm
        )
        , name="login"),
    url(r'^', include('django.contrib.auth.urls')), # Auth views (login, logout, reset password)
    url(r'^.*$', RedirectView.as_view(pattern_name='login')), # Redirect all other URLs to "Wake Me Up" homepage
]
