from django.urls import re_path

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
from core.web_sockets.views import (
    CustomClusterRoleAlert, EventDeviceResponse, EventDevicePingError)

websockets = URLRouter([
    re_path(
        r"ws/device-command-responses/(?P<device_identifier>.*)/.*",
        EventDeviceResponse,
        name="device-command-responses"
    ),
    re_path(
        r"ws/device-ping/(?P<cluster_id>.*)/.*",
        EventDevicePingError,
        name="event-device-ping-error"
    ),
    re_path(
        r"ws/cluster-role-alert/(?P<user_id>.*)/.*",
        CustomClusterRoleAlert,
        name="event-custom-cluster-role-alert"
    ),
])

application = ProtocolTypeRouter({
    "websocket": AuthMiddlewareStack(websockets),
})
