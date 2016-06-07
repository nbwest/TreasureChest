from django.conf.urls import include, url
from django.contrib import admin
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.core.urlresolvers import reverse

urlpatterns = [
    url(r'^login/', auth_views.login,{'extra_context':{'title': 'Login'}}),
    url(r'^logout/$', auth_views.logout_then_login),
    url(r'^$', views.base, name='base'),
    url(r'^toybox/', include('toybox.urls', namespace="toybox")),
    url(r'^admin/', include(admin.site.urls)),
    url('^', include('django.contrib.auth.urls')),
    url(r'^report_builder/', include('report_builder.urls'))
]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


