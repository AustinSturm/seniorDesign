from django.contrib.auth.models import User, Group
from rest_framework import serializers
from apiAuth.models import Device, Account
from devices import models

# Creates device for the logged in users
# lists object with id deviceId and user.id field
class DeviceSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    deviceId = serializers.CharField(required=True, allow_blank=False)
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    def create(self, validated_data):
        request = self.context['request']
        validated_data['user'] = request.user
        if 'user' in request.data:
            if request.user.is_staff:
                validated_data['user'] = Account.objects.get(id=request.data['user'])
        return Device.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.deviceId = validated_data.get('deviceId', instance.deviceId)
        instance.user = validated_data.get('user', instance.user)
        instance.save()
        return instance

    class Meta:
        model = models.Device
        fields = ('id', 'deviceId', 'user')

class StatisticSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Statistic
        exclude = ('id',)
        extra_kwargs = {'alertTime':{'required':False},
                        'device':{'required':False, 'write_only':True,},
                        }

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Location
        exclude = ('id',)
        extra_kwargs = {'alertTime':{'required':False},
                        'device':{'required':False, 'write_only':True,},
                        }

# serializer for an alert associated to an alert queue
class AlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Alert
        fields = '__all__'
        extra_kwargs = {'id':{'required':False},
                        'alertTime':{'required':False},
                        'uid':{'required':False}
                        }

# can be used to determine all related alerts to a device
class AlertsSerializer(serializers.ModelSerializer):
    # setting to another serialzier allows for serializer.data to contain all related alert to alerts
    alerts = AlertSerializer(many=True, read_only=False, required=False)

    class Meta:
        model = models.Alerts
        fields = ('device', 'alerts')

    def create(self, validated_data):
        alerts_data = validated_data.pop('alerts')
        alerts = models.Alerts.objects.create(**validated_data)
        for alert_data in alerts_data:
            models.Alert.objects.create(alerts=alerts, **alert_data).save()
        return alerts

    #!!!!!! tODO FIGURE OUT why shit doesn't actually update!!!!!!!!!!
    # doesn't even call this function on puts/gets when data that does exist is in the data
    def update(self, instance, validated_data):
        alerts_data = validated_data.pop('alerts')
        if alerts_data:
            for alert_data in alerts_data:
                # try updating the entry
                try:
                    alertUid = alert_data.get('uid')
                    alert = instance.alerts.get(uid=alertUid)
                    alert.alertType = alert_data.get('alertType', alert.alertType)
                    alert.alertTime = alert_data.get('alertTime', alert.alertTime)
                    alert.alertDetails = alert_data.get('alertDetails', alert.alertDetails)
                    print(alert)
                    alert.save()
                # item doesn't exist so create it
                except:
                    print("It happens here!")
                    models.Alert.objects.create(alerts=instance, **alert_data, alertUid=alertUid)
                # create a new entry

        instance.save()
        return instance

class NetworkSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Network
        fields = ('networkList', 'netNum', 'ssid', 'psk', 'netType')
        extra_kwargs = {'netNum': {'required':False},
                        'ssid': {'required':False},
                        'psk': {'required':False},
                        'netType': {'required':False}}

class NetworkListSerializer(serializers.ModelSerializer):
    networkList = NetworkSerializer(many=True, read_only=False, required=False)

    class Meta:
        model = models.NetworkList
        fields = ('device', 'networkList')

    def create(self, validated_data):
        networkList_data = validated_data.pop('networkList')
        networkList = models.NetworkList.objects.create(**validated_data)
        for network_data in networkList_data:
            models.Network.objects.create(networkList=networkList, **network_data).save()
        return networkList


class MediaSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Media
        fields = ('id', 'media',)

class StreamSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Stream
        fields = ('device', 'url', 'frontEnable', 'rearEnable',)

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Event
        fields = ('uid', 'device', 'time', 'command', 'priority')
        extra_kwargs = {'time': {'required':False},
                        'priority': {'required':False},
                        'uid': {'required':False, 'read_only':True},}
