# Generated by Django 3.2.9 on 2023-01-14 16:21

import datetime
from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Boroughs',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('OutwardName', models.CharField(max_length=128)),
                ('ApiName', models.CharField(max_length=128)),
            ],
            options={
                'verbose_name': 'Borough',
                'verbose_name_plural': 'Boroughs',
                'ordering': ['OutwardName'],
            },
        ),
        migrations.CreateModel(
            name='Inhalers',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
            ],
        ),
        migrations.CreateModel(
            name='PollutionLevelInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('band', models.CharField(max_length=6)),
                ('lower_bound', models.IntegerField()),
                ('upper_bound', models.IntegerField()),
                ('general_description', models.CharField(max_length=512)),
                ('risk_description', models.CharField(max_length=512)),
            ],
            options={
                'verbose_name': 'Pollution Level Info',
                'verbose_name_plural': 'Pollution Level Info',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='AppUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('dob', models.DateField(default=datetime.date.today)),
                ('pollution_limit', models.IntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(10)])),
                ('consent', models.BooleanField()),
                ('current_borough', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='current_users', to='Clear.boroughs')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('home_borough', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='home_users', to='Clear.boroughs')),
                ('other_borough', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='other_users', to='Clear.boroughs')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
                ('work_borough', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='work_users', to='Clear.boroughs')),
            ],
            options={
                'verbose_name': 'App User',
                'verbose_name_plural': 'App Users',
                'ordering': ['id'],
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='UserInhaler',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('puffs_today', models.IntegerField(default=0)),
                ('puffs_remaining', models.IntegerField()),
                ('puffs_per_day', models.IntegerField(blank=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('inhaler', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='inhaler_user', to='Clear.inhalers')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_inhaler', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'User Inhaler',
                'verbose_name_plural': 'Users Inhalers',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='PollutionLevels',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pollution_level', models.IntegerField(help_text='Overall Pollution Level')),
                ('pollution_level_no2', models.IntegerField(help_text='NO2 Pollution Level')),
                ('pollution_level_o3', models.IntegerField(help_text='O3 Pollution Level')),
                ('pollution_level_so2', models.IntegerField(help_text='SO2 Pollution Level')),
                ('pollution_level_pm10', models.IntegerField(help_text='PM10 Particulate')),
                ('pollution_level_pm25', models.IntegerField(help_text='PM25 Particulate')),
                ('pollution_level_pm2_5', models.IntegerField(help_text='PM2.5 Particulate')),
                ('pollution_date', models.DateField(default=datetime.date.today)),
                ('current_flag', models.BooleanField(default=True)),
                ('borough', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='borough_pollution', to='Clear.boroughs')),
            ],
            options={
                'verbose_name': 'Pollution Levels',
                'verbose_name_plural': 'Pollution Levels',
                'ordering': ['borough_id'],
            },
        ),
    ]
