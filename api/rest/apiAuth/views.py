from django.contrib.auth.models import Group
from rest_framework import viewsets


from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from rest_framework import generics

from rest_framework import permissions
from rest_framework import authentication

from apiAuth import models
from apiAuth.serializers import UserSerializer, AccountSerializer

# Create your views here.


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = models.Account.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer

#returns user based on token if authorization token set. Admin accounts return all accounts
class AccountViewSet(generics.ListAPIView):
    serializer_class = AccountSerializer
    authentication_classes = (authentication.TokenAuthentication,)

    def get_queryset(self):
        queryset = models.Account.objects.all()
        # if admin return all
        if(self.request.user.is_staff):
            return queryset

        username = self.request.user.username
        #username = self.request.query_params.get('username', None)
        if username is not None:
            queryset = queryset.filter(username=username)

        # queryset.password == request.password then return queryset else return error
        return queryset

# Registers a user
class AccountRegisterViewSet(generics.CreateAPIView):
    serializer_class = AccountSerializer
    permission_classes = (permissions.AllowAny,)
