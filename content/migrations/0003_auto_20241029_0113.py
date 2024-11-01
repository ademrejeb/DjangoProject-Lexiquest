# Generated by Django 3.2.6 on 2024-10-29 00:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0002_course_summary'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='course_images/'),
        ),
        migrations.AddField(
            model_name='course',
            name='language',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
