# Generated by Django 2.2.17 on 2020-12-31 16:10

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('discordbot', '0024_auto_20201019_0052'),
    ]

    operations = [
        migrations.DeleteModel(
            name='CoronaReport',
        ),
        migrations.AlterModelOptions(
            name='mixpollentry',
            options={'verbose_name': 'Mix Poll Entry', 'verbose_name_plural': 'Mix Poll Entries'},
        ),
        migrations.AddField(
            model_name='gachi',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='gachi',
            name='deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='gachi',
            name='modified',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.DeleteModel(
            name='Counter',
        ),
        migrations.DeleteModel(
            name='CounterGroup',
        ),
    ]