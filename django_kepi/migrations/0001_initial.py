# Generated by Django 2.1.5 on 2019-05-21 20:07

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CachedRemoteText',
            fields=[
                ('address', models.URLField(primary_key=True, serialize=False)),
                ('content', models.TextField(default=None, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Following',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('follower', models.URLField(max_length=255)),
                ('following', models.URLField(max_length=255)),
                ('pending', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='IncomingMessage',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('received_date', models.DateTimeField(auto_now_add=True)),
                ('content_type', models.CharField(default='', max_length=255)),
                ('date', models.CharField(default='', max_length=255)),
                ('digest', models.CharField(default='', max_length=255)),
                ('host', models.CharField(default='', max_length=255)),
                ('path', models.CharField(default='', max_length=255)),
                ('signature', models.CharField(default='', max_length=255)),
                ('body', models.TextField(default='')),
                ('waiting_for', models.URLField(default=None, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Thing',
            fields=[
                ('number', models.CharField(default='', max_length=8, primary_key=True, serialize=False, unique=True)),
                ('f_type', models.CharField(choices=[('Reject', 'Reject'), ('Remove', 'Remove'), ('Update', 'Update'), ('Delete', 'Delete'), ('Add', 'Add'), ('Create', 'Create'), ('Like', 'Like'), ('Accept', 'Accept'), ('Follow', 'Follow'), ('Undo', 'Undo')], max_length=255)),
                ('remote_url', models.URLField(default=None, max_length=255, null=True, unique=True)),
                ('f_actor', models.URLField(blank=True, max_length=255)),
                ('f_name', models.CharField(blank=True, max_length=255)),
                ('active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='ThingField',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('value', models.TextField()),
                ('parent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='django_kepi.Thing')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='thingfield',
            unique_together={('parent', 'name')},
        ),
    ]
