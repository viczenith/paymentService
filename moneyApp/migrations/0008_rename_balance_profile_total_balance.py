# Generated by Django 5.0.3 on 2024-03-09 22:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('moneyApp', '0007_remove_profile_total_balance'),
    ]

    operations = [
        migrations.RenameField(
            model_name='profile',
            old_name='balance',
            new_name='total_balance',
        ),
    ]