from django.db import models
from models.common.models import BaseModelFields


class MachineModel(models.Model):
    name = models.CharField(max_length=255)
    note = models.TextField(blank=True, null=True)
    program_number = models.CharField(max_length=255, blank=True, null=True)
    bar_cutter = models.BooleanField(default=False)

    def __str__(self):
        return f'Id: {self.id} Name: {self.name}'


class Machine(BaseModelFields):
    name = models.CharField(max_length=255)
    ip = models.GenericIPAddressField(blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    cluster = models.ForeignKey('cluster.Cluster', on_delete=models.CASCADE)
    machine_model = models.ForeignKey(MachineModel, on_delete=models.CASCADE)
    active_wires = models.IntegerField(default=1)
    active_bins = models.IntegerField(null=True, blank=True)
    designated_disposal_bin = models.IntegerField(null=True, blank=True)
    location_designation = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f'Id: {self.id} Name: {self.name}'
