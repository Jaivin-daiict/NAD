# Generated by Django 5.1.3 on 2024-11-10 16:03

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0003_alter_userprofile_metrics"),
    ]

    operations = [
        migrations.AddField(
            model_name="criterion",
            name="criterionId",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="document",
            name="docId",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="metrics",
            name="metricId",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="subcriterion",
            name="SubCriterionId",
            field=models.IntegerField(default=0),
        ),
    ]