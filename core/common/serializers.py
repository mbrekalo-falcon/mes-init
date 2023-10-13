from rest_framework import serializers
from models.common.models import ApplicationRole, AvailableDomain


class ApplicationRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationRole
        fields = '__all__'

    def create(self, validated_data):
        application_role = ApplicationRole(**validated_data)
        application_role.save()
        return application_role

    def update(self, instance, validated_data):
        if validated_data:
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
        return instance


class AvailableDomainSerializer(serializers.ModelSerializer):
    class Meta:
        model = AvailableDomain
        fields = '__all__'
