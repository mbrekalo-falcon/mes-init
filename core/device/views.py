from core.__init__ import *
from core.device.serializers import (
    DeviceModelSerializer, DeviceSerializer, DeviceCommandSerializer, DeviceFirmwareSerializer,
    DeviceCommandRequestSerializer, DeviceCommandResponseSerializer, DevicePingSerializer
)
from models.device.models import (
    DeviceModel, Device, DeviceCommand, DeviceFirmware, DeviceCommandRequest, DeviceCommandResponse, DevicePing
)


class DeviceModelApi(
    generics.ListAPIView,
    generics.CreateAPIView,
    generics.UpdateAPIView,
    generics.DestroyAPIView,
):
    """CRUD Api for DeviceModel model

            Params:
                - row_size: how many results to show default is 100
                - instance_id: 1 returns object ID
                - search_name: search by device model name
    """
    queryset = DeviceModel.objects.all()
    serializer_class = DeviceModelSerializer
    pagination_class = StandardApplicationSetPagination
    filter_backends = (DjangoFilterBackend, )
    filter_fields = ('name', )
    permission_classes = (IsAuthenticated, )
    lookup_url_kwarg = ('instance_id', )
    
    def list(self, request, *args, **kwargs):
        response = super(DeviceModelApi, self).list(request, *args, **kwargs)
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
            queryset = queryset.filter(name__icontains=search_name)

        return queryset
    
    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return rest_default_response(data=serializer.data, status=status.HTTP_201_CREATED)
        return rest_default_response(message=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        instance_id = self.request.GET.get('instance_id')
        if not instance_id:
            return rest_default_response(status=status.HTTP_403_FORBIDDEN, message='Please provide instance_id.')
        check_query = self.get_queryset().filter(id=instance_id)
        if not check_query.exists():
            return rest_default_response(status=status.HTTP_404_NOT_FOUND, message='Object not found')
        
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
        
        check_query.first().delete()
        return rest_default_response(status=status.HTTP_200_OK, message='Object deleted.')


class DeviceApi(
    generics.ListAPIView,
    generics.CreateAPIView,
    generics.UpdateAPIView,
    generics.DestroyAPIView
):
    """CRUD Api for Device model

            Params:
                - row_size: how many results to show default is 100
                - instance_id: 1 returns object ID
                - search_name: search device by name
    """
    queryset = (
        Device.custom_manager.alive()
    )
    serializer_class = DeviceSerializer
    pagination_class = StandardApplicationSetPagination
    filter_backends = (DjangoFilterBackend, )
    filter_fields = ('name', )
    permission_classes = (IsAuthenticated,)
    
    lookup_url_kwarg = ('instance_id', )

    def list(self, request, *args, **kwargs):
        response = super(DeviceApi, self).list(request, *args, **kwargs)
        check = dict(response.data)
        if check['count'] == 0:
            return rest_default_response(data=None, status=status.HTTP_404_NOT_FOUND)
        return rest_default_response(data=response.data, status=status.HTTP_200_OK)

    def filter_queryset(self, queryset):
        row_size = self.request.GET.get('row_size')
        search_name = self.request.GET.get('search_name')
        instance_id = self.request.GET.get('instance_id')
        cluster_id = self.request.GET.get('cluster_id')
        queryset = self.queryset

        if row_size:
            self.pagination_class.page_size = row_size

        if instance_id:
            queryset = queryset.filter(id=instance_id)

        if cluster_id:
            queryset = queryset.filter(cluster_id=cluster_id)

        if search_name:
            queryset = queryset.filter(name__icontains=search_name)

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


class DeviceCommandApi(
    generics.ListAPIView,
    generics.CreateAPIView,
    generics.UpdateAPIView,
    generics.DestroyAPIView
):
    """CRUD Api for DeviceCommand model

            Params:
                - row_size: how many results to show default is 100
                - instance_id: 1 returns object ID
                - search_name: search device command by name
    """
    queryset = (
        DeviceCommand.objects.get_queryset()
    )
    serializer_class = DeviceCommandSerializer
    pagination_class = StandardApplicationSetPagination
    filter_backends = (DjangoFilterBackend, )
    filter_fields = ('name', )
    permission_classes = (IsAuthenticated,)
    
    lookup_url_kwarg = ('instance_id', )

    def list(self, request, *args, **kwargs):
        response = super(DeviceCommandApi, self).list(request, *args, **kwargs)
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
            queryset = queryset.filter(name__icontains=search_name)

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

        check_query.first().delete()
        return rest_default_response(status=status.HTTP_200_OK, message='Object deleted.')


class DeviceFirmwareApi(
    generics.ListAPIView,
    generics.CreateAPIView,
    generics.UpdateAPIView,
    generics.DestroyAPIView
):
    """CRUD Api for DeviceFirmware model

            Params:
                - row_size: how many results to show default is 100
                - instance_id: 1 returns object ID
                - search_name: search firmware by device_model_name or firmware_version
    """
    queryset = (
        DeviceFirmware.objects.get_queryset()
    )
    serializer_class = DeviceFirmwareSerializer
    pagination_class = StandardApplicationSetPagination
    filter_backends = (DjangoFilterBackend, )
    filter_fields = ('device_model__name', )
    permission_classes = (IsAuthenticated,)
    
    lookup_url_kwarg = ('instance_id', )

    def list(self, request, *args, **kwargs):
        response = super(DeviceFirmwareApi, self).list(request, *args, **kwargs)
        check = dict(response.data)
        if check['count'] == 0:
            return rest_default_response(data=None, status=status.HTTP_404_NOT_FOUND)
        return rest_default_response(data=response.data, status=status.HTTP_200_OK)

    def filter_queryset(self, queryset):
        row_size = self.request.GET.get('row_size')
        search_name = self.request.GET.get('search_name')
        instance_id = self.request.GET.get('instance_id')
        queryset = self.queryset.select_related('device_model')

        if row_size:
            self.pagination_class.page_size = row_size

        if instance_id:
            queryset = queryset.filter(id=instance_id)

        if search_name:
            queryset = queryset.filter(
                Q(device_model__name__icontains=search_name) |
                Q(firmware_version__icontains=search_name)
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

        check_query.first().delete()
        return rest_default_response(status=status.HTTP_200_OK, message='Object deleted.')


class DeviceCommandRequestApi(
    generics.ListAPIView,
    generics.CreateAPIView,
    generics.UpdateAPIView,
    generics.DestroyAPIView
):
    """CRUD Api for DeviceCommandRequest model

            Params:
                - row_size: how many results to show default is 100
                - instance_id: 1 returns object ID
                - search_name: search device command reqest by device_name
    """
    queryset = (
        DeviceCommandRequest.custom_manager.alive()
    )
    serializer_class = DeviceCommandRequestSerializer
    pagination_class = StandardApplicationSetPagination
    filter_backends = (DjangoFilterBackend, )
    filter_fields = ('device__name', )
    permission_classes = (IsAuthenticated,)
    
    lookup_url_kwarg = ('instance_id', )

    def list(self, request, *args, **kwargs):
        response = super(DeviceCommandRequestApi, self).list(request, *args, **kwargs)
        check = dict(response.data)
        if check['count'] == 0:
            return rest_default_response(data=None, status=status.HTTP_404_NOT_FOUND)
        return rest_default_response(data=response.data, status=status.HTTP_200_OK)

    def filter_queryset(self, queryset):
        row_size = self.request.GET.get('row_size')
        search_name = self.request.GET.get('search_name')
        instance_id = self.request.GET.get('instance_id')
        device_id = self.request.GET.get('device_id')
        queryset = self.queryset.order_by('-created_at')

        if row_size:
            self.pagination_class.page_size = row_size

        if device_id:
            queryset = queryset.filter(device_id=device_id)

        if instance_id:
            queryset = queryset.filter(id=instance_id)

        if search_name:
            queryset = queryset.filter(device__name__icontains=search_name)

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


class DeviceCommandResponseApi(
    generics.ListAPIView,
    generics.CreateAPIView,
    generics.UpdateAPIView,
    generics.DestroyAPIView
):
    """CRUD Api for DeviceCommandRespons model

            Params:
                - row_size: how many results to show default is 100
                - instance_id: 1 returns object ID
                - search_name: search firmware by device_name
    """
    queryset = (
        DeviceCommandResponse.custom_manager.alive()
    )
    serializer_class = DeviceCommandResponseSerializer
    pagination_class = StandardApplicationSetPagination
    filter_backends = (DjangoFilterBackend, )
    filter_fields = ('device_command_request__device__name', )
    permission_classes = (IsAuthenticated,)
    
    lookup_url_kwarg = ('instance_id', )

    def list(self, request, *args, **kwargs):
        response = super(DeviceCommandResponseApi, self).list(request, *args, **kwargs)
        check = dict(response.data)
        if check['count'] == 0:
            return rest_default_response(data=None, status=status.HTTP_404_NOT_FOUND)
        return rest_default_response(data=response.data, status=status.HTTP_200_OK)

    def filter_queryset(self, queryset):
        row_size = self.request.GET.get('row_size')
        search_name = self.request.GET.get('search_name')
        instance_id = self.request.GET.get('instance_id')
        queryset = self.queryset.select_related('device_command_request__device')

        if row_size:
            self.pagination_class.page_size = row_size

        if instance_id:
            queryset = queryset.filter(id=instance_id)

        if search_name:
            queryset = queryset.filter(device_command_request__device__name__icontains=search_name)

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


class DevicePingApi(generics.ListAPIView):

    queryset = (
        DevicePing.custom_manager.alive()
    )
    serializer_class = DevicePingSerializer
    pagination_class = StandardApplicationSetPagination
    filter_backends = (DjangoFilterBackend, )
    filter_fields = ('device_id', )
    permission_classes = (IsAuthenticated,)
    
    lookup_url_kwarg = ('cluster_id', )

    def list(self, request, *args, **kwargs):
        response = super(DevicePingApi, self).list(request, *args, **kwargs)
        check = dict(response.data)
        if check['count'] == 0:
            return rest_default_response(data=None, status=status.HTTP_404_NOT_FOUND)
        return rest_default_response(data=response.data, status=status.HTTP_200_OK)

    def filter_queryset(self, queryset):
        row_size = self.request.GET.get('row_size')
        instance_id = self.request.GET.get('instance_id')
        cluster_id = self.request.GET.get('cluster_id')
        device_id = self.request.GET.get('device_id')
        status_id = self.request.GET.get('status_id')
        queryset = self.queryset.select_related('device')

        if row_size:
            self.pagination_class.page_size = row_size

        if instance_id:
            queryset = queryset.filter(id=instance_id)

        if cluster_id:
            queryset = queryset.filter(device__cluster_id=cluster_id)

        if device_id:
            queryset = queryset.filter(device_id=device_id)

        if status_id:
            queryset = queryset.filter(device_ping_status_id=status_id)

        return queryset
