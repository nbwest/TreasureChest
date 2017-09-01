from django.conf.urls import include, url
from django.conf import settings
from django.conf.urls.static import static
from views.borrow import borrow
from views.members import members
from views.returns import returns
from views.transactions import transactions
from views.toys import toys
from views.feedback import feedback
from views.shifts import shifts



urlpatterns = [
                  url(r'^$', shifts, name='home'),
                  url(r'^borrow/$', borrow, kwargs=dict(member_id=None), name='borrow'),
                  url(r'^borrow/(?P<member_id>[0-9]+)/$', borrow, name='borrow'),
                  # url(r'^borrow/success/$', borrow, kwargs=dict(member_id=None), name='borrow'),
                  url(r'^returns/$', returns, name='returns'),
                  url(r'^returns/(?P<member_id>[0-9]+)/$',  returns, name='returns'),
                  url(r'^members/$', members, name='members'),
                  url(r'^members/(?P<member_id>[0-9]+)/$', members, name='members'),
                  url(r'^shifts/', shifts, name='shifts'),
                  url(r'^transactions/', transactions, name='transactions'),
                  url(r'^toys/$',toys, name='toys'),
                  url(r'^toys/(?P<toy_id>\w{0,50})/$',toys, name='toys'),
                  url(r'^feedback/', feedback, name='feedback'),
              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
