# Generated by Django 2.1.5 on 2019-05-16 15:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('django_kepi', '0020_auto_20190516_1451'),
    ]

    operations = [
        migrations.CreateModel(
            name='ActivityField',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('value', models.TextField()),
            ],
        ),
        migrations.RemoveField(
            model_name='activity',
            name='other_fields',
        ),
        migrations.AddField(
            model_name='activityfield',
            name='parent',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='django_kepi.Activity'),
        ),
        migrations.AlterUniqueTogether(
            name='activityfield',
            unique_together={('parent', 'name')},
        ),
    ]
