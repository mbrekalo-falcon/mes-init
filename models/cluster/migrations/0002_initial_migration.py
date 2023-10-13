# Generated by Django 4.2.5 on 2023-10-13 07:22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('cluster', '0001_initial_migration'),
        ('device', '0001_initial_migration'),
        ('machine', '0001_initial_migration'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('common', '0001_initial_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='userclient',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='userapplicationrole',
            name='cluster_role',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cluster.clusterrole'),
        ),
        migrations.AddField(
            model_name='userapplicationrole',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='clusteruser',
            name='cluster',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cluster.cluster'),
        ),
        migrations.AddField(
            model_name='clusteruser',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='clusterrolealert',
            name='alert_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cluster.alerttype'),
        ),
        migrations.AddField(
            model_name='clusterrolealert',
            name='application_role',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='common.applicationrole'),
        ),
        migrations.AddField(
            model_name='clusterrolealert',
            name='cluster',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='cluster.cluster'),
        ),
        migrations.AddField(
            model_name='clusterrolealert',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='clusterrole',
            name='application_role',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='common.applicationrole'),
        ),
        migrations.AddField(
            model_name='clusterrole',
            name='cluster',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cluster.cluster'),
        ),
        migrations.AddField(
            model_name='clustermachinedevice',
            name='cluster',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cluster.cluster'),
        ),
        migrations.AddField(
            model_name='clustermachinedevice',
            name='device',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='device.device'),
        ),
        migrations.AddField(
            model_name='clustermachinedevice',
            name='machine',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='machine.machine'),
        ),
        migrations.AddField(
            model_name='applicationmoduleclusterrolepermission',
            name='application_module',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='common.applicationmodule'),
        ),
        migrations.AddField(
            model_name='applicationmoduleclusterrolepermission',
            name='cluster_role',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cluster.clusterrole'),
        ),
        migrations.AlterUniqueTogether(
            name='userclient',
            unique_together={('user',)},
        ),
        migrations.AlterUniqueTogether(
            name='userapplicationrole',
            unique_together={('cluster_role', 'user')},
        ),
        migrations.AlterUniqueTogether(
            name='clusteruser',
            unique_together={('cluster', 'user')},
        ),
        migrations.AlterUniqueTogether(
            name='clusterrole',
            unique_together={('cluster', 'application_role')},
        ),
        migrations.AlterUniqueTogether(
            name='clustermachinedevice',
            unique_together={('cluster', 'machine', 'device')},
        ),
        migrations.AlterIndexTogether(
            name='clustermachinedevice',
            index_together={('cluster', 'machine', 'device')},
        ),
        migrations.AlterUniqueTogether(
            name='applicationmoduleclusterrolepermission',
            unique_together={('cluster_role', 'application_module')},
        ),
    ]
