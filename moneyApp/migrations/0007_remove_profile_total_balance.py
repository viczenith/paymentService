# Generated by Django 5.0.3 on 2024-03-09 21:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('moneyApp', '0006_transaction_deposit_method_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='total_balance',
        ),
    ]
