from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
                  url(r'^$', views.home, name='home'),
                  url(r'^borrow/$', views.borrow, kwargs=dict(member_id=None), name='borrow'),
                  url(r'^borrow/(?P<member_id>[0-9]+)/$', views.borrow, name='borrow'),#member_
                  url(r'^returns/$', views.returns, name='returns'),
                  url(r'^returns/(?P<member_id>[0-9]+)/$',  views.returns, name='returns'),
                  url(r'^members/$', views.members, name='members'),
                  url(r'^members/(?P<member_id>[0-9]+)/$', views.members, name='members'),
                  url(r'^transactions/', views.transactions, name='transactions'),
                  url(r'^reports/', views.reports, name='reports'),
              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
