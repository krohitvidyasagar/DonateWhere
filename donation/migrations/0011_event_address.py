# Generated by Django 5.0.4 on 2024-05-02 13:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('donation', '0010_alter_message_options_event'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='address',
            field=models.TextField(null=True),
        ),
    ]
