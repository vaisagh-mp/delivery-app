# Generated by Django 5.1.7 on 2025-04-16 10:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('delivery', '0002_customeraddress_alt_contact_no_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customeraddress',
            name='address',
            field=models.CharField(max_length=255),
        ),
    ]
