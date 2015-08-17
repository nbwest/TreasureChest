from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
                  url(r'^$', views.home, name='home'),
                  url(r'^loans/$', views.loans, kwargs=dict(member_id=None), name='loans'),
                  url(r'^loans/(?P<member_id>[0-9]+)/$', views.loans, name='member_loan'),
                  url(r'^returns/$', views.returns, name='returns'),
                  url(r'^returns/(?P<member_id>[0-9]+)/$',  views.returns, name='returns'),
                  url(r'^membership/$', views.membership_admin, name='membership_admin'),
                  url(r'^membership/(?P<member_id>[0-9]+)/$', views.membership_admin, name='membership_admin'),#name='member_details'),
                  url(r'^transactions/', views.transactions, name='transactions'),
                  url(r'^reports/', views.reports, name='reports'),
              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
