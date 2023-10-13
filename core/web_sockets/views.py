from asgiref.sync import async_to_sync

from channels.generic.websocket import JsonWebsocketConsumer

from models.cluster.models import Cluster
from models.device.models import Device
from models.user.models import UserModel


class EventDeviceResponse(JsonWebsocketConsumer):

    def connect(self):
        kwargs = self.scope["url_route"]["kwargs"]["device_identifier"]
        if not kwargs:
            self.disconnect(0)

        qv_device = Device.custom_manager.alive().filter(identifier=kwargs)
        if not qv_device.exists():
            self.disconnect(0)

        channel_name = f"device-response-{kwargs}"
        async_to_sync(self.channel_layer.group_add)(
            str(channel_name),
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            'events',
            self.channel_name
        )
        self.close()

    def events_alarm(self, event):
        self.send_json(
            {
                'type': 'events.alarm',
                'content': event['content']
            }
        )

    def events_update(self, event):
        self.send_json(
            {
                'type': 'events.update',
                'content': event['content']
            }
        )


class EventDevicePingError(JsonWebsocketConsumer):

    def connect(self):
        kwargs = self.scope["url_route"]["kwargs"]["cluster_id"]
        if not kwargs:
            self.disconnect(0)

        if type(kwargs) != int:
            self.disconnect(0)

        qv_cluster = Cluster.custom_manager.alive().filter(id=kwargs)
        if not qv_cluster.exists():
            self.disconnect(0)

        channel_name = f"device-ping-alert-{kwargs}"
        async_to_sync(self.channel_layer.group_add)(
            str(channel_name),
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            'events',
            self.channel_name
        )
        self.close()

    def events_alarm(self, event):
        self.send_json(
            {
                'type': 'events.alarm',
                'content': event['content']
            }
        )

    def events_update(self, event):
        self.send_json(
            {
                'type': 'events.update',
                'content': event['content']
            }
        )


class CustomClusterRoleAlert(JsonWebsocketConsumer):

    def connect(self):
        kwargs = self.scope["url_route"]["kwargs"]["user_id"]
        if not kwargs:
            self.disconnect(0)


        qv_user = UserModel.custom_manager.alive().filter(id=kwargs)
        if not qv_user.exists():
            self.disconnect(0)

        channel_name = f"cluster-role-alert-{kwargs}"
        async_to_sync(self.channel_layer.group_add)(
            str(channel_name),
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            'events',
            self.channel_name
        )
        self.close()

    def events_alarm(self, event):
        self.send_json(
            {
                'type': 'events.alarm',
                'content': event['content']
            }
        )

    def events_update(self, event):
        self.send_json(
            {
                'type': 'events.update',
                'content': event['content']
            }
        )