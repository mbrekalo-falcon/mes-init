from core.__init__ import *
from core.common.serializers import ApplicationRoleSerializer, AvailableDomainSerializer
from models.cluster.models import ClusterUser, ClusterRole, UserApplicationRole, \
    ApplicationModuleClusterRolePermission
from models.user.models import UserType, UserModel
from models.common.models import ApplicationRole, ApplicationModule, ApplicationSubModule, AvailableDomain


class CommonView(APIView):
    """API view for reading common models"""

    permission_classes = (IsAuthenticated,)

    def get(self, request):
        app_roll_query = ApplicationRole.custom_manager.alive()
        app_roll = [{'id': app_roll.id, 'name': app_roll.name, 'description': app_roll.description} for app_roll in
                    app_roll_query]

        app_module_q = ApplicationModule.objects.all()
        app_module = [{'id': x.id, 'name': x.name} for x in app_module_q]

        app_sub_module_query = ApplicationSubModule.objects.all()
        app_sub_module = [{'id': app_sub_module.id, 'name': app_sub_module.name, 'module': app_sub_module.module.name}
                          for app_sub_module in app_sub_module_query]

        user_type_query = UserType.objects.all().order_by('name')
        user_type = [{'id': x.id, 'name': x.name} for x in user_type_query]

        prepare_response = {
            'app_rolls': app_roll,
            'app_modules': app_module,
            'app_sub_module': app_sub_module,
            'user_types': user_type,
        }

        return rest_default_response(data=prepare_response, status=status.HTTP_200_OK)


class ApplicationRoleAPI(generics.ListAPIView,
                         generics.CreateAPIView,
                         generics.UpdateAPIView,
                         generics.DestroyAPIView
                         ):
    queryset = (
        ApplicationRole.custom_manager.alive()
    )
    serializer_class = ApplicationRoleSerializer
    pagination_class = StandardApplicationSetPagination
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('name',)
    permission_classes = (IsAuthenticated,)
    lookup_url_kwarg = ('instance_id',)

    def list(self, request, *args, **kwargs):
        response = super(ApplicationRoleAPI, self).list(request, *args, **kwargs)
        check = dict(response.data)
        if check['count'] == 0:
            return rest_default_response(data=None, status=status.HTTP_404_NOT_FOUND)
        return rest_default_response(data=response.data, status=status.HTTP_200_OK)

    def filter_queryset(self, queryset):
        row_size = self.request.GET.get('row_size')
        instance_id = self.request.GET.get('instance_id')
        search_name = self.request.GET.get('search_name')
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

        check_query.first().soft_delete()
        return rest_default_response(status=status.HTTP_200_OK, message='Object deleted.')


class UserModulePermissionApi(
    APIView
):
    """Api for ClusterUserModulePermission model
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request, user_id):

        user = UserModel.custom_manager.alive().filter(id=user_id)
        if not user.exists():
            return rest_default_response(status=status.HTTP_403_FORBIDDEN,
                                         message="Nepostojeći korisnik.")

        qv_cluster_user = ClusterUser.custom_manager.alive().filter(user_id=user_id)
        if not qv_cluster_user.exists():
            return rest_default_response(status=status.HTTP_403_FORBIDDEN,
                                         message="Korisnik nije dodijeljen na podružnicu. "
                                                 "Molimo kontaktirajte svojeg administratora za nastavak.")

        qv_cluster_user_clusters = qv_cluster_user.values_list('cluster_id', flat=True)
        cluster_role = ClusterRole.custom_manager.alive().filter(cluster_id__in=qv_cluster_user_clusters)
        if not cluster_role.exists():
            return rest_default_response(status=status.HTTP_403_FORBIDDEN,
                                         message="Korisnik nije dodijeljena cluster rola. "
                                                 "Molimo kontaktirajte svojeg administratora za nastavak.")
        user_application_roles = UserApplicationRole.custom_manager.alive().filter(user_id=user_id)

        if not user_application_roles.exists():
            return rest_default_response(status=status.HTTP_403_FORBIDDEN,
                                         message="Korisnik nisu dodjeljenje role."
                                                 "Molimo kontaktirajte svojeg administratora za nastavak.")

        prepare = []

        for _uar in user_application_roles:
            prep = {
                'cluster_id': _uar.cluster_role.cluster.id,
                'cluster_name': _uar.cluster_role.cluster.name,
                'application_role': _uar.cluster_role.application_role.id,
                'application_name': _uar.cluster_role.application_role.name,
                'module_permissions':
                    [
                        {
                            'module_id': _x.application_module.id,
                            'module_name': _x.application_module.name,
                            'read': _x.read,
                            'write': _x.write,
                            'delete': _x.delete,
                        }
                        for _x in ApplicationModuleClusterRolePermission.custom_manager.alive().filter(
                            cluster_role_id=_uar.cluster_role.id
                        )
                    ],
            }
            prepare.append(prep)

        return rest_default_response(data=prepare, status=status.HTTP_200_OK)


class AvailableDomainApi(
    generics.ListAPIView
):
    permission_classes = (IsAuthenticated, )
    queryset = AvailableDomain.objects.all()
    serializer_class = AvailableDomainSerializer

    def list(self, request, *args, **kwargs):
        response = super(AvailableDomainApi, self).list(request, *args, **kwargs)
        check = dict(response.data)
        if check['count'] == 0:
            return rest_default_response(data=None, status=status.HTTP_404_NOT_FOUND)
        return rest_default_response(data=response.data, status=status.HTTP_200_OK)
