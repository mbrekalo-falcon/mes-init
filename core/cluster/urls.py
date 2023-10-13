from django.urls import path

from .views import (
    ClusterApi, ClusterUserApi, UserApplicationRoleApi,
    ApplicationModuleClusterRolePermissionApi, ClusterMachineDeviceApi,
    ClusterRoleView
)

MAIN_PATH = 'clusters'

app_name = 'clusters'

urlpatterns = [
    # Clusters
    # url path for clusters api view
    path(MAIN_PATH, ClusterApi.as_view(), name='clusters-list'),
    # url path for clusters users api view
    path(MAIN_PATH+'/users', ClusterUserApi.as_view(), name='clusters-users'),
    # url path for clusters user roles api view 
    path(MAIN_PATH+'/user-roles', UserApplicationRoleApi.as_view(), name='user-roles'),
    # url path for clusters user module permissions api view
    path(MAIN_PATH+'/cluster-role-module-permissions', ApplicationModuleClusterRolePermissionApi.as_view(), name='cluster-user-module-permissions'),
    # url path for clusters machine devices api view
    path(MAIN_PATH+'/machine-devices', ClusterMachineDeviceApi.as_view(), name='machine-devices'),
    # url to ClusterRoleView
    path(MAIN_PATH+'/cluster-role', ClusterRoleView.as_view(), name='cluster-role'),
]
