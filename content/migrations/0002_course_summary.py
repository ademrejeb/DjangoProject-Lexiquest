# Generated by Django 3.2.6 on 2024-10-28 12:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='summary',
            field=models.TextField(blank=True, null=True),
        ),
    ]
