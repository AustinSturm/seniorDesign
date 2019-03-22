from django.db import models
from apiAuth.models import Device
from datetime import datetime
from uuid import uuid4
from rest.settings import MEDIA_ROOT

# Create your models here.

class Alerts(models.Model):
    device = models.OneToOneField(Device, on_delete=models.CASCADE, related_name='device')

class Alert(models.Model):
    alerts = models.ForeignKey(Alerts, on_delete=models.CASCADE, related_name='alerts')
    uid = models.CharField(max_length=40, default=uuid4, unique=True)
    alertType = models.CharField(max_length=20, default='', blank=True)
    alertTime = models.DateTimeField(default=datetime.now, blank=True)
    alertDetails = models.TextField(default='', blank=True)

    class Meta:
            ordering = ['alertTime']

class NetworkList(models.Model):
    device = models.OneToOneField(Device, on_delete=models.CASCADE, related_name='networkList_device')

# todo: auto increment NetNum based on current highest netNum associated with networkList
class Network(models.Model):
    class Meta:
        ordering = ['-netNum']
        unique_together = ("networkList", "netNum")

    networkList = models.ForeignKey(NetworkList, on_delete=models.CASCADE, related_name='networkList')
    netNum = models.IntegerField(null=True)
    ssid = models.CharField(max_length=48, default='', blank=True)
    psk = models.CharField(max_length=48, default='', blank=True)
    # only set to WPA, WPA2, WEP or None
    netType = models.CharField(max_length=48, default='', blank=True)

    # returns the highest netNum for that NetList
    #def getNetNum(networkList):
    #    return Network.objects.filter(networkList=networkList)[0].netNum


class Location(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='location_device')
    longitude = models.DecimalField(max_digits=16, decimal_places=6, null=True)
    latitude = models.DecimalField(max_digits=16, decimal_places=6, null=True)
    altitude = models.DecimalField(max_digits=16, decimal_places=6, null=True)
    alertTime = models.DateTimeField(default=datetime.now, blank=True)

class Statistic(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='statistic_device')
    accel_x = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    accel_y = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    accel_z = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    statTime = models.DateTimeField(default=datetime.now, blank=True)

def user_directory(instance, filename):
    return '/'.join([str(instance.device.deviceId), filename])

class Media(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='media_device', default=1)
    media = models.FileField(blank=True, default='', upload_to=user_directory)

# class used to determine stream location for a device and camera status
class Stream(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='stream_device', default=1)
    url = models.URLField(blank=True, unique=True)
    frontEnable = models.BooleanField(default=False)
    rearEnable = models.BooleanField(default=False)

# events to trigger device actions
# todo: create events from other views
class Event(models.Model):
    class Meta:
        ordering = ['priority']

    uid = models.CharField(max_length=40, default=uuid4, unique=True)
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='event_device', default=1)
    time = models.DateTimeField(default=datetime.now, blank=True)
    command = models.CharField(max_length=128, default='', blank=True)
    # priority is 1-3 with 1 highest priority
    priority = models.IntegerField(default=3, null=False)
