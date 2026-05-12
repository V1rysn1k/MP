from django.contrib.auth.models import AbstractUser
from django.db import models
from PIL import Image


class User(AbstractUser):
    bio = models.TextField(blank=True, verbose_name='О себе')
    email = models.EmailField(unique=True, verbose_name='Email')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Номер телефона')
    friends = models.ManyToManyField('self', blank=True, symmetrical=False, related_name='friend_of', verbose_name='Друзья')
    friend_requests = models.ManyToManyField('self', blank=True, symmetrical=False, related_name='incoming_requests', verbose_name='Заявки в друзья')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='Аватар', help_text='Загрузите изображение (jpg, png)')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username

    def is_friend(self, user):
        return self.friends.filter(pk=user.pk).exists()

    def has_sent_request(self, user):
        return self.friend_requests.filter(pk=user.pk).exists()
    
    def save(self, *args, **kwargs):
        """Переопределяем save для оптимизации аватара"""
        super().save(*args, **kwargs)
        
        if self.avatar and hasattr(self.avatar, 'path'):
            try:
                img = Image.open(self.avatar.path)
                if img.height > 300 or img.width > 300:
                    output_size = (300, 300)
                    img.thumbnail(output_size)
                    img.save(self.avatar.path)
            except Exception as e:
                pass