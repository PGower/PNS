from django.conf.urls import url
from endpoint.views import *

urlpatterns = [
    url(r'^mapping/action$', MappingAction.as_view(), name='mapping_action'),
    url(r'^mapping/user/$', InfoForUser.as_view(), name='user_info'),
    url(r'^mapping/address/$', InfoForAddress.as_view(), name='address_info'),
    url(r'^search/$', NameSearch.as_view(), name='search'),
    url(r'^mapping/realtime$', RealtimeUpdates.as_view(), name='mapping_realtime'),
    url(r'^mapping/realtime/(?P<last_id>[0-9].*)/$', RealtimeUpdates.as_view(), name='mapping_realtime_last'),
]
