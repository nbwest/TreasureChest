from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^member/(?P<member_id>[0-9]+)/', views.member, name='member'),
]
