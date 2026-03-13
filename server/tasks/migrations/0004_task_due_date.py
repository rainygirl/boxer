from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('tasks', '0003_task_number')]
    operations = [
        migrations.AddField(
            model_name='task',
            field=models.DateField(blank=True, null=True),
            name='due_date',
        )
    ]
