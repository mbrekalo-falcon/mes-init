import json
from core.__init__ import *
from django.utils import timezone

from core.device.serializers import (
    DeviceSerializer, DeviceCommandRequestSerializer, DeviceCommandResponseSerializer, DevicePingSerializer,
    DeviceFirmwareSerializer
)
from django.utils.timezone import now
from models.cluster.models import ClusterMachineDevice
from models.device.models import Device, DeviceCommandRequest, DeviceFirmware
from models.machine.models import Machine, MachineModel
import logging

logger = logging.getLogger('tempname')


class DeviceApi(
    generics.GenericAPIView
):
    """
        Expose Device API
    """
    queryset = Device.custom_manager.alive()
    serializer_class = DeviceSerializer
    permission_classes = (AllowAny,)

    def get(self, request, identifier):

        if not identifier:
            return rest_default_response(status=status.HTTP_403_FORBIDDEN, message='Please provide identifier.')

        device = self.queryset.filter(identifier=identifier)
        if not device.exists():
            return rest_default_response(status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(device.first())
        return rest_default_response(data=serializer.data, status=status.HTTP_200_OK)

    def put(self, request, identifier):
        """
        Sets configured to True and configured_at to current datetime
        """
        if not identifier:
            return rest_default_response(status=status.HTTP_403_FORBIDDEN, message='Please provide identifier.')
        device = self.queryset.filter(identifier=identifier)
        if not device.exists():
            return rest_default_response(status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()
        data['configured'] = True
        data['configured_at'] = now()
        serializer = self.serializer_class(data=data, instance=device.first(), partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return rest_default_response(data=serializer.data, status=status.HTTP_200_OK)
        return rest_default_response(message=serializer.errors, status=status.HTTP_403_FORBIDDEN)


class DeviceCommandRequestApi(
    generics.GenericAPIView
):
    """
        Request Device Command API
    """
    queryset = DeviceCommandRequest.custom_manager.alive()
    serializer_class = DeviceCommandRequestSerializer
    permission_classes = (AllowAny,)

    def get(self, request, identifier):
        """
        Fetches all available command requests for device
        """

        if not identifier:
            return rest_default_response(status=status.HTTP_403_FORBIDDEN, message='Please provide identifier.')

        commands = self.queryset.filter(device__identifier=identifier).filter(device_command_response__isnull=True)
        if not commands.exists():
            return rest_default_response(status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(commands.first())
        return rest_default_response(data=serializer.data, status=status.HTTP_200_OK)


class DeviceCommandResponseApi(
    generics.GenericAPIView
):
    """
        Response Device Command API
    """
    serializer_class = DeviceCommandResponseSerializer
    permission_classes = (AllowAny,)

    def post(self, request, identifier):
        data = request.data.copy()
        data['device_command_request'] = identifier
        serializer = self.serializer_class(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return rest_default_response(data=serializer.data, status=status.HTTP_200_OK)
        return rest_default_response(message=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DevicePingApi(
    generics.GenericAPIView
):
    """
        Device Ping API
    """
    serializer_class = DevicePingSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        data = request.data.copy()
        dev_ident = Device.custom_manager.alive().filter(identifier=data['identifier'])
        if not dev_ident.exists():
            return rest_default_response(status=status.HTTP_404_NOT_FOUND)
        data['device'] = dev_ident.first().id
        serializer = self.serializer_class(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return rest_default_response(data=serializer.data, status=status.HTTP_200_OK)
        return rest_default_response(message=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeviceCurrentFirmwareApi(
    generics.GenericAPIView
):
    """
        Request Current Device Firmware API
    """
    queryset = DeviceFirmware.objects.all()
    serializer_class = DeviceFirmwareSerializer
    permission_classes = (AllowAny,)

    def get(self, request, identifier):
        """
        Fetches all available command requests for device
        """

        if not identifier:
            return rest_default_response(status=status.HTTP_403_FORBIDDEN, message='Please provide identifier.')

        current_firmware = self.queryset.filter(device_model__device__identifier=identifier)
        if not current_firmware.exists():
            return rest_default_response(status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(current_firmware.last())
        return rest_default_response(data=serializer.data, status=status.HTTP_200_OK)


class MachineDomainApi(
    APIView
):
    """
        Get current domain for machine
    """
    queryset = Device.custom_manager.alive()
    permission_classes = (AllowAny,)

    def get(self, request, identifier):
        if not identifier:
            return rest_default_response(status=status.HTTP_403_FORBIDDEN, message='Please provide identifier.')

        q_device = self.queryset.filter(identifier=identifier)
        if not q_device.exists():
            return rest_default_response(status=status.HTTP_404_NOT_FOUND, message="No device with this identifier.")
        device = q_device.first()
        q_cmd = ClusterMachineDevice.custom_manager.alive().filter(device_id=device.id)
        if not q_cmd.exists():
            return rest_default_response(status=status.HTTP_404_NOT_FOUND, message="Machine is not connected to cluster.")
        cmd = q_cmd.first()
        domain = cmd.domain
        if not domain:
            return rest_default_response(status=status.HTTP_404_NOT_FOUND, message="Domain not defined for this machine-device.")
        data = {"domain": domain}
        return rest_default_response(data=data, status=status.HTTP_200_OK)