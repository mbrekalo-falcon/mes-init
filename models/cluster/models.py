from django.db import models
from models.common.models import BaseModelFields
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from models.user.models import UserModel


class Cluster(BaseModelFields):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=150, blank=True, null=True)
    postal_code = models.CharField(max_length=45, blank=True, null=True)
    country = models.CharField(max_length=60, blank=True, null=True)
    phone = models.CharField(max_length=35, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    external_cluster_id = models.CharField(max_length=255, blank=True, null=True, unique=True)  # UNIQUE!
    active_antennas = models.BooleanField(default=False)

    def __str__(self):
        return f'Id: {self.id} Name: {self.name} Address: {self.address}'


class ClusterUser(BaseModelFields):
    """
    Povezivanje usera na cluster za potrebe praćenja proizvodnje u određenom clusteru (clusterima)
    """
    cluster = models.ForeignKey(Cluster, on_delete=models.CASCADE)
    user = models.ForeignKey('user.UserModel', on_delete=models.CASCADE)

    def __str__(self):
        return f'Id: {self.id} Cluster: {self.cluster.name} User: {self.user.full_name}'

    class Meta:
        unique_together = ('cluster', 'user',)


class ClusterRole(BaseModelFields):
    """
    Kad se kreira novi cluster automatski će se napuniti cluster-role
    Role se definiraju za svaki cluster posebno (role nevezane za cluster će se dodijeljivati na Zagreb po defaultu)
    """
    cluster = models.ForeignKey(Cluster, on_delete=models.CASCADE)
    application_role = models.ForeignKey('common.ApplicationRole', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('cluster', 'application_role',)

    def __str__(self):
        return f'Id: {self.id} Cluster Id: {self.cluster.id} Application Role ID: {self.application_role.id}'


class ApplicationModuleClusterRolePermission(BaseModelFields):
    """
    Permisije za module za cluster-rolu
    """
    cluster_role = models.ForeignKey(ClusterRole, on_delete=models.CASCADE)
    application_module = models.ForeignKey('common.ApplicationModule', on_delete=models.CASCADE)
    read = models.BooleanField(default=False)
    write = models.BooleanField(default=False)
    delete = models.BooleanField(default=False)

    class Meta:
        unique_together = ('cluster_role', 'application_module',)

    def __str__(self):
        return f'Id: {self.id} Cluster Role Id: {self.cluster_role.id} Application Module: {self.application_module.id}'


class UserApplicationRole(BaseModelFields):
    """
        Povezivanje usera i cluster-role
    """
    cluster_role = models.ForeignKey(ClusterRole, on_delete=models.CASCADE)
    user = models.ForeignKey('user.UserModel', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('cluster_role', 'user',)

    def __str__(self):
        return f'Id: {self.id} Cluster Role Id: {self.cluster_role.id} User: {self.user.id}'


class ClusterMachineDevice(BaseModelFields):
    """
        Assign Cluster To Machine and Device
    """
    cluster = models.ForeignKey(Cluster, on_delete=models.CASCADE)
    machine = models.ForeignKey('machine.Machine', on_delete=models.CASCADE, blank=True, null=True)
    device = models.ForeignKey('device.Device', on_delete=models.CASCADE)
    domain = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        unique_together = ('cluster', 'machine', 'device',)
        index_together = ('cluster', 'machine', 'device',)

    def __str__(self):
        return f'Id: {self.id} Cluster: {self.cluster.name} Device: {self.device.name}'


class AlertType(BaseModelFields):
    name = models.CharField(max_length=255)
    persistant = models.BooleanField(default=False)

    def __str__(self):
        return f'Id: {self.id}, Name: {self.name}'

    @classmethod
    def danger(cls):
        alert_type = AlertType.custom_manager.alive().filter(id=1)
        if not alert_type.exists():
            return None
        return alert_type.first().id

    @classmethod
    def alert(cls):
        alert_type = AlertType.custom_manager.alive().filter(id=2)
        if not alert_type.exists():
            return None
        return alert_type.first().id

    @classmethod
    def info(cls):
        alert_type = AlertType.custom_manager.alive().filter(id=3)
        if not alert_type.exists():
            return None
        return alert_type.first().id

    @classmethod
    def global_message(cls):
        alert_type = AlertType.custom_manager.alive().filter(id=4)
        if not alert_type.exists():
            return None
        return alert_type.first().id


class ClusterRoleAlert(BaseModelFields):
    """
    Alerts for users based on their cluster and/or role
    null value for cluster will send alert to all clusters
    and null value for application_role will send alert to all roles
    """
    cluster = models.ForeignKey('cluster.Cluster', on_delete=models.CASCADE, blank=True, null=True)
    application_role = models.ForeignKey('common.ApplicationRole', on_delete=models.CASCADE, blank=True, null=True)
    alert_type = models.ForeignKey('cluster.AlertType', on_delete=models.CASCADE)
    data = models.JSONField(default=dict)
    created_by = models.ForeignKey('user.UserModel', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f'Id: {self.id} AlertTypeId: {self.alert_type_id}'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super(ClusterRoleAlert, self).save(force_insert, force_update)
        # if self._state.adding:     <-- somehow it doesn't work if this is active
        q_users = UserApplicationRole.custom_manager.alive()
        if self.cluster:
            q_users = q_users.filter(cluster_role__cluster=self.cluster)

        if self.application_role:
            q_users = q_users.filter(cluster_role__application_role=self.application_role)

        q_filtered_users = list(q_users.values_list('user_id', flat=True))
        q_superadmins = list(UserModel.custom_manager.alive().filter(is_superuser=True).values_list('id', flat=True))

        target_user_ids = q_filtered_users+q_superadmins
        target_user_ids = set(target_user_ids)

        for user_id in target_user_ids:
            layer = get_channel_layer()
            channel_name = 'cluster-role-alert-{}'.format(user_id)
            async_to_sync(layer.group_send)(channel_name, {
                'type': 'events.alarm',
                'content': {
                    'id': self.id,
                    'alert_type_id': self.alert_type_id,
                    'alert_type_name': self.alert_type.name,
                    'alert_type_persistant': self.alert_type.persistant,
                    'message': self.data,
                    'created_at': self.created_at.strftime('%Y-%m-%d %H:%M %z')
                }
            })
