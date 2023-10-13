from rest_framework import serializers
from models.cluster.models import (
    Cluster, ClusterRoleAlert, ClusterUser, ClusterRole, UserApplicationRole, UserClient,
    ClusterMachineDevice, ApplicationModuleClusterRolePermission
)
from models.common.models import ApplicationRole
from models.machine.models import (Machine)


class ClusterMachineDeviceSerializer(serializers.ModelSerializer):
    cluster_name = serializers.ReadOnlyField(source='cluster.name')
    machine_name = serializers.ReadOnlyField(source='machine.name')
    machine_ip = serializers.ReadOnlyField(source='machine.ip')
    device_name = serializers.ReadOnlyField(source='device.name')
    device_identifier = serializers.ReadOnlyField(source='device.identifier')
    device_status_id = serializers.SerializerMethodField()
    printer_name = serializers.ReadOnlyField(source='printer.name')

    class Meta:
        model = ClusterMachineDevice
        fields = '__all__'

    def get_device_status_id(self, obj):
        status = obj.device.return_last_ping().device_ping_status.id
        return status

    def create(self, validated_data):
        cluster_machine_device = ClusterMachineDevice(**validated_data)
        cluster_machine_device.save()
        return cluster_machine_device

    def update(self, instance, validated_data):
        if validated_data:
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.deleted = False
            instance.save()
        return instance


class ApplicationModuleClusterRolePermissionSerializer(serializers.ModelSerializer):
    application_module_name = serializers.ReadOnlyField(source='application_module.name')
    cluster_role_name = serializers.ReadOnlyField(source='cluster_role.application_role.name')

    class Meta:
        model = ApplicationModuleClusterRolePermission
        fields = '__all__'

    def create(self, validated_data):
        role_module_permission = ApplicationModuleClusterRolePermission(**validated_data)
        role_module_permission.save()
        return role_module_permission

    def update(self, instance, validated_data):
        if validated_data:
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
        return instance


class ClusterRoleSerializer(serializers.ModelSerializer):
    application_role_name = serializers.ReadOnlyField(source='application_role.name')

    class Meta:
        model = ClusterRole
        fields = '__all__'

    def create(self, validated_data):
        cluster_role = ClusterRole(**validated_data)
        cluster_role.save()
        return cluster_role

    def update(self, instance, validated_data):
        if validated_data:
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
        return instance


class UserApplicationRoleSerializer(serializers.ModelSerializer):
    user_data = serializers.SerializerMethodField()
    role_data = serializers.SerializerMethodField()

    class Meta:
        model = UserApplicationRole
        fields = '__all__'

    def get_user_data(self, obj):
        data = {
            "user_fullname": obj.user.full_name,
            "user_email": obj.user.email
        }
        return data

    def get_role_data(self, obj):
        data = {
            "cluster_role_name": obj.cluster_role.application_role.name,
            "cluster_name": obj.cluster_role.cluster.name
        }
        return data

    def create(self, validated_data):
        user_role = UserApplicationRole(**validated_data)
        user_role.save()
        return user_role

    def update(self, instance, validated_data):
        if validated_data:
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
        return instance


class UserClientSerializer(serializers.ModelSerializer):
    client_details = serializers.SerializerMethodField()
    user_details = serializers.SerializerMethodField()

    class Meta:
        model = UserClient
        fields = '__all__'

    def get_client_details(self, obj):
        return {
            'id': obj.client.id,
            'sap_card_code': obj.client.sap_card_code,
            'sap_card_name': obj.client.sap_card_name,
            'type': obj.client.sap_partner_type.name,
        }

    def get_user_details(self, obj):
        return {
            'id': obj.user.id,
            'full_name': obj.user.full_name,
            'email': obj.user.email
        }

    def create(self, validated_data):
        user_client = UserClient(**validated_data)
        user_client.save()
        return user_client

    def update(self, instance, validated_data):
        if validated_data:
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
        return instance


class ClusterUserSerializer(serializers.ModelSerializer):
    user_full_name = serializers.ReadOnlyField(source='user.full_name')
    user_email = serializers.ReadOnlyField(source='user.email')
    cluster_name = serializers.ReadOnlyField(source='cluster.name')
    cluster_city = serializers.ReadOnlyField(source='cluster.city')
    cluster_email = serializers.ReadOnlyField(source='cluster.email')
    user_cluster_roles = serializers.SerializerMethodField()

    class Meta:
        model = ClusterUser
        fields = '__all__'

    def get_user_cluster_roles(self, obj):
        q_roles = UserApplicationRole.custom_manager.alive().filter(
            user=obj.user.id,
            cluster_role__cluster_id=obj.cluster.id
        )
        prepare_data = []
        prepare_data.append({
            "id": role.id,
            "application_role_id": role.cluster_role.application_role.id,
            "application_role_name": role.cluster_role.application_role.name}
                for role in q_roles )

        return prepare_data


    def create(self, validated_data):
        cluster_user = ClusterUser(**validated_data)
        cluster_user.save()
        return cluster_user

    def update(self, instance, validated_data):
        if validated_data:
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
        return instance


class ClusterSerializer(serializers.ModelSerializer):
    information = serializers.SerializerMethodField()

    class Meta:
        model = Cluster
        fields = '__all__'

    def get_information(self, obj):
        cluster = obj.id
        machines = Machine.custom_manager.alive().filter(cluster=cluster).count()
        informations = {'machine_count': machines}
        return informations

    def create(self, validated_data):
        cluster = Cluster(**validated_data)
        cluster.save()

        if not ClusterRole.custom_manager.alive().filter(cluster=cluster).exists():
            ar = ApplicationRole.custom_manager.alive().values_list('id', flat=True)
            for _a in ar:
                cr = ClusterRole(cluster=cluster, application_role_id=_a)
                cr.save()

        return cluster

    def update(self, instance, validated_data):
        if validated_data:
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
        return instance


class ClusterRoleAlertSerializer(serializers.ModelSerializer):

    class Meta:
        model = ClusterRoleAlert
        fields = '__all__'

    def create(self, validated_data):
        user_client = ClusterRoleAlert(**validated_data)
        user_client.save()
        return user_client

    def update(self, instance, validated_data):
        if validated_data:
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
        return instance