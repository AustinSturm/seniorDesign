from django.contrib.auth.models import User, Group
from rest_framework import serializers
from apiAuth import models

from rest_framework.validators import UniqueValidator

# serializers fields data sent as a result of the call

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Account
        fields = ('url', 'username', 'email', 'first_name', 'password', 'auth_token')
        extra_kwargs = {'auth_token': {'required': False}, 'url':{'required':False}}


# used in getting current user and creating user
class AccountSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True,validators=[UniqueValidator(queryset=models.Account.objects.all())])
    username = serializers.CharField(validators=[UniqueValidator(queryset=models.Account.objects.all())])
    password = serializers.CharField(min_length=8, write_only=True)

    def create(self, validated_data):
        account = models.Account.objects.create_user(validated_data['username'], validated_data['email'], validated_data['password'])
        return account
    class Meta:
        model = models.Account
        fields = ('id', 'email', 'username','password', 'auth_token')
        # how to make a field not required in a serializer
        extra_kwargs = {'auth_token': {'required': False, 'read_only': True}}
