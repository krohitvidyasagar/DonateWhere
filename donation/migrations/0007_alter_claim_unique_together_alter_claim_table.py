# Generated by Django 5.0.4 on 2024-04-21 15:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('donation', '0006_claim'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='claim',
            unique_together={('donation', 'claimant')},
        ),
        migrations.AlterModelTable(
            name='claim',
            table='claim',
        ),
    ]
