# Generated by Django 2.2 on 2019-05-29 13:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20190529_2152'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='name',
            field=models.CharField(default='noname', max_length=254),
            preserve_default=False,
        ),
    ]