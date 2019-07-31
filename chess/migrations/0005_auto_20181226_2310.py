# Generated by Django 2.1.4 on 2018-12-26 23:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chess', '0004_auto_20181226_1934'),
    ]

    operations = [
        migrations.AddField(
            model_name='chesspiece',
            name='can_castle',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='chesspiece',
            name='can_double_jump',
            field=models.BooleanField(default=False),
        ),
    ]
