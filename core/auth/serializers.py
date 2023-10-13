from rest_framework import serializers


class LoginUserSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)


class SocialAuthSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    photo_url = serializers.URLField(required=False)
    provider = serializers.CharField(required=True, help_text='FACEBOOK | GOOGLE')
    auth_id = serializers.CharField(required=True)
