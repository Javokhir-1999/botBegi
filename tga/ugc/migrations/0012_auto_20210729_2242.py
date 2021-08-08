# Generated by Django 3.1 on 2021-07-29 17:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ugc', '0011_auto_20210722_0203'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='status',
            field=models.TextField(choices=[('REQUESTED', 'REQUESTED'), ('JOINED', 'JOINED'), ('BLOCKED', 'BLOCKED'), ('ADMIN', 'ADMIN')], default='REQUESTED', max_length=20, verbose_name='Статус'),
        ),
    ]
