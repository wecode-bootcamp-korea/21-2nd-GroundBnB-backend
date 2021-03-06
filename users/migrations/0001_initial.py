# Generated by Django 3.2.4 on 2021-07-01 11:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=45)),
                ('birth', models.DateField(null=True)),
                ('email', models.EmailField(max_length=45, null=True)),
                ('password', models.CharField(max_length=200, null=True)),
                ('host', models.BooleanField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=0)),
            ],
            options={
                'db_table': 'users',
            },
        ),
        migrations.CreateModel(
            name='SocialFlatform',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('provider_name', models.CharField(max_length=45)),
                ('provider_id', models.CharField(max_length=200)),
                ('profile_image', models.URLField(max_length=2000)),
                ('nick_name', models.CharField(max_length=45)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.user')),
            ],
            options={
                'db_table': 'social_flatform',
            },
        ),
    ]
