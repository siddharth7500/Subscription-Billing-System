# Generated by Django 4.2.21 on 2025-05-10 19:23

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("billing", "0006_alter_subscription_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="subscription",
            name="requested_on",
            field=models.DateField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
