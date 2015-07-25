from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
                  url(r'^$', views.home, name='home'),
                  url(r'^loans/$', views.loans, kwargs=dict(member_id=None), name='loans'),
                  url(r'^loans/(?P<member_id>[0-9]+)/$', views.loans, name='member_loan'),
                  url(r'^returns/$', views.returns, name='returns'),
                  url(r'^membership/', views.membership_admin, name='membership_admin'),
                  url(r'^eod/', views.end_of_day, name='end_of_day'),
              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
