# Generated by Django 3.2.9 on 2021-11-16 16:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('BPBackendDjango', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='o_auth_token',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='token_time',
            field=models.DateTimeField(null=True),
        ),
    ]