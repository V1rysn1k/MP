from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.core.exceptions import ValidationError
import re


class Teacher(models.Model):
    first_name = models.CharField(max_length=50, verbose_name='Имя')
    last_name = models.CharField(max_length=50, verbose_name='Фамилия')
    
    created_at = models.DateTimeField(auto_now_add=True, null=True, verbose_name='Дата создания')

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = 'Преподаватель'
        verbose_name_plural = 'Преподаватели'
        ordering = ['-created_at']


class TeacherInfo(models.Model):
    teacher = models.OneToOneField(
        Teacher,
        on_delete=models.CASCADE,
        related_name='info',
        verbose_name='Преподаватель'
    )
    email = models.EmailField(unique=True, verbose_name='Email')
    bio = models.TextField(max_length=1000, verbose_name='Биография', blank=True)
    
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Телефон',
        validators=[
            RegexValidator(
                regex=r'^\+?7\d{10}$|^8\d{10}$',
                message='Телефон должен быть в формате +7XXXXXXXXXX или 8XXXXXXXXXX'
            )
        ]
    )
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Рейтинг',
        validators=[MinValueValidator(0), MaxValueValidator(20000)]
    )
    is_verified = models.BooleanField(default=False,null=True, verbose_name='Верифицирован')
    def __str__(self):
        return f"Информация о {self.teacher}"

    class Meta:
        verbose_name = 'Информация о преподавателе'
        verbose_name_plural = 'Информация о преподавателях'


class Course(models.Model):
    DOTA_RANKS = [
        ('Herald', 'Хранитель'),
        ('Guardian', 'Страж'),
        ('Crusader', 'Рыцарь'),
        ('Archon', 'Архонт'),
        ('Legend', 'Легенда'),
        ('Ancient', 'Древний'),
        ('Divine', 'Божество'),
        ('Immortal', 'Титан'),
    ]
    
    title = models.CharField(max_length=100, verbose_name='Название')
    description = models.TextField(max_length=500, verbose_name='Описание')
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.SET_NULL,
        related_name='courses',
        null=True,
        blank=True,
        verbose_name='Автор'
    )
    level = models.CharField(
        max_length=20,
        choices=DOTA_RANKS,
        default='Herald',
        verbose_name='Ранг'
    )
    created_at = models.DateTimeField(auto_now_add=True, null=True, verbose_name='Дата создания')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'
        ordering = ['-created_at']


class Student(models.Model):
    first_name = models.CharField(max_length=50, verbose_name='Имя')
    last_name = models.CharField(max_length=50, verbose_name='Фамилия')
    email = models.EmailField(unique=True, verbose_name='Email')
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='Телефон')
    birth_date = models.DateField(verbose_name='Дата рождения')
    enrollment_date = models.DateField(auto_now_add=True, verbose_name='Дата регистрации')
    
    steam_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        unique=True,
        verbose_name='Steam ID',
        validators=[
            RegexValidator(
                regex=r'^[0-9]{17}$',
                message='Steam ID должен содержать 17 цифр'
            )
        ]
    )
    dota_mmr = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='MMR',
        validators=[MinValueValidator(0), MaxValueValidator(15000)]
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = 'Студент'
        verbose_name_plural = 'Студенты'


class Enrollment(models.Model):
    STATUS_CHOICES = [
        ('ENROLLED', 'Записан'),
        ('COMPLETED', 'Завершил'),
        ('DROPPED', 'Отчислен'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name='Студент')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name='Курс')
    enrollment_date = models.DateField(auto_now_add=True, verbose_name='Дата записи')
    status = models.CharField(max_length=10, null=True, choices=STATUS_CHOICES, default='ENROLLED')

    def __str__(self):
        return f"{self.student} — {self.course}"

    class Meta:
        unique_together = ['student', 'course']
        verbose_name = 'Запись на курс'
        verbose_name_plural = 'Записи на курсы'