# Generated by Django 2.0.2 on 2018-08-09 12:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('poeladder', '0014_poeleague_slug_link'),
    ]

    operations = [
        migrations.RenameField(
            model_name='poeleague',
            old_name='slug_link',
            new_name='slug',
        ),
    ]
