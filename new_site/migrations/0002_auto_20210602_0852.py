# Generated by Django 3.2.3 on 2021-06-02 05:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('new_site', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='schedule',
            old_name='Organizator_id',
            new_name='organizator_id',
        ),
        migrations.RemoveField(
            model_name='schedule',
            name='status',
        ),
        migrations.AlterField(
            model_name='room',
            name='seats',
            field=models.PositiveIntegerField(null=True),
        ),
    ]
