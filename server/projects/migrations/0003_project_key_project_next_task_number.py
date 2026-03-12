from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0002_project_disabled_statuses"),
    ]

    operations = [
        # Add key as nullable first — unique constraint added after data migration populates values
        migrations.AddField(
            model_name="project",
            name="key",
            field=models.CharField(blank=True, null=True, max_length=20),
        ),
        migrations.AddField(
            model_name="project",
            name="next_task_number",
            field=models.PositiveIntegerField(default=1),
        ),
    ]
