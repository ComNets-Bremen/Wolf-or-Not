# Generated by Django 3.2.15 on 2022-08-19 08:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('simplelabel', '0006_remove_class_class_color'),
    ]

    operations = [
        migrations.AddField(
            model_name='class',
            name='class_color',
            field=models.CharField(default='00FF00', max_length=12),
        ),
    ]
