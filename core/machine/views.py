from core.__init__ import *
from core.machine.serializers import MachineModelSerializer, MachineSerializer
from models.machine.models import MachineModel, Machine
from models.cluster.models import Cluster
from django.db.models import F

class MachineModelApi(
    generics.ListAPIView,
    generics.CreateAPIView,
    generics.UpdateAPIView,
    generics.DestroyAPIView,
):
    """CRUD Api for MachineModel model

            Params:
                - row_size: how many results to show default is 100
                - instance_id: 1 returns object ID
                - search_name: search by name
    """
    queryset = MachineModel.objects.all()
    serializer_class = MachineModelSerializer
    pagination_class = StandardApplicationSetPagination
    filter_backends = (DjangoFilterBackend, )
    filter_fields = ('name', )
    permission_classes = (IsAuthenticated, )
    
    lookup_url_kwarg = ('instance_id', )
    
    def list(self, request, *args, **kwargs):
        response = super(MachineModelApi, self).list(request, *args, **kwargs)
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


class MachineApi(
    generics.ListAPIView,
    generics.CreateAPIView,
    generics.UpdateAPIView,
    generics.DestroyAPIView
):
    """CRUD Api for Machine Model
    
            Params:
            - row_size: how many results to show default is 100
            - instance_id: 1 returns object ID
            - search_name: search user by name or machine_model_name
    """
    queryset = Machine.custom_manager.alive()
    serializer_class = MachineSerializer
    pagination_class = StandardApplicationSetPagination
    filter_backends = (DjangoFilterBackend, )
    filter_fields = ('name', )
    permission_classes = (IsAuthenticated, )
    
    lookup_url_kwarg = ('instance_id', )

    def list(self, request, *args, **kwargs):
        response = super(MachineApi, self).list(request, *args, **kwargs)
        check = dict(response.data)
        if check['count'] == 0:
            return rest_default_response(data=None, status=status.HTTP_404_NOT_FOUND)
        return rest_default_response(data=response.data, status=status.HTTP_200_OK)

    def filter_queryset(self, queryset):
        row_size = self.request.GET.get('row_size')
        search_name = self.request.GET.get('search_name')
        instance_id = self.request.GET.get('instance_id')
        cluster_id = self.request.GET.get('cluster_id')
        queryset = self.queryset.select_related('machine_model')

        if row_size:
            self.pagination_class.page_size = row_size

        if instance_id:
            queryset = queryset.filter(id=instance_id)

        if cluster_id:
            queryset = queryset.filter(cluster=cluster_id)

        if search_name:
            queryset = queryset.filter(
                Q(name__icontains=search_name) |
                Q(machine_model__name__icontains=search_name)
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