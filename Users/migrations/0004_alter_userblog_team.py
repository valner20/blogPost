# Generated by Django 5.2.1 on 2025-05-30 02:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Users', '0003_alter_userblog_role_delete_roles'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userblog',
            name='team',
            field=models.ForeignKey(default=1, null=True, on_delete=models.SET(1), to='Users.teams'),
        ),
    ]
