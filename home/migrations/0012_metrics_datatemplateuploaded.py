# Generated by Django 5.0.4 on 2024-11-25 05:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0011_metrics_datatemplate_metrics_hint'),
    ]

    operations = [
        migrations.AddField(
            model_name='metrics',
            name='dataTemplateUploaded',
            field=models.FileField(blank=True, null=True, upload_to='templates/'),
        ),
    ]