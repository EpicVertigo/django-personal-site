# Generated by Django 2.0.2 on 2018-04-23 18:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('discordbot', '0054_auto_20180423_2152'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='discorduser',
            name='wf_settings',
        ),
        migrations.AddField(
            model_name='wfsettings',
            name='discord_user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='discordbot.DiscordUser'),
        ),
    ]