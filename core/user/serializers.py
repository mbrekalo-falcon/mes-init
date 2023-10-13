import datetime

from rest_framework import serializers
from core.helpers.emails import SystemMail
from models.user.models import UserModel, UserDetail


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDetail
        fields = '__all__'

    def create(self, validated_data):
        user_detail = UserDetail(**validated_data)
        user_detail.save()
        return user_detail

    def update(self, instance, validated_data):
        if validated_data:
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
        return instance


class UserSerializer(serializers.ModelSerializer):
    user_detail = UserDetailSerializer()

    class Meta:
        model = UserModel
        exclude = ('groups', 'user_permissions',)

    def update(self, instance, validated_data):
        user_detail = validated_data.pop('user_detail', None)

        if validated_data:
            for attr, value in validated_data.items():
                if attr == 'password':
                    if value:
                        if len(value):
                            instance.set_password(value)
                            instance.last_login = datetime.datetime.now()
                else:
                    setattr(instance, attr, value)
            instance.save()

        if user_detail:
            qv_user_detail = UserDetail.custom_manager.alive().filter(user=instance)
            if qv_user_detail.exists():
                qv_user_detail.update(**user_detail)
            else:
                user_detail_create = UserDetail(user=instance, **user_detail)
                user_detail_create.save()
        return instance


class UserCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserModel
        fields = ('email', 'password', 'first_name', 'last_name',)

    def create(self, validated_data):
        user = UserModel.objects.create_user(**validated_data)
        user.save()

        user_detail_create = UserDetail(user=user)
        user_detail_create.save()
        # Send email for activation
        # SystemMail.activation_email(user)
        # Register account
        #send_custom_email_to_user(user, EmailTemplateOption.Registration)

        return user


class UserListSerializer(serializers.ModelSerializer):
    user_detail = UserDetailSerializer()

    class Meta:
        model = UserModel
        exclude = ('groups', 'user_permissions', 'password')

    def create(self, validated_data):
        user = UserModel.objects.create_user(**validated_data)
        user.save()

        return user

    def update(self, instance, validated_data):
        user_detail = validated_data.pop('user_detail', None)

        if validated_data:
            for attr, value in validated_data.items():
                if attr == 'password':
                    if value:
                        if len(value):
                            instance.set_password(value)
                else:
                    setattr(instance, attr, value)
            instance.save()

        if user_detail:
            qv_user_detail = UserDetail.custom_manager.alive().filter(user=instance)
            if qv_user_detail.exists():
                qv_user_detail.update(**user_detail)
            else:
                user_detail_create = UserDetail(user=instance, **user_detail)
                user_detail_create.save()
        return instance
