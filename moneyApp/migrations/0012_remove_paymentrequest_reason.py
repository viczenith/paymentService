# Generated by Django 5.0.3 on 2024-03-18 15:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('moneyApp', '0011_paymentrequest'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='paymentrequest',
            name='reason',
        ),
    ]
