from django import forms
from .models import Teacher, TeacherInfo


class TeacherForm(forms.Form):
    first_name = forms.CharField(
        max_length=50,
        label='Имя',
        help_text='Введите имя преподавателя',
        widget=forms.TextInput(attrs={'placeholder': 'Например: Иван'})
    )
    last_name = forms.CharField(
        max_length=50,
        label='Фамилия',
        help_text='Введите фамилию преподавателя',
        widget=forms.TextInput(attrs={'placeholder': 'Например: Петров'})
    )
    email = forms.EmailField(
        label='Email',
        help_text='Введите email преподавателя',
        required=False,
        widget=forms.EmailInput(attrs={'placeholder': 'ivan@example.com'})
    )
    bio = forms.CharField(
        label='Биография',
        help_text='Краткая информация о преподавателе',
        required=False,
        widget=forms.Textarea(attrs={'placeholder': 'Опыт работы, достижения...', 'rows': 4})
    )