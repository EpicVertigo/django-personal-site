# Generated by Django 2.1.4 on 2019-01-26 13:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('discordbot', '0003_remove_discorduser_bnet_token'),
    ]

    operations = [
        migrations.CreateModel(
            name='MixEvent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mix_events', to='discordbot.DiscordUser')),
                ('wisdom', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='discordbot.Wisdom')),
            ],
        ),
    ]
