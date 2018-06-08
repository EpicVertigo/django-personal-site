# Generated by Django 2.0.2 on 2018-04-23 19:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('discordbot', '0055_auto_20180423_2158'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='wfsettings',
            name='discord_user',
        ),
        migrations.AddField(
            model_name='discorduser',
            name='wf_settings',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='discordbot.WFSettings'),
        ),
    ]