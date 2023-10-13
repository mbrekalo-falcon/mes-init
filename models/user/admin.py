import uuid
from django.contrib import admin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from custom_user.admin import EmailUserAdmin
from .models import (
    UserModel
)
from django.apps import apps


class UserCreateForm(UserCreationForm):
    class Meta:
        model = UserModel
        fields = ('first_name', 'last_name', 'email', 'username', 'is_superuser', 'is_staff',
                  'is_active', 'last_login', 'full_name', 'last_login',)


@admin.register(UserModel)
class UserModelAdmin(EmailUserAdmin):
    list_display = [
        'id', 'email', 'first_name', 'last_name', 'is_active', 'is_superuser', 'is_staff', 'last_login', 'deleted',
        'created_at',
    ]
    ordering = ('-last_login',)
    search_fields = ('email',)

    form = UserChangeForm
    add_form = UserCreateForm

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'first_name', 'last_name', 'email', 'username', 'is_superuser', 'is_staff',
                'is_active', 'last_login', 'full_name', 'password1', 'password2', 'deleted',
                'last_login',
            ),
        }),
    )

    fieldsets = (
        ('Email & Password', {
            'fields': ('email', 'password', 'username',)
        }),
        ('First name & Last name', {
            'fields': ('first_name', 'last_name',)
        }),
        ('Full name', {
            'fields': ('full_name',)

        }),
        ('Admin', {
            'fields': ('is_superuser', 'is_staff'),
        }),
        ('Status', {
            'fields': ('is_active', 'deleted', 'last_login',)

        })

    )

    exclude = ('password1', 'password2',)

    def get_form(self, request, obj=None, **kwargs):
        add_form = super(UserModelAdmin, self).get_form(request, obj, **kwargs)
        add_form.base_fields['username'].initial = uuid.uuid4()
        return add_form




# Register all models

# large fk list will be read-only in admin:
large_fk_fields = []


class ListAdminMixin(object):
    def __init__(self, model, admin_site):
        self.list_display = [field.name for field in model._meta.fields]
        self.search_fields = [field.name for field in model._meta.fields]  # Search fields
        self.readonly_fields = [field.name for field in model._meta.fields if field.name in large_fk_fields]
        super(ListAdminMixin, self).__init__(model, admin_site)


models = apps.get_models()
for model in models:
    admin_class = type('AdminClass', (ListAdminMixin, admin.ModelAdmin), {})
    try:
        admin.site.register(model, admin_class)
    except admin.sites.AlreadyRegistered:
        pass
