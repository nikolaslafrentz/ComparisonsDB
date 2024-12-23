# Generated by Django 5.1.3 on 2024-12-02 14:36

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Country',
            fields=[
                ('code', models.CharField(max_length=3, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('region', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Indicator',
            fields=[
                ('code', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='StatisticValue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField()),
                ('value', models.FloatField(null=True)),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stats_comparison.country')),
                ('indicator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stats_comparison.indicator')),
            ],
            options={
                'indexes': [models.Index(fields=['country', 'indicator', 'year'], name='stats_compa_country_405f20_idx')],
                'unique_together': {('country', 'indicator', 'year')},
            },
        ),
    ]
