from django.conf.urls import url
from interface.views import dashboard_page

urlpatterns = [
    url(r'^$', dashboard_page, name='dashboard'),
]
