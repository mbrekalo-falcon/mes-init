from django.urls import path

from .views import (
    DeviceApi, DeviceModelApi, DeviceCommandApi, DeviceFirmwareApi, 
    DeviceCommandRequestApi, DeviceCommandResponseApi, DevicePingApi
)

MAIN_PATH = 'devices'

app_name = 'devices'

urlpatterns = [
    # Devices
    # url path for device api view
    path(MAIN_PATH, DeviceApi.as_view(), name='devices-list'),
    # url path for device model api view
    path(MAIN_PATH+'/device-models', DeviceModelApi.as_view(), name='device-models'),
    # url path for device command api view
    path(MAIN_PATH+'/device-commands', DeviceCommandApi.as_view(), name='device-commands'),
    # url path for device firmware api view
    path(MAIN_PATH+'/device-firmwares', DeviceFirmwareApi.as_view(), name='device-firmwares'),
    # url path for device command requests api view
    path(MAIN_PATH+'/device-command-requests', DeviceCommandRequestApi.as_view(), name='device-command-requests'),
    # url path for device command responses api view
    path(MAIN_PATH+'/device-command-responses', DeviceCommandResponseApi.as_view(), name='device-command-responses'),
    # url path for device ping api view
    path(MAIN_PATH + '/device-ping', DevicePingApi.as_view(), name='device-ping')

]
