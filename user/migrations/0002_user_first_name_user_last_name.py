# Generated by Django 5.1.1 on 2024-09-12 11:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='first_name',
            field=models.CharField(default='Test', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='user',
            name='last_name',
            field=models.CharField(default='Test', max_length=100),
            preserve_default=False,
        ),
    ]
