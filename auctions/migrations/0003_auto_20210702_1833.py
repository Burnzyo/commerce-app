# Generated by Django 3.2.4 on 2021-07-02 23:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0002_auto_20210702_1824'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='firstName',
        ),
        migrations.RemoveField(
            model_name='user',
            name='lastName',
        ),
    ]
