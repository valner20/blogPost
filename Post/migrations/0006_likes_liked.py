# Generated by Django 5.2.1 on 2025-05-28 20:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Post', '0005_rename_userb_comments_user_rename_userb_likes_user_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='likes',
            name='liked',
            field=models.BooleanField(default=False),
        ),
    ]
