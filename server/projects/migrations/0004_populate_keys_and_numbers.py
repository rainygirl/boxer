from django.db import migrations


def _index_to_key(n):
    length = 2
    total = 0
    while True:
        count = 26 ** length
        if n < total + count:
            break
        total += count
        length += 1
    rem = n - total
    result = ''
    for _ in range(length):
        result = chr(ord('A') + rem % 26) + result
        rem //= 26
    return result


def populate_keys_and_task_numbers(apps, schema_editor):
    Project = apps.get_model('projects', 'Project')
    Task = apps.get_model('tasks', 'Task')

    # Assign keys to existing projects in creation order
    used_keys = set()
    i = 0
    for project in Project.objects.order_by('created_at'):
        if project.key:
            used_keys.add(project.key)
            continue
        while True:
            candidate = _index_to_key(i)
            i += 1
            if candidate not in used_keys:
                project.key = candidate
                used_keys.add(candidate)
                break
        project.save(update_fields=['key'])

    # Assign sequential task numbers per project
    for project in Project.objects.all():
        tasks = list(Task.objects.filter(project=project).order_by('sort_order', 'created_at'))
        for idx, task in enumerate(tasks, start=1):
            task.number = idx
            task.save(update_fields=['number'])
        project.next_task_number = len(tasks) + 1
        project.save(update_fields=['next_task_number'])


class Migration(migrations.Migration):
    dependencies = [
        ('projects', '0003_project_key_project_next_task_number'),
        ('tasks', '0003_task_number'),
    ]

    operations = [
        migrations.RunPython(populate_keys_and_task_numbers, migrations.RunPython.noop),
    ]
