# Generated by Django 3.2.9 on 2021-12-16 17:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('databases', '0003_remove_investment_invested_amt'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bank',
            name='Current_amount',
            field=models.IntegerField(default=0),
        ),
    ]