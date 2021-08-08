# Generated by Django 3.1 on 2021-08-05 18:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ugc', '0024_requests_reply_to'),
    ]

    operations = [
        migrations.AlterField(
            model_name='requests',
            name='message_id',
            field=models.IntegerField(default=100, verbose_name='ID Сообщения'),
        ),
        migrations.AlterField(
            model_name='requests',
            name='reply_to',
            field=models.IntegerField(default=200, verbose_name='ID Запроса'),
        ),
    ]
