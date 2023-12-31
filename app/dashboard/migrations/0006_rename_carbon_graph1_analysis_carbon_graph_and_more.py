# Generated by Django 4.1.7 on 2023-05-07 23:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0005_alter_host_flexible'),
    ]

    operations = [
        migrations.RenameField(
            model_name='analysis',
            old_name='carbon_graph1',
            new_name='carbon_graph',
        ),
        migrations.RenameField(
            model_name='analysis',
            old_name='carbon_graph2',
            new_name='cost_graph',
        ),
        migrations.RenameField(
            model_name='analysis',
            old_name='usage_percentage',
            new_name='cpu_usage',
        ),
        migrations.RenameField(
            model_name='analysis',
            old_name='cost_graph1',
            new_name='energy_graph',
        ),
        migrations.RemoveField(
            model_name='analysis',
            name='cost_graph2',
        ),
        migrations.RemoveField(
            model_name='analysis',
            name='energy_graph1',
        ),
        migrations.RemoveField(
            model_name='analysis',
            name='energy_graph2',
        ),
    ]
