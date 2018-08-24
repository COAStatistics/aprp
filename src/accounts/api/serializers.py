from django.contrib.auth import get_user_model

from rest_framework.serializers import (
    ModelSerializer
)

from accounts.models import UserInformation

User = get_user_model()


class UserDetailSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'first_name',
            'last_name',
        ]


class UserInformationSerializer(ModelSerializer):
    class Meta:
        model = UserInformation
        fields = '__all__'



