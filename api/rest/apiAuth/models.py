from django.db import models
from django.contrib.auth.models import AbstractUser

from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save
from rest_framework.authtoken.models import Token

# Create your models here.

# model formats the data for the tables in the database, establishes relationships
class Account(AbstractUser):
    pass

# autocreates an auth_token for a new user
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)

class Device(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='user')
    deviceId = models.CharField(max_length=24, unique=True)
