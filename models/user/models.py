import uuid

from django.db import models
from django.core.exceptions import ValidationError

from custom_user.models import AbstractEmailUser

from models.common.models import BaseModelFields
from sorl.thumbnail import ImageField


class UserType(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return f'Id: {self.id} Name: {self.name}'


class UserModel(AbstractEmailUser, BaseModelFields):
    first_name = models.CharField(max_length=40)
    last_name = models.CharField(max_length=150)
    full_name = models.CharField(max_length=255, blank=True, null=True)

    username = models.CharField(db_index=True, unique=True, max_length=64)
    email = models.EmailField(unique=False, db_index=True)
    USERNAME_FIELD = 'username'

    user_type = models.ForeignKey(UserType, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return f'Id: {self.id} Email: {self.email} Full Name: {self.full_name}'

    @staticmethod
    def check_email_unique(email):
        return UserModel.objects.filter(email=email.lower()).exists()

    def clean(self):
        em = UserModel.custom_manager.alive().filter(id=self.id)
        if em.exists():
            if em.first().email == self.email:
                self.email.lower()
        elif UserModel.objects.filter(email=self.email.lower(), is_active=True).exists():
            raise ValidationError('Email already exists.')
        self.email.lower()

    def check_last_login(self):
        um = UserModel.custom_manager.alive().filter(id=self.id, last_login__isnull=True)
        if um.exists():
            return False
        return True

    def set_new_user_detail_token(self):
        token_generated = str(uuid.uuid4())
        user_detail = UserDetail.custom_manager.alive().filter(user=self).first()
        user_detail.token_code = token_generated
        user_detail.save()
        return

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.full_name = '{} {}'.format(self.first_name.capitalize(), self.last_name.capitalize())
        self.email = self.email.replace(" ", "").replace("\t", "").lower()
        if not self.username:
            self.username = str(uuid.uuid4())
        super(UserModel, self).save(force_insert, force_update)

    @classmethod
    def user_reusable_details(self, user_id):
        user = UserModel.custom_manager.alive().filter(id=user_id).first()
        return {
            'id': user.id,
            'full_name': user.full_name,
            'email': user.email,
        }


class UserDetail(BaseModelFields):
    mobile_phone = models.CharField(max_length=36, blank=True, null=True)
    phone_verified = models.BooleanField(default=False)
    phone_verified_code = models.CharField(max_length=255, blank=True, null=True)

    email_verified = models.BooleanField(default=False)
    email_verified_code = models.CharField(max_length=255, blank=True, null=True)

    profile_picture = ImageField(upload_to='user-profile-photo', blank=True, null=True)

    token_code = models.CharField(max_length=255, blank=True, null=True)  # Serve as auth for password or activation

    user = models.OneToOneField(UserModel, on_delete=models.CASCADE, related_name='user_detail')

    def __str__(self):
        return f'Id: {self.id} User Id: {self.user.id} User Full Name: {self.user.full_name}'
