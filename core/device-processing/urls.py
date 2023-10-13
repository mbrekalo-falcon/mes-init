from django.urls import path

from .views import (DeviceApi,
                    DeviceCommandRequestApi,
                    DeviceCommandResponseApi,
                    DevicePingApi,
                    DeviceCurrentFirmwareApi,
                    MachineDomainApi
                    )

MAIN_PATH = ''

app_name = 'device-processing'

urlpatterns = [
    # device-processing
    # url path for device api view
    path(MAIN_PATH+'device/<identifier>', DeviceApi.as_view(), name='device'),
    # url path for device request commands
    path(MAIN_PATH+'command-requests/<identifier>', DeviceCommandRequestApi.as_view(), name='request-commands'),
    # url path for device response commands
    path(MAIN_PATH+'command-responses/<identifier>', DeviceCommandResponseApi.as_view(), name='response-commands'),
    # url path for device ping api view
    path(MAIN_PATH + 'device-ping', DevicePingApi.as_view(), name='device-ping'),
    # url path for current device firmware
    path(MAIN_PATH + 'firmware/<identifier>', DeviceCurrentFirmwareApi.as_view(), name='device-firmware'),
    # url path for printing slip after process is done
    path(MAIN_PATH + 'domain/<identifier>', MachineDomainApi.as_view(), name='machine-domain'),
]
