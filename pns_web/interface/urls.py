from django.conf.urls import url
from interface.views import dashboard_page, realtime_updates_page

urlpatterns = [
    url(r'^$', dashboard_page, name='dashboard'),
    url(r'^realtime/$', realtime_updates_page, name='realtime'),
]
