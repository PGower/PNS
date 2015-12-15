from __future__ import unicode_literals

from django.db import models


class Mapping(models.Model):
    username = models.CharField(max_length=10)
    computer_name = models.CharField(max_length=50)
    ip_address = models.GenericIPAddressField()
    created = models.DateTimeField(auto_now_add=True)
    expired = models.BooleanField(default=False)
    action = models.CharField(max_length=25, choices=[("LOGIN", "login"), ("LOGOUT", "logout"), ("UPDATE", "update")])
