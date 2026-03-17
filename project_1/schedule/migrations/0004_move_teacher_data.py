# schedule/migrations/0004_move_teacher_data.py
from django.db import migrations


def move_teacher_data(apps, schema_editor):
    Teacher = apps.get_model('schedule', 'Teacher')
    TeacherInfo = apps.get_model('schedule', 'TeacherInfo')
    
    for teacher in Teacher.objects.all():
        TeacherInfo.objects.get_or_create(
            teacher=teacher,
            defaults={
                'email': f"{teacher.first_name.lower()}.{teacher.last_name.lower()}@dota2.ru",
                'bio': 'Биография не указана'
            }
        )


def reverse_move(apps, schema_editor):
    TeacherInfo = apps.get_model('schedule', 'TeacherInfo')
    TeacherInfo.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ('schedule', '0003_alter_teacher_options_remove_teacher_bio_and_more'),  # Точное имя файла без .py
    ]

    operations = [
        migrations.RunPython(move_teacher_data, reverse_move),
    ]