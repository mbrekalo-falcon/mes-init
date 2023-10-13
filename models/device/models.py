from django.db import models
from models.common.models import BaseModelFields

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


class DeviceModel(models.Model):
    name = models.CharField(max_length=255)
    note = models.TextField()

    def __str__(self):
        return f'Id: {self.id} Name: {self.name}'


class DeviceCommand(models.Model):
    name = models.CharField(max_length=255)
    identifier = models.IntegerField(unique=True, default=0)
    note = models.TextField(blank=True, null=True)
    default_value = models.JSONField(blank=True, null=True)
    device_model = models.ForeignKey(DeviceModel, on_delete=models.CASCADE)
    domain_switch = models.BooleanField(default=False)

    class Meta:
        unique_together = ('name', 'device_model')

    def __str__(self):
        return f'Id: {self.id} Name: {self.name}'


class DeviceFirmware(models.Model):
    firmware_version = models.CharField(max_length=255)
    firmware_note = models.TextField(blank=True, null=True)
    firmware = models.FileField(upload_to='device-firmware')
    device_model = models.ForeignKey(DeviceModel, on_delete=models.CASCADE)

    def __str__(self):
        return f'Id: {self.id} FW Version: {self.firmware_version} Device Model: {self.device_model.name}'


class Device(BaseModelFields):
    name = models.CharField(max_length=255)
    identifier = models.CharField(max_length=64, db_index=True)

    configured = models.BooleanField(default=False)
    configured_at = models.DateTimeField(blank=True, null=True)

    firmware = models.ForeignKey(DeviceFirmware, on_delete=models.CASCADE)
    device_model = models.ForeignKey(DeviceModel, on_delete=models.CASCADE)
    cluster = models.ForeignKey('cluster.Cluster', on_delete=models.CASCADE)

    def return_last_ping(self):
        pings = DevicePing.custom_manager.alive().filter(device_id=self.id)
        """in case device hasn't been pinged before:"""
        if not pings.exists():
            last_ping = DevicePing(device_ping_status=DevicePingStatus(id=0, name='No data'), message='Nema podataka.')
        else:
            last_ping = pings.order_by('created_at').last()
        return last_ping

    def __str__(self):
        return f'Id: {self.id} Name: {self.name}'


class DeviceCommandRequest(BaseModelFields):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    device_command = models.ForeignKey(DeviceCommand, on_delete=models.CASCADE)
    device_command_updated = models.JSONField(blank=True, null=True)
    data = models.JSONField(blank=True, null=True)
    domain = models.ForeignKey('common.AvailableDomain', blank=True, null=True, on_delete=models.CASCADE)

    class Meta:
        ordering = ('created_at',)

    def __str__(self):
        return f'Id: {self.id} Device name: {self.device.name} Command: {self.device_command.name}'


class DeviceCommandResponse(BaseModelFields):
    device_command_request = models.OneToOneField(DeviceCommandRequest, on_delete=models.CASCADE, related_name='device_command_response')
    response_at = models.DateTimeField(db_index=True)
    applied = models.BooleanField(default=False)
    response_message = models.JSONField(blank=True, null=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return f'Id: {self.id} Command: {self.device_command_request.device_command.name}'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super(DeviceCommandResponse, self).save(force_insert, force_update)
        #  Lets call Channels
        layer = get_channel_layer()
        channel_name = 'device-response-{}'.format(self.device_command_request.device.identifier)
        async_to_sync(layer.group_send)(channel_name, {
            'type': 'events.alarm',
            'content': {
                'id': self.id,
                'device_command_request_id': self.device_command_request.id,
                'device_command_id': self.device_command_request.device_command.id,
                'device_command_name': self.device_command_request.device_command.name,
                'applied': self.applied,
                'response_message': self.response_message,
                'created_at': self.created_at.strftime('%Y-%m-%d %H:%M %z'),
                'created_at_timestamp': self.created_at.strftime('%s')
            }
        })


class DevicePingStatus(models.Model):
    name = models.CharField(max_length=255)
    note = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'Id: {self.id} Name: {self.name}'


class DevicePing(BaseModelFields):
    message = models.TextField(blank=True, null=True)
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    device_ping_status = models.ForeignKey(DevicePingStatus, on_delete=models.CASCADE)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return (
            f'Id: {self.id} Device Id: {self.device.identifier} '
            f'Device Ping Status Id: {self.device_ping_status.id} '
            f'Message: {self.message}'
        )

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super(DevicePing, self).save(force_insert, force_update)

        if not self.device_ping_status_id == 1:
            #  Lets call Channels
            layer = get_channel_layer()
            channel_name = 'device-ping-alert-{}'.format(self.device.cluster_id)
            async_to_sync(layer.group_send)(channel_name, {
                'type': 'events.alarm',
                'content': {
                    'device_id': self.device.id,
                    'device_name': self.device.name,
                    'device_ping_status': self.device_ping_status.name,
                    'message': self.message,
                    'created_at': self.created_at.strftime('%Y-%m-%d %H:%M %z'),
                }
            })

        """
        Delete first 900 records when pings count is over 1000
        """
        total = DevicePing.custom_manager.alive().order_by('created_at')
        if total.count() > 1000:
            slice_time = total[900].created_at
            obsolete_pings = total.filter(created_at__lte=slice_time)
            obsolete_pings.update(deleted=True)
