from django.contrib.auth.models import User, Group
from rest_framework import serializers
from shredder.models import File


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ["url", "username", "email", "groups"]


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ["url", "name"]


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ["file", "remark", "timestamp", "processed", "chunkmap"]

    def create(self, validated_data):
        print(validated_data)
        return super().create(validated_data)
