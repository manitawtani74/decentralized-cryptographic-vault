# Generated by Django 3.2.7 on 2022-01-18 16:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shredder', '0002_file_processed'),
    ]

    operations = [
        migrations.AddField(
            model_name='file',
            name='chunkmap',
            field=models.JSONField(default={}),
        ),
    ]
