# Generated by Django 2.0.2 on 2018-05-17 05:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('discordbot', '0063_wfsettings_kavat'),
    ]

    operations = [
        migrations.AddField(
            model_name='wfsettings',
            name='corrosive',
            field=models.BooleanField(default=False),
        ),
    ]
