from django.conf.urls import include, url
from django.contrib import admin
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    url(r'^$', views.base, name='base'),
    url(r'^toybox/', include('toybox.urls', namespace="toybox")),
    url(r'^admin/', include(admin.site.urls)),
]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


