# Generated by Django 5.1.3 on 2024-11-10 15:09

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0002_alter_metrics_answer_alter_metrics_answered_at_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="userprofile",
            name="metrics",
            field=models.ManyToManyField(blank=True, null=True, to="home.metrics"),
        ),
    ]