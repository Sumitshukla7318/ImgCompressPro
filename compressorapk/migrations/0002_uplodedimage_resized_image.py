# Generated by Django 5.0.3 on 2024-12-06 17:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('compressorapk', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='uplodedimage',
            name='resized_image',
            field=models.ImageField(blank=True, null=True, upload_to='resized/'),
        ),
    ]
