
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from rest_framework import generics, mixins

from rest_framework import permissions
from apiAuth import permissions as apiPermissions
from rest_framework import authentication

from apiAuth.models import Device
from devices import models
from devices import serializers

from rest_framework import parsers
from rest_framework.views import APIView

import os
from rest.settings import MEDIA_ROOT

# used for streams
from rest.settings import NGINXROUTE
from uuid import uuid4



from django.shortcuts import get_object_or_404

# return device.id associated with a deviceId
def get_device_id(queryset, deviceId):
    return get_object_or_404(queryset, deviceId=deviceId).id


#@permission_classes((permissions.IsAdminUser))
class device_list(generics.ListCreateAPIView):
    serializer_class = serializers.DeviceSerializer
    authentication_classes = (authentication.TokenAuthentication,)

    # list a users devices or if admin list all
    def get_queryset(self):
        queryset = Device.objects.all()
        if(self.request.user.is_staff):
            return queryset

        user = self.request.user
        if user is not None:
            queryset = queryset.filter(user=user.id)

        return queryset

    def create(self, request, *arg, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        # creates an alerts for the device then for the stream
        models.Alerts.objects.create(device_id=serializer.data['id']).save()
        models.NetworkList.objects.create(device_id=serializer.data['id']).save()
        models.Stream.objects.create(device_id=serializer.data['id'], url=NGINXROUTE + str(uuid4())).save()
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

# display and update a device based on the deviceId
class device_detail(generics.DestroyAPIView, generics.UpdateAPIView):
    serializer_class = serializers.DeviceSerializer
    permission_classes = (apiPermissions.IsDeviceOwner, permissions.IsAuthenticated)

    def get_queryset(self):
        if self.request.user.is_staff:
            return Device.objects.get_queryset()
        queryset = Device.objects.get_queryset().filter(user=self.request.user)
        return queryset

    def get_object(self):
        queryset = self.get_queryset()
        obj = None
        if 'deviceId' in self.request.data:
            obj = get_object_or_404(queryset, deviceId=self.request.data['deviceId'])
        return obj

    # overwrote post function to retrieve specific user
    def post(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    # placeholder, can update device id given a newDeviceId key. Also can change user
    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        if 'newDeviceId' in request.data:
            request.data['deviceId'] = request.data['newDeviceId']
        serializer = serializers.DeviceSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
        return Response(serializer.data)

# lists all alert queues or get one based on deviceId
class alerts_list(generics.ListAPIView):
    queryset = models.Alerts.objects.get_queryset()
    serializer_class = serializers.AlertsSerializer

    def get_queryset(self):
        if self.request.user.is_staff:
            return models.Alerts.objects.all()
        devices = Device.objects.filter(user=self.request.user)
        queryset = models.Alerts.objects.filter(device__in=devices)
        return queryset

    def get_object(self):
        queryset = self.get_queryset()
        obj = queryset[0]
        if 'deviceId' in self.request.data:
            device = get_object_or_404(Device.objects.filter(user=self.request.user), deviceId=self.request.data['deviceId'])
            obj = get_object_or_404(queryset, device=device.id)
        return obj

    def post(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    # clears alert que for a device
    def delete(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if 'device' in request.data:
            alerts = queryset.get(device=int(request.data['device']))
            if alerts:
                for alert in alerts.alerts.get_queryset():
                    alert.delete()
                return Response(status=204)
        return Response(status=500)

# list all location info for deviceId
class device_statistic_list(generics.GenericAPIView, mixins.ListModelMixin):
    serializer_class = serializers.StatisticSerializer
    def get_queryset(self):
        queryset = None
        if 'deviceId' in self.request.data:
            device = models.Device.objects.get(user=self.request.user, deviceId=self.request.data['deviceId'])
            queryset = models.Statistic.objects.filter(device=device)
        return queryset

    def post(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

class device_statistic(mixins.CreateModelMixin, mixins.DestroyModelMixin, generics.GenericAPIView):
    serializer_class = serializers.StatisticSerializer

    def get_queryset(self):
        queryset = None
        if 'deviceId' in self.request.data:
            device = models.Device.objects.get(user=self.request.user, deviceId=self.request.data['deviceId'])
            queryset = models.Statistic.objects.filter(device=device)
        return queryset

    # returns device for user account
    def get_object(self):
        if 'deviceId' in self.request.data:
            obj = get_object_or_404(models.Device.objects.all(), user=self.request.user, deviceId=self.request.data['deviceId'])
            return obj
        else:
            return None

    # create one statistic
    def post(self, request, *args, **kwargs):
        device = self.get_object()
        self.request.data['device'] = device.id
        return self.create(request, *args, **kwargs)

    # deletes all elements in the queue
    def delete(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        for element in queryset:
            element.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# list all location info for deviceId
class device_location_list(generics.GenericAPIView, mixins.ListModelMixin):
    serializer_class = serializers.LocationSerializer
    def get_queryset(self):
        queryset = None
        if 'deviceId' in self.request.data:
            device = models.Device.objects.get(user=self.request.user, deviceId=self.request.data['deviceId'])
            queryset = models.Location.objects.filter(device=device)
        return queryset

    def post(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

class device_location(mixins.CreateModelMixin, mixins.DestroyModelMixin, generics.GenericAPIView):
    serializer_class = serializers.LocationSerializer

    def get_queryset(self):
        queryset = None
        if 'deviceId' in self.request.data:
            device = models.Device.objects.get(user=self.request.user, deviceId=self.request.data['deviceId'])
            queryset = models.Location.objects.filter(device=device)
        return queryset

    # returns device for user account
    def get_object(self):
        if 'deviceId' in self.request.data:
            obj = get_object_or_404(models.Device.objects.all(), user=self.request.user, deviceId=self.request.data['deviceId'])
            return obj
        else:
            return None

    def post(self, request, *args, **kwargs):
        req_fields = ['device', 'longitude', 'latitude', 'altitude']
        #check if req_fields are set
        if all(field in request.data for field in req_fields):
            return self.create(request, *args, **kwargs)
        return Response(status=400)

    # deletes all elements in the queue
    def delete(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        for element in queryset:
            element.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# lists all ntworks or get one based on device_id
class networkList_list(generics.ListAPIView):
    serializer_class = serializers.NetworkListSerializer

    def get_queryset(self):
        if self.request.user.is_staff:
            return models.NetworkList.objects.all()
        devices = Device.objects.filter(user=self.request.user)
        queryset = models.NetworkList.objects.filter(device__in=devices)
        return queryset

    def post(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if 'deviceId' in self.request.data:
            instance = get_object_or_404(queryset, device_id=get_device_id(Device.objects.filter(user=self.request.user), self.request.data['deviceId']) )
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        return self.get(request)

# view to pull alerts based on device id TODO: delete an alert, add an alert, update
class device_alerts(generics.RetrieveUpdateAPIView, mixins.CreateModelMixin):
    serializer_class = serializers.AlertSerializer

    def get_queryset(self):
        if self.request.user.is_staff:
            return models.Alerts.objects.all()
        devices = Device.objects.filter(user=self.request.user)
        queryset = models.Alerts.objects.filter(device__in=devices)
        return queryset

    def get_object(self):
        queryset = self.get_queryset()
        obj = None
        if 'device' in self.request.data:
            queryset = models.Alerts.objects.get(device__id=int(self.request.data['device']))
            if 'id' in self.request.data:
                obj = queryset.alerts.get(id=int(self.request.data['id']))
        return obj

    def post(self, request, *args, **kwargs):
        req_fields = ['device', 'alertType', 'alertDetails']
        #check if req_fields are set
        if all(field in request.data for field in req_fields):
            alerts = models.Alerts.objects.get(device__id=self.request.data['device'])
            print(alerts)
            self.request.data['alerts'] = alerts.id
            return self.create(request, *args, **kwargs)
        return Response(status=400)


# add/remove networks from networkList
# add : requires post with "deviceId" at minimum, + optional all other params
# del : requires delete with "deviceId" and "netNum", returns 204
class device_network(mixins.CreateModelMixin, mixins.DestroyModelMixin, generics.GenericAPIView):
    serializer_class = serializers.NetworkSerializer

    def get_queryset(self):
        devices = Device.objects.filter(user=self.request.user)
        queryset = models.NetworkList.objects.filter(device__in=devices)
        return queryset

    def get_object(self):
        queryset = self.get_queryset()
        obj = None
        if 'deviceId' in self.request.data:
            if 'netNum' in self.request.data:
                # get networkList based on deviceId
                networkList = get_object_or_404(self.get_queryset(), device_id=get_device_id(Device.objects.filter(user=self.request.user), self.request.data['deviceId']) )
                # return network from list of networks based on networkList for a device, grab the one with the netNum
                obj = get_object_or_404(models.Network.objects.filter(networkList_id=networkList.id), netNum=self.request.data['netNum'])
        return obj

    def post(self, request, *args, **kwargs):
        if 'deviceId' in self.request.data:
            networkList = get_object_or_404(self.get_queryset(), device_id=get_device_id(Device.objects.filter(user=self.request.user), self.request.data['deviceId']) )
            self.request.data.update({'networkList':networkList.id})
        return self.create(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


# todo force it to upload to nginx rtmp server, api just maps the urls? else get it to return media
# todo delete videos
# todo create new view that renders the media data?
# upload file to /device/upload/<deviceId>/<filename> or retrieve urls for a device. Requires header
class device_upload(generics.ListCreateAPIView):
    serializer_class = serializers.MediaSerializer
    parser_classes = (parsers.MultiPartParser,)

    def get_queryset(self):
        device = Device.objects.get(user=self.request.user, deviceId=self.request.META['HTTP_DEVICEID'])
        return models.Media.objects.filter(device=device.id)

    #works but uploads to filename stored in the MultiPartParser data opposed to the url
    def perform_create(self, serializer):
        device = Device.objects.get(user=self.request.user, deviceId=self.request.META['HTTP_DEVICEID'])
        serializer.save(device=device, media = self.request.data['file'])

# todo : add an update for frontEnable and rearEnable
class device_stream(generics.ListAPIView):
    serializer_class = serializers.StreamSerializer

    def get_queryset(self):
        if self.request.user.is_staff:
            return models.Stream.objects.all()
        device = Device.objects.filter(user=self.request.user)
        queryset = models.Stream.objects.filter(device__in=device)
        return queryset

    def get_object(self):
        queryset = self.get_queryset()
        obj = queryset[0]
        if 'deviceId' in self.request.data:
            device = get_object_or_404(Device.objects.filter(user=self.request.user), deviceId=self.request.data['deviceId'])
            obj = get_object_or_404(queryset, device=device.id)
        return obj

    def post(self, request, *args, **kwargs):
        instance = self.get_object()
        if ('frontEnable' in self.request.data):
            instance.frontEnable = self.request.data['frontEnable']
            instance.save()
        if ('rearEnable' in self.request.data):
            instance.rearEnable = self.request.data['rearEnable']
            instance.save()

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

# lists device que based on deviceId
class device_eventQ(generics.GenericAPIView):
    serializer_class = serializers.EventSerializer

    def get_queryset(self):
        queryset = []
        if 'deviceId' in self.request.data:
            device = models.Device.objects.get(user=self.request.user, deviceId=self.request.data['deviceId'])
            queryset = models.Event.objects.filter(device=device)
        return queryset

    def post(self, request, *args, **kwargs):
        instance = self.get_queryset()
        serializer = self.get_serializer(instance, many=True)
        return Response(serializer.data)

# used to add / delete event
class device_event(mixins.CreateModelMixin, mixins.DestroyModelMixin, generics.GenericAPIView):
    serializer_class = serializers.EventSerializer

    # return potential devices
    def get_queryset(self):
        return models.Device.objects.filter(user=self.request.user)

    def get_object(self):
        obj = None
        if 'deviceId' in self.request.data:
            if 'uid' in self.request.data:
                device = get_object_or_404(self.get_queryset(), deviceId=self.request.data['deviceId'])
                events = models.Event.objects.filter(device=device)
                obj = get_object_or_404(events, uid=self.request.data['uid'])
        return obj

    def post(self, request, *args, **kwargs):
        if 'deviceId' in request.data:
            request.data['device'] = get_device_id(self.get_queryset(), request.data['deviceId'])
            return self.create(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
