# Generated by Django 5.0.3 on 2024-03-14 14:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('moneyApp', '0009_customuser_currency_alter_profile_total_balance'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='currency',
            field=models.CharField(choices=[('USD', 'US Dollar'), ('GBP', 'British Pound'), ('EUR', 'Euro')], default='USD', max_length=3),
        ),
    ]
