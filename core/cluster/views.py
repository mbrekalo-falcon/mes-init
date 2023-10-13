from django.core.exceptions import ObjectDoesNotExist

from core.__init__ import *
from core.cluster.serializers import (
    ClusterRoleAlertSerializer, ClusterSerializer, ClusterUserSerializer, ClusterMachineDeviceSerializer,
    ApplicationModuleClusterRolePermissionSerializer, ClusterRoleSerializer, UserApplicationRoleSerializer
)
from core.helpers.alerts import SYSTEM_ALERT_MESSAGES
from models.cluster.models import (
    Cluster, ClusterRoleAlert, ClusterUser, ClusterMachineDevice, UserApplicationRole, ApplicationModuleClusterRolePermission,
    ClusterRole
)
from models.user.models import UserModel


class ClusterApi(
    generics.ListAPIView,
    generics.CreateAPIView,
    generics.UpdateAPIView,
    generics.DestroyAPIView
):
    """CRUD Api for Cluster model

            Params:
                - row_size: how many results to show default is 100
                - instance_id: 1 returns object ID
                - search_name: search user by name or email
    """
    queryset = (
        Cluster.custom_manager.alive().order_by('external_cluster_id')
    )
    serializer_class = ClusterSerializer
    pagination_class = StandardApplicationSetPagination
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('name',)
    permission_classes = (IsAuthenticated,)
    lookup_url_kwarg = ('instance_id',)

    def list(self, request, *args, **kwargs):
        response = super(ClusterApi, self).list(request, *args, **kwargs)
        check = dict(response.data)
        if check['count'] == 0:
            return rest_default_response(data=None, status=status.HTTP_404_NOT_FOUND)
        return rest_default_response(data=response.data, status=status.HTTP_200_OK)

    def filter_queryset(self, queryset):
        row_size = self.request.GET.get('row_size')
        search_name = self.request.GET.get('search_name')
        instance_id = self.request.GET.get('instance_id')
        queryset = self.queryset

        if row_size:
            self.pagination_class.page_size = row_size

        if instance_id:
            queryset = queryset.filter(id=instance_id)

        if search_name:
            queryset = queryset.filter(
                Q(name__icontains=search_name) |
                Q(email__icontains=search_name)
            )

        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return rest_default_response(data=serializer.data, status=status.HTTP_200_OK)
        return rest_default_response(message=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        instance_id = self.request.GET.get('instance_id')
        if not instance_id:
            return rest_default_response(status=status.HTTP_403_FORBIDDEN, message='Please provide instance_id.')
        check_query = self.get_queryset().filter(id=instance_id)
        if not check_query.exists():
            return rest_default_response(status=status.HTTP_404_NOT_FOUND, message='Object not found.')

        serializer = self.serializer_class(
            data=self.request.data,
            instance=check_query.first(),
            partial=True
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return rest_default_response(data=serializer.data, status=status.HTTP_200_OK)
        return rest_default_response(message=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance_id = self.request.GET.get('instance_id')
        if not instance_id:
            return rest_default_response(status=status.HTTP_403_FORBIDDEN, message='Please provide instance_id.')
        check_query = self.get_queryset().filter(id=instance_id)
        if not check_query.exists():
            return rest_default_response(status=status.HTTP_404_NOT_FOUND, message='Object not found.')

        check_query.first().soft_delete()
        return rest_default_response(status=status.HTTP_200_OK, message='Object deleted.')


class ClusterUserApi(
    generics.ListAPIView,
    generics.CreateAPIView,
    generics.UpdateAPIView,
    generics.DestroyAPIView
):
    """CRUD API for ClusterUser model

        Params:
            - row_size: how many results to show default is 100
            - instance_id: 1 returns object ID
            - search_name: search user by user_full_name or user_email
    """
    queryset = ClusterUser.custom_manager.alive()

    serializer_class = ClusterUserSerializer
    pagination_class = StandardApplicationSetPagination
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('user__full_name', 'user_id', )
    permission_classes = (IsAuthenticated,)
    lookup_url_kwarg = ('instance_id',)

    def list(self, request, *args, **kwargs):
        response = super(ClusterUserApi, self).list(request, *args, **kwargs)
        check = dict(response.data)
        if check['count'] == 0:
            return rest_default_response(data=None, status=status.HTTP_404_NOT_FOUND)
        return rest_default_response(data=response.data, status=status.HTTP_200_OK)

    def filter_queryset(self, queryset):
        row_size = self.request.GET.get('row_size')
        search_name = self.request.GET.get('search_name')
        user_id = self.request.GET.get('user_id')
        instance_id = self.request.GET.get('instance_id')
        cluster_id = self.request.GET.get('cluster_id')
        queryset = self.queryset

        if row_size:
            self.pagination_class.page_size = row_size

        if instance_id:
            queryset = queryset.filter(id=instance_id)

        if user_id:
            queryset = queryset.filter(user_id=user_id)

        if search_name:
            queryset = queryset.filter(
                Q(user__full_name__icontains=search_name) |
                Q(user__email__icontains=search_name)
            )

        if cluster_id:
            queryset = queryset.filter(cluster_id=cluster_id)

        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return rest_default_response(data=serializer.data, status=status.HTTP_200_OK)
        return rest_default_response(message=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        instance_id = self.request.GET.get('instance_id')
        if not instance_id:
            return rest_default_response(status=status.HTTP_403_FORBIDDEN, message='Please provide instance_id.')
        check_query = self.get_queryset().filter(id=instance_id)
        if not check_query.exists():
            return rest_default_response(status.HTTP_404_NOT_FOUND, message='Object not found')

        serializer = self.serializer_class(
            data=self.request.data,
            instance=check_query.first(),
            partial=True
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return rest_default_response(data=serializer.data, status=status.HTTP_200_OK)
        return rest_default_response(message=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance_id = self.request.GET.get('instance_id')
        if not instance_id:
            return rest_default_response(status=status.HTTP_403_FORBIDDEN, message='Please provide instance_id.')
        check_query = self.get_queryset().filter(id=instance_id)
        if not check_query.exists():
            return rest_default_response(status.HTTP_404_NOT_FOUND, message='Object not found')

        check_query.first().hard_delete()
        return rest_default_response(status=status.HTTP_200_OK, message='Object deleted.')


class UserApplicationRoleApi(
    generics.ListAPIView,
    generics.CreateAPIView,
    generics.UpdateAPIView,
    generics.DestroyAPIView
):
    """CRUD Api for ClusterUserRole model

        Params:
            - row_size: how many results to show default is 100
            - instance_id: 1 returns object ID
            - search_name: search user by user_full_name, cluster_user_email or application_role_name
    """
    queryset = (
        UserApplicationRole.custom_manager.alive()
    )
    serializer_class = UserApplicationRoleSerializer
    pagination_class = StandardApplicationSetPagination
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('user__full_name',)
    permission_classes = (IsAuthenticated,)
    lookup_url_kwarg = ('instance_id',)

    def list(self, request, *args, **kwargs):
        response = super(UserApplicationRoleApi, self).list(request, *args, **kwargs)
        check = dict(response.data)
        if check['count'] == 0:
            return rest_default_response(data=None, status=status.HTTP_404_NOT_FOUND)
        return rest_default_response(data=response.data, status=status.HTTP_200_OK)

    def filter_queryset(self, queryset):
        row_size = self.request.GET.get('row_size')
        search_name = self.request.GET.get('search_name')
        instance_id = self.request.GET.get('instance_id')
        user_id = self.request.GET.get('user_id')
        queryset = self.queryset

        if row_size:
            self.pagination_class.page_size = row_size

        if instance_id:
            queryset = queryset.filter(id=instance_id)

        if search_name:
            queryset = queryset.filter(
                Q(user__full_name__icontains=search_name) |
                Q(user__email__icontains=search_name) |
                Q(cluster_role__application_role__name__icontains=search_name)
            )

        if user_id:
            queryset = queryset.filter(user_id=user_id)

        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return rest_default_response(data=serializer.data, status=status.HTTP_200_OK)
        return rest_default_response(message=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        instance_id = self.request.GET.get('instance_id')
        if not instance_id:
            return rest_default_response(status=status.HTTP_403_FORBIDDEN, message='Please provide instance_id.')
        check_query = self.get_queryset().filter(id=instance_id)
        if not check_query.exists():
            return rest_default_response(status=status.HTTP_404_NOT_FOUND, message='Object not found.')

        serializer = self.serializer_class(
            data=self.request.data,
            instance=check_query.first(),
            partial=True
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return rest_default_response(data=serializer.data, status=status.HTTP_200_OK)
        return rest_default_response(message=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance_id = self.request.GET.get('instance_id')
        if not instance_id:
            return rest_default_response(status=status.HTTP_403_FORBIDDEN, message='Please provide instance_id.')

        check_query = self.get_queryset().filter(id=instance_id)
        if not check_query.exists():
            return rest_default_response(status=status.HTTP_404_NOT_FOUND, message='Object not found.')

        check_query.first().hard_delete()
        return rest_default_response(status=status.HTTP_200_OK, message='Object deleted.')


class ApplicationModuleClusterRolePermissionApi(
    generics.ListAPIView,
    generics.CreateAPIView,
    generics.UpdateAPIView,
    generics.DestroyAPIView
):
    """Api for ClusterUserModulePermission model
    """
    queryset = (
        ApplicationModuleClusterRolePermission.custom_manager.alive()
    )
    serializer_class = ApplicationModuleClusterRolePermissionSerializer
    pagination_class = StandardApplicationSetPagination
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('application_module__name', 'cluster_role__id')
    permission_classes = (IsAuthenticated,)
    lookup_url_kwarg = ('instance_id',)

    def list(self, request, *args, **kwargs):
        response = super(ApplicationModuleClusterRolePermissionApi, self).list(request, *args, **kwargs)
        check = dict(response.data)
        if check['count'] == 0:
            return rest_default_response(data=None, status=status.HTTP_404_NOT_FOUND)
        return rest_default_response(data=response.data, status=status.HTTP_200_OK)

    def filter_queryset(self, queryset):
        row_size = self.request.GET.get('row_size')
        search_module = self.request.GET.get('search_module')
        search_role = self.request.GET.get('search_role')
        instance_id = self.request.GET.get('instance_id')
        cluster_role_id = self.request.GET.get('cluster_role_id')

        queryset = self.queryset

        if row_size:
            self.pagination_class.page_size = row_size

        if cluster_role_id:
            queryset = queryset.filter(cluster_role_id=cluster_role_id)

        if instance_id:
            queryset = queryset.filter(id=instance_id)

        if search_module:
            queryset = queryset.filter(application_module__name__icontains=search_module)

        if search_role:
            queryset = queryset.filter(cluster_role__application_role__name__icontains=search_role)

        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return rest_default_response(data=serializer.data, status=status.HTTP_200_OK)
        return rest_default_response(message=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        instance_id = self.request.GET.get('instance_id')
        if not instance_id:
            return rest_default_response(status=status.HTTP_403_FORBIDDEN, message='Please provide instance_id.')
        check_query = self.get_queryset().filter(id=instance_id)
        if not check_query.exists():
            return rest_default_response(status=status.HTTP_404_NOT_FOUND, message='Object not found.')

        serializer = self.serializer_class(
            data=self.request.data,
            instance=check_query.first(),
            partial=True
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return rest_default_response(data=serializer.data, status=status.HTTP_200_OK)
        return rest_default_response(message=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance_id = self.request.GET.get('instance_id')
        if not instance_id:
            return rest_default_response(status=status.HTTP_403_FORBIDDEN, message='Please provide instance_id.')
        check_query = self.get_queryset().filter(id=instance_id)
        if not check_query.exists():
            return rest_default_response(status=status.HTTP_404_NOT_FOUND, message='Object not found.')

        check_query.first().hard_delete()
        return rest_default_response(status=status.HTTP_200_OK, message='Object deleted.')


class ClusterMachineDeviceApi(
    generics.ListAPIView,
    generics.CreateAPIView,
    generics.UpdateAPIView,
    generics.DestroyAPIView
):
    """Api for ClusterMachineDevice model
     
        Params:
            - row_size: how many results to show default is 100
            - instance_id: 1 returns object ID
            - search_machine_name: search machine name by machine_name
            - search_cluster_name: search cluster name by cluster_name
            - search_device_name: search device name by device_name
            - search_printer_name: search printer name by printer_name
    """
    queryset = (
        ClusterMachineDevice.custom_manager.alive()
    )
    serializer_class = ClusterMachineDeviceSerializer
    pagination_class = StandardApplicationSetPagination
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('cluster',)
    permission_classes = (IsAuthenticated,)
    lookup_url_kwarg = ('instance_id',)

    def list(self, request, *args, **kwargs):
        response = super(ClusterMachineDeviceApi, self).list(request, *args, **kwargs)
        check = dict(response.data)
        if check['count'] == 0:
            return rest_default_response(data=None, status=status.HTTP_404_NOT_FOUND)
        return rest_default_response(data=response.data, status=status.HTTP_200_OK)

    def filter_queryset(self, queryset):
        row_size = self.request.GET.get('row_size')
        search_name = self.request.GET.get('search_name')
        instance_id = self.request.GET.get('instance_id')
        cluster_id = self.request.GET.get('cluster_id')

        if not cluster_id:
            return []

        queryset = self.queryset.filter(cluster_id=cluster_id).order_by('machine__name')

        if row_size:
            self.pagination_class.page_size = row_size

        if instance_id:
            queryset = queryset.filter(id=instance_id)

        else:
            queryset = queryset.filter(machine__isnull=False)

        if search_name:
            queryset = queryset.filter(
                Q(machine__name__icontains=search_name) |
                Q(device__name__icontains=search_name) 

            )
        return queryset

    def create(self, request, *args, **kwargs):

        old_cmd = ClusterMachineDevice.custom_manager.dead().filter(
            cluster=request.data['cluster'],
            machine=request.data['machine'],
            device=request.data['device']
        )
        if old_cmd.exists():
            serializer = self.serializer_class(
                data=self.request.data,
                instance=old_cmd.first(),
                partial=True
            )
            if serializer.is_valid(raise_exception=True):
                serializer.save()

                return rest_default_response(data=serializer.data, status=status.HTTP_200_OK)
            return rest_default_response(message=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(data=self.request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return rest_default_response(data=serializer.data, status=status.HTTP_200_OK)
        return rest_default_response(message=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        instance_id = self.request.GET.get('instance_id')
        if not instance_id:
            return rest_default_response(status=status.HTTP_403_FORBIDDEN, message='Please provide instance_id.')
        check_query = self.get_queryset().filter(id=instance_id)
        if not check_query.exists():
            return rest_default_response(status=status.HTTP_404_NOT_FOUND, message='Object not found.')

        serializer = self.serializer_class(
            data=self.request.data,
            instance=check_query.first(),
            partial=True
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return rest_default_response(data=serializer.data, status=status.HTTP_200_OK)
        return rest_default_response(message=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance_id = self.request.GET.get('instance_id')
        if not instance_id:
            return rest_default_response(status=status.HTTP_403_FORBIDDEN, message='Please provide instance_id.')
        check_query = self.get_queryset().filter(id=instance_id)
        if not check_query.exists():
            return rest_default_response(status=status.HTTP_404_NOT_FOUND, message='Object not found.')

        check_query.first().soft_delete()
        return rest_default_response(status=status.HTTP_200_OK, message='Object deleted.')


class ClusterRoleView(
    generics.ListAPIView,
    generics.CreateAPIView,
    generics.UpdateAPIView,
    generics.DestroyAPIView
):
    """
        Api for ClusterRoleView model
    """
    queryset = (
        ClusterRole.custom_manager.alive()
    )
    serializer_class = ClusterRoleSerializer
    pagination_class = StandardApplicationSetPagination
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('cluster__name', )
    permission_classes = (IsAuthenticated,)
    lookup_url_kwarg = ('instance_id',)

    def list(self, request, *args, **kwargs):
        response = super(ClusterRoleView, self).list(request, *args, **kwargs)
        check = dict(response.data)
        if check['count'] == 0:
            return rest_default_response(data=None, status=status.HTTP_404_NOT_FOUND)
        return rest_default_response(data=response.data, status=status.HTTP_200_OK)

    def filter_queryset(self, queryset):
        row_size = self.request.GET.get('row_size')
        search_module = self.request.GET.get('search_module')
        search_role = self.request.GET.get('search_role')
        instance_id = self.request.GET.get('instance_id')
        cluster_id = self.request.GET.get('cluster_id')
        queryset = self.queryset

        if row_size:
            self.pagination_class.page_size = row_size

        if cluster_id:
            queryset = queryset.filter(cluster_id=cluster_id)

        if instance_id:
            queryset = queryset.filter(id=instance_id)

        if search_module:
            queryset = queryset.filter(application_role__name__icontains=search_module)

        if search_role:
            queryset = queryset.filter(application_role__name__icontains=search_role)

        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return rest_default_response(data=serializer.data, status=status.HTTP_200_OK)
        return rest_default_response(message=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        instance_id = self.request.GET.get('instance_id')
        if not instance_id:
            return rest_default_response(status=status.HTTP_403_FORBIDDEN,
                                         message='Please provide instance_id.')
        check_query = self.get_queryset().filter(id=instance_id)
        if not check_query.exists():
            return rest_default_response(status=status.HTTP_404_NOT_FOUND, message='Object not found.')

        serializer = self.serializer_class(
            data=self.request.data,
            instance=check_query.first(),
            partial=True
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return rest_default_response(data=serializer.data, status=status.HTTP_200_OK)
        return rest_default_response(message=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance_id = self.request.GET.get('instance_id')
        if not instance_id:
            return rest_default_response(status=status.HTTP_403_FORBIDDEN,
                                         message='Please provide instance_id.')
        check_query = self.get_queryset().filter(id=instance_id)
        if not check_query.exists():
            return rest_default_response(status=status.HTTP_404_NOT_FOUND, message='Object not found.')

        check_query.first().hard_delete()
        return rest_default_response(status=status.HTTP_200_OK, message='Object deleted.')
    

class ClusterRoleAlertView(
    generics.ListAPIView,
    generics.CreateAPIView,
    generics.UpdateAPIView,
    generics.DestroyAPIView
):
    """CRUD Api for ClusterRoleAlert model

            Params:
                - row_size: how many results to show default is 100
    """
    queryset = (
        ClusterRoleAlert.custom_manager.alive()
    )
    serializer_class = ClusterRoleAlertSerializer
    pagination_class = StandardApplicationSetPagination
    filter_backends = (DjangoFilterBackend,)
    permission_classes = (IsAuthenticated,)
    lookup_url_kwarg = ('instance_id',)

    def list(self, request, *args, **kwargs):
        response = super(ClusterRoleAlertView, self).list(request, *args, **kwargs)
        check = dict(response.data)
        if check['count'] == 0:
            return rest_default_response(data=None, status=status.HTTP_404_NOT_FOUND)
        response.data["templates"] = SYSTEM_ALERT_MESSAGES
        return rest_default_response(data=response.data, status=status.HTTP_200_OK)

    def filter_queryset(self, queryset):
        row_size = self.request.GET.get('row_size')
        instance_id = self.request.GET.get('instance_id')
        user_id = self.request.GET.get('user_id')
        queryset = self.queryset.order_by('-created_at')

        if row_size:
            self.pagination_class.page_size = row_size

        if instance_id:
            queryset = queryset.filter(id=instance_id)

        if user_id:
            superuser = UserModel.custom_manager.alive().filter(is_superuser=True, id=user_id)
            if not superuser.exists():
                q_ar = UserApplicationRole.custom_manager.alive().filter(user_id=user_id)
                if q_ar.exists():
                    cluster_ids = []
                    role_ids = []
                    for ar in q_ar:
                        cluster_ids.append(ar.cluster_role.cluster_id)
                        role_ids.append(ar.cluster_role.application_role_id)
                    if cluster_ids:
                        queryset = queryset.filter(Q(cluster_id__in=cluster_ids) | Q(cluster_id__isnull=True))
                    if role_ids:
                        queryset = queryset.filter(Q(application_role_id__in=role_ids) | Q(application_role_id__isnull=True))
                else:
                    queryset = []

        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return rest_default_response(data=serializer.data, status=status.HTTP_200_OK)
        return rest_default_response(message=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        instance_id = self.request.GET.get('instance_id')
        if not instance_id:
            return rest_default_response(status=status.HTTP_403_FORBIDDEN, message='Please provide instance_id.')
        check_query = self.get_queryset().filter(id=instance_id)
        if not check_query.exists():
            return rest_default_response(status=status.HTTP_404_NOT_FOUND, message='Object not found.')

        serializer = self.serializer_class(
            data=self.request.data,
            instance=check_query.first(),
            partial=True
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return rest_default_response(data=serializer.data, status=status.HTTP_200_OK)
        return rest_default_response(message=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance_id = self.request.GET.get('instance_id')
        if not instance_id:
            return rest_default_response(status=status.HTTP_403_FORBIDDEN, message='Please provide instance_id.')
        check_query = self.get_queryset().filter(id=instance_id)
        if not check_query.exists():
            return rest_default_response(status=status.HTTP_404_NOT_FOUND, message='Object not found.')

        check_query.first().soft_delete()
        return rest_default_response(status=status.HTTP_200_OK, message='Object deleted.')