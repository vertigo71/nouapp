from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    url(r'^selector/$', views.selector, name='selector'),
    url(r'^selector/(?P<person_id>[0-9]+)/(?P<datefrom>[0-9]{8})/(?P<dateto>[0-9]{8})/$', views.selector, name='selector'),
    url(r'^selectionlist/(?P<person_id>[0-9]+)/(?P<datefrom>[0-9]{8})/(?P<dateto>[0-9]{8})/$', views.selectionlist, name='selectionlist'),
    url(r'^updatecal/(?P<person_id>[0-9]+)/(?P<datefrom>[0-9]{8})/(?P<dateto>[0-9]{8})/$', views.updatecal, name='updatecal'),
]

