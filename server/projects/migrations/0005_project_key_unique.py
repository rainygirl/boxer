from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0004_populate_keys_and_numbers"),
    ]

    operations = [
        migrations.AlterField(
            model_name="project",
            name="key",
            field=models.CharField(blank=True, max_length=20, unique=True),
        ),
    ]
