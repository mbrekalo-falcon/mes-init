import uuid

from django.db import models


class BaseModelManager(models.Manager):
    def alive(self):
        return super().get_queryset().filter(deleted=False)

    def dead(self):
        return super().get_queryset().filter(deleted=True)


class BaseModelFields(models.Model):
    """

        UUID is representation for scalability and async operations on models.
        Future thoughts scale application.

    """
    id = models.BigAutoField(primary_key=True, db_index=True, unique=True, editable=False)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, auto_created=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    deleted = models.BooleanField(default=False)

    custom_manager = BaseModelManager()  # Extend manager for some custom methods

    class Meta:
        abstract = True

    def soft_delete(self):
        self.deleted = True
        super(BaseModelFields, self).save()

    def hard_delete(self):
        super(BaseModelFields, self).delete()


class ApplicationModule(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return 'Id: {} Name: {}'.format(self.id, self.name)


class ApplicationSubModule(models.Model):
    name = models.CharField(max_length=255)
    module = models.ForeignKey(ApplicationModule, on_delete=models.CASCADE)

    def __str__(self):
        return 'Id: {} Name: {} Module: {}'.format(self.id, self.name, self.module.name)


class ApplicationRole(BaseModelFields):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return 'Id: {} Name: {}'.format(self.id, self.name)


class AvailableDomain(models.Model):
    domain = models.CharField(max_length=255)
    note = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'Id: {self.id} Domain: {self.domain}'
