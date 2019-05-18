# Generated by Django 2.1.5 on 2019-05-18 11:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('things_for_testing', '0012_auto_20190518_1156'),
        ('django_kepi', '0024_auto_20190518_1145'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ActivityModel',
        ),
        migrations.AlterField(
            model_name='thing',
            name='f_type',
            field=models.CharField(choices=[('Reject', 'Reject'), ('Add', 'Add'), ('Update', 'Update'), ('Remove', 'Remove'), ('Undo', 'Undo'), ('Delete', 'Delete'), ('Accept', 'Accept'), ('Create', 'Create'), ('Like', 'Like'), ('Follow', 'Follow')], max_length=255),
        ),
    ]
