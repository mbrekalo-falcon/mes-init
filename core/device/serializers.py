from rest_framework import serializers
from models.device.models import (
                                  DeviceModel, DeviceCommand, DeviceFirmware, 
                                  Device, DeviceCommandRequest, DeviceCommandResponse,
                                  DevicePing
)


class DeviceModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = DeviceModel
        fields = '__all__'

    def create(self, validated_data):
        device_model = DeviceModel(**validated_data)
        device_model.save()
        return device_model

    def update(self, instance, validated_data):
        if validated_data:
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
        return instance


class DeviceCommandSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = DeviceCommand
        fields = '__all__'
    
    def create(self, validated_data):
        device_command = DeviceCommand(**validated_data)
        device_command.save()
        return device_command
    
    def update(self, instance, validated_data):
        if validated_data:
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
        return instance


class DeviceFirmwareSerializer(serializers.ModelSerializer):
    device_name = serializers.ReadOnlyField(source='device.name')
    device_model_name = serializers.ReadOnlyField(source='device_model.name')

    class Meta:
        model = DeviceFirmware
        fields = '__all__'

    def create(self, validated_data):
        device_firmware = DeviceFirmware(**validated_data)
        device_firmware.save()
        return device_firmware

    def update(self, instance, validated_data):
        if validated_data:
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
        return instance


class DeviceSerializer(serializers.ModelSerializer):
    device_model_name = serializers.ReadOnlyField(source='device_model.name')
    firmware_version = serializers.ReadOnlyField(source='firmware.firmware_version')

    class Meta:
        model = Device
        fields = '__all__'

    def create(self, validated_data):
        device = Device(**validated_data)
        device.save()
        get_device_initialization_command = DeviceCommand.objects.filter(identifier=6, device_model=device.device_model)
        if get_device_initialization_command.exists():
            get_device_initialization_command = get_device_initialization_command.first()

        DeviceCommandRequest.custom_manager.create(
            device_id=device.id,
            device_command_id=get_device_initialization_command.id
        )
        return device
    
    def update(self, instance, validated_data):
        if validated_data:
            for attr, value, in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
        return instance


class DeviceCommandResponseSerializer(serializers.ModelSerializer):
    device_name = serializers.ReadOnlyField(source='device_command_request.device.name')

    class Meta:
        model = DeviceCommandResponse
        fields = '__all__'

    def create(self, validated_data):
        device_command_request = DeviceCommandResponse(**validated_data)
        device_command_request.save()
        return device_command_request

    def update(self, instance, validated_data):
        if validated_data:
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
        return instance


class DeviceCommandRequestSerializer(serializers.ModelSerializer):
    device_name = serializers.ReadOnlyField(source='device.name')
    device_identifier = serializers.ReadOnlyField(source='device_command.identifier')
    device_command_name = serializers.ReadOnlyField(source='device_command.name')
    device_command_response = DeviceCommandResponseSerializer(required=False)

    class Meta:
        model = DeviceCommandRequest
        fields = '__all__'
    
    def create(self, validated_data):
        device_command_request = DeviceCommandRequest(**validated_data)
        device_command_request.save()
        return device_command_request

    def update(self, instance, validated_data):
        if validated_data:
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
        return instance
    

class DevicePingSerializer(serializers.ModelSerializer):

    class Meta:
        model = DevicePing
        fields = '__all__'

    def create(self, validated_data):
        device_ping = DevicePing(**validated_data)
        device_ping.save()
        return device_ping

    def update(self, instance, validated_data):
        if validated_data:
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
        return instance
