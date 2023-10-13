from .views import MachineApi, MachineModelApi
from django.urls import path


MAIN_PATH = 'machines'

app_name = 'machines'

urlpatterns = [
    # Machines
    # url path for machines api view
    path(MAIN_PATH, MachineApi.as_view(), name='machines-list'),
    # url path for machine models api view
    path(MAIN_PATH+'/models', MachineModelApi.as_view(), name='machine-models'),
]
