# Generated by Django 3.1 on 2021-08-05 12:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ugc', '0017_auto_20210805_1730'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='message_id',
        ),
        migrations.AddField(
            model_name='requests',
            name='message_id',
            field=models.IntegerField(default=101, unique=True, verbose_name='ID Сообщения'),
        ),
    ]
