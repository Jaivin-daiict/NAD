# Generated by Django 5.1.3 on 2024-11-13 16:09

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0006_alter_metrics_max_length_alter_userprofile_metrics"),
    ]

    operations = [
        migrations.AddField(
            model_name="document",
            name="documentFile",
            field=models.FileField(blank=True, null=True, upload_to="documents/"),
        ),
    ]