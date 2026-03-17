# schedule/migrations/0002_load_dota2_data.py
from django.db import migrations, transaction
import sys
from pathlib import Path


def load_dota2_data(apps, schema_editor):
    # Получаем модели
    Teacher = apps.get_model('schedule', 'Teacher')
    Course = apps.get_model('schedule', 'Course')
    
    # Добавляем путь к проекту для импорта catalog.data
    import sys
    from pathlib import Path
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    if str(BASE_DIR) not in sys.path:
        sys.path.append(str(BASE_DIR))
    
    try:
        from catalog import data
    except ImportError:
        print("="*50)
        print("ВНИМАНИЕ: Не удалось импортировать catalog.data")
        print("Убедитесь, что файл catalog/data.py существует")
        print("="*50)
        return
    
    # Словарь для соответствия старых ID новым объектам
    author_map = {}
    
    # 1. Загружаем авторов
    print("Загружаем авторов из data.py...")
    for author_data in data.AUTHORS:
        # Разделяем имя и фамилию
        name_parts = author_data['name'].split(' ', 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ''
        
        # Создаем автора
        author, created = Teacher.objects.get_or_create(
            email=author_data['email'],
            defaults={
                'first_name': first_name,
                'last_name': last_name,
                'bio': author_data['bio'],
            }
        )
        
        if not created:
            # Обновляем существующего
            author.first_name = first_name
            author.last_name = last_name
            author.bio = author_data['bio']
            author.save()
            print(f"  Обновлен автор: {author.first_name} {author.last_name}")
        else:
            print(f"  Создан автор: {author.first_name} {author.last_name}")
        
        # Сохраняем соответствие ID
        author_map[author_data['id']] = author
    
    # 2. Загружаем курсы
    print("\nЗагружаем курсы из data.py...")
    
    # Соответствие ваших уровней рангам DOTA 2
    LEVEL_MAPPING = {
        "Титан": "Immortal",
        "Рекрут": "Herald",
        "Рыцарь": "Crusader",
        "Страж": "Guardian"
    }
    
    for course_data in data.COURSES:
        # Получаем автора
        author = author_map.get(course_data['author_id'])
        if not author:
            print(f"  Предупреждение: автор с ID {course_data['author_id']} не найден для курса {course_data['title']}")
            continue
        
        # Преобразуем уровень
        dota_level = LEVEL_MAPPING.get(course_data['level'], 'Herald')
        
        # Создаем или обновляем курс
        course, created = Course.objects.get_or_create(
            title=course_data['title'],
            teacher=author,
            defaults={
                'description': course_data['description'],
                'level': dota_level,
            }
        )
        
        if not created:
            # Обновляем существующий
            course.description = course_data['description']
            course.level = dota_level
            course.save()
            print(f"  Обновлен курс: {course.title} (уровень: {dota_level})")
        else:
            print(f"  Создан курс: {course.title} (уровень: {dota_level})")
    
    print("\n" + "="*50)
    print(f"Загружено авторов: {Teacher.objects.count()}")
    print(f"Загружено курсов: {Course.objects.count()}")
    print("="*50)


def reverse_load(apps, schema_editor):
    """Откат миграции - удаляем загруженные данные"""
    Teacher = apps.get_model('schedule', 'Teacher')
    Course = apps.get_model('schedule', 'Course')
    
    # Удаляем все курсы и авторов
    Course.objects.all().delete()
    Teacher.objects.all().delete()
    print("Данные удалены")


class Migration(migrations.Migration):
    dependencies = [
        ('schedule', '0001_initial'),  # Зависимость от первой миграции
    ]

    operations = [
        migrations.RunPython(load_dota2_data, reverse_load),
    ]