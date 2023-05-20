# Generated by Django 4.1.7 on 2023-05-09 21:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0010_analysis_flex_carbon_graph_analysis_flex_cost_graph_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Budget',
        ),
        migrations.RemoveField(
            model_name='analysis',
            name='flex_carbon_graph',
        ),
        migrations.RemoveField(
            model_name='analysis',
            name='flex_cost_graph',
        ),
        migrations.RemoveField(
            model_name='analysis',
            name='flex_energy_dict',
        ),
        migrations.RemoveField(
            model_name='analysis',
            name='flex_energy_graph',
        ),
        migrations.RemoveField(
            model_name='host',
            name='TCO',
        ),
        migrations.RemoveField(
            model_name='host',
            name='app_waste_cost_3',
        ),
        migrations.RemoveField(
            model_name='host',
            name='capital',
        ),
        migrations.RemoveField(
            model_name='host',
            name='carbon_footprint_3',
        ),
        migrations.RemoveField(
            model_name='host',
            name='op_cost_3',
        ),
        migrations.RemoveField(
            model_name='host',
            name='ops_cons_3',
        ),
        migrations.AddField(
            model_name='host',
            name='carbon_footprint',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='host',
            name='carbon_footprint_high',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='host',
            name='carbon_footprint_low',
            field=models.FloatField(null=True),
        ),
    ]
