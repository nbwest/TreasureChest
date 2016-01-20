from django.conf.urls import include, url
from django.conf import settings
from django.conf.urls.static import static

# from . import views
from views.home import home
from views.borrow import borrow
from views.members import members
from views.returns import returns
from views.transactions import transactions
from views.reports import reports
from views.toys import toys
from views.feedback import feedback



urlpatterns = [
                  url(r'^$', borrow, kwargs=dict(member_id=None), name='home'),
                  url(r'^borrow/$', borrow, kwargs=dict(member_id=None), name='borrow'),
                  url(r'^borrow/(?P<member_id>[0-9]+)/$', borrow, name='borrow'),#member_
                  url(r'^returns/$', returns, name='returns'),
                  url(r'^returns/(?P<member_id>[0-9]+)/$',  returns, name='returns'),
                  url(r'^members/$', members, name='members'),
                  url(r'^members/(?P<member_id>[0-9]+)/$', members, name='members'),
                  url(r'^transactions/', transactions, name='transactions'),
                  url(r'^reports/', reports, name='reports'),
                  url(r'^toys/$',toys, name='toys'),
                  url(r'^toys/(?P<toy_id>[0-9]+)/$',toys, name='toys'),
                  url(r'^feedback/', feedback, name='feedback'),
              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
