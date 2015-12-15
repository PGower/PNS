from django.conf.urls import url
from django.contrib import admin
from endpoint.views import *

urlpatterns = [
    url(r'^mapping/action$', MappingAction.as_view(), name='mapping_action'),
    url(r'^mapping/user/(?P<term>[a-zA-Z0-9]{2,10})/$', InfoForUser.as_view(), name='user_info'),
    url(r'^mapping/address/(?P<term>[0-9\.]{7,15})/$', InfoForAddress.as_view(), name='address_info'),
]
