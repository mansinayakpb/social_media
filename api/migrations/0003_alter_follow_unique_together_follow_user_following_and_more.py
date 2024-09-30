# Generated by Django 4.2.16 on 2024-09-26 10:12

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0002_remove_user_username"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="follow",
            unique_together=set(),
        ),
        migrations.AddField(
            model_name="follow",
            name="user_following",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="user_following",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="follow",
            name="user",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="user",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterUniqueTogether(
            name="follow",
            unique_together={("user", "user_following")},
        ),
        migrations.RemoveField(
            model_name="follow",
            name="user_followed",
        ),
    ]
