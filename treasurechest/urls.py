from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^toybox/', include('toybox.urls', namespace="toybox")),
    url(r'^admin/', include(admin.site.urls)),
]

