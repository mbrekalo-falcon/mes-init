from rest_framework import serializers
from django.db.models import F

from models.machine.models import MachineModel, Machine


class MachineModelSerializer(serializers.ModelSerializer):
    compatible_diameters = serializers.SerializerMethodField()

    class Meta:
        model = MachineModel
        fields = "__all__"
    
    def create(self, validated_data):
        machine_model = MachineModel(**validated_data)
        machine_model.save()
        return machine_model

    def update(self, instance, validated_data):
        if validated_data:
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
        return instance


class MachineSerializer(serializers.ModelSerializer):
    machine_model_name = serializers.ReadOnlyField(source='machine_model.name')
    is_cutter = serializers.ReadOnlyField(source='machine_model.bar_cutter')

    class Meta:
        model = Machine
        fields = '__all__'
    
    def create(self, validated_data):
        machine = Machine(**validated_data)
        machine.save()
        return machine

    def update(self, instance, validated_data):
        if validated_data:
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
        return instance
