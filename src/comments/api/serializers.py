from rest_framework import serializers
from comments import models
from accounts.api.serializers import UserUsernameSerializer


class CommentListAllSerializer(serializers.ModelSerializer):
    user = UserUsernameSerializer()

    class Meta:
        model = models.Comment
        fields = '__all__'
