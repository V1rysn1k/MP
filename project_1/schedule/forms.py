from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
import re
from .models import Teacher, TeacherInfo, Course, Student, Enrollment

def validate_name_not_numbers(value):
    if value.isdigit():
        raise ValidationError('Имя не может состоять только из цифр')


def validate_no_special_chars(value):
    if re.search(r'[!@#$%^&*()]', value):
        raise ValidationError('Имя не может содержать специальные символы')


def validate_min_age(value):
    from datetime import date
    today = date.today()
    age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
    if age < 16:
        raise ValidationError('Студент должен быть старше 16 лет')


class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['first_name', 'last_name']
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'Введите имя'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Введите фамилию'}),
        }
    
    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if first_name:
            first_name = first_name.strip().capitalize()
            
            validate_name_not_numbers(first_name)
            validate_no_special_chars(first_name)
            
            if len(first_name) < 2:
                raise ValidationError('Имя должно содержать минимум 2 символа')
        return first_name
    
    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if last_name:
            last_name = last_name.strip().capitalize()
            
            validate_name_not_numbers(last_name)
            validate_no_special_chars(last_name)
            
            if len(last_name) < 2:
                raise ValidationError('Фамилия должна содержать минимум 2 символа')
        return last_name
    
    def clean(self):
        cleaned_data = super().clean()
        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')
        
        if first_name and last_name and first_name.lower() == last_name.lower():
            raise ValidationError('Имя и фамилия не могут быть одинаковыми')
        
        return cleaned_data


class TeacherInfoForm(forms.ModelForm):
    class Meta:
        model = TeacherInfo
        fields = ['email', 'bio', 'phone', 'rating']
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'email@example.com', 'required': True}),
            'bio': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Краткая биография...'}),
            'phone': forms.TextInput(attrs={'placeholder': '+7XXXXXXXXXX'}),
            'rating': forms.NumberInput(attrs={'placeholder': '0-20000'}),
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            email = email.strip().lower()
            
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                raise ValidationError('Введите корректный email адрес')
        return email
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            phone = re.sub(r'\D', '', phone)
            
            if len(phone) == 11 and phone.startswith('8'):
                phone = '+7' + phone[1:]
            elif len(phone) == 11 and phone.startswith('7'):
                phone = '+7' + phone[1:]
            elif len(phone) == 10:
                phone = '+7' + phone
            else:
                raise ValidationError('Телефон должен быть в формате +7XXXXXXXXXX')
        
        return phone
    
    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if rating is not None:
            rating = round(rating, 2)
            
            if rating < 0 or rating > 20000:
                raise ValidationError('Рейтинг должен быть от 0 до 20000')
        return rating
    
    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        
        if not email:
            raise ValidationError('Email обязателен для заполнения')
        
        return cleaned_data


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'teacher', 'level']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Название курса', 'required': True}),
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Описание курса...', 'required': True}),
            'teacher': forms.Select(attrs={'required': True}),
            'level': forms.Select(attrs={'required': True}),
        }
    
    def clean_title(self):
        title = self.cleaned_data.get('title')
        if title:
            title = ' '.join(title.strip().split())
            title = title[0].upper() + title[1:] if title else title
            
            if len(title) < 5:
                raise ValidationError('Название курса должно содержать минимум 5 символов')
        return title
    
    def clean_description(self):
        description = self.cleaned_data.get('description')
        if description:
            description = ' '.join(description.strip().split())
            description = description[0].upper() + description[1:] if description else description
        return description
    
    def clean_teacher(self):
        teacher = self.cleaned_data.get('teacher')
        if not teacher:
            raise ValidationError('Необходимо выбрать автора курса')
        return teacher
    
    def clean_level(self):
        level = self.cleaned_data.get('level')
        if not level:
            raise ValidationError('Необходимо выбрать уровень курса')
        return level


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['first_name', 'last_name', 'email', 'phone', 'birth_date', 'steam_id', 'dota_mmr']
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'Имя', 'required': True}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Фамилия', 'required': True}),
            'email': forms.EmailInput(attrs={'placeholder': 'email@example.com', 'required': True}),
            'phone': forms.TextInput(attrs={'placeholder': '+7XXXXXXXXXX'}),
            'birth_date': forms.DateInput(attrs={'type': 'date', 'required': True}),
            'steam_id': forms.TextInput(attrs={'placeholder': '12345678901234567'}),
            'dota_mmr': forms.NumberInput(attrs={'placeholder': '0-20000'}),
        }
    
    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if first_name:
            first_name = first_name.strip().capitalize()
            
            validate_name_not_numbers(first_name)
            
            if len(first_name) < 2:
                raise ValidationError('Имя должно содержать минимум 2 символа')
        return first_name
    
    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if last_name:
            last_name = last_name.strip().capitalize()
            
            validate_name_not_numbers(last_name)
            
            if len(last_name) < 2:
                raise ValidationError('Фамилия должна содержать минимум 2 символа')
        return last_name
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            email = email.strip().lower()
            
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                raise ValidationError('Введите корректный email адрес')
        return email
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            phone = re.sub(r'\D', '', phone)

            if len(phone) == 11 and phone.startswith('8'):
                phone = '+7' + phone[1:]
            elif len(phone) == 11 and phone.startswith('7'):
                phone = '+7' + phone[1:]
            elif len(phone) == 10:
                phone = '+7' + phone
            else:
                raise ValidationError('Телефон должен быть в формате +7XXXXXXXXXX')
        return phone
    
    def clean_birth_date(self):
        birth_date = self.cleaned_data.get('birth_date')
        if birth_date:
            validate_min_age(birth_date)
        return birth_date
    
    def clean_steam_id(self):
        steam_id = self.cleaned_data.get('steam_id')
        if steam_id:
            steam_id = re.sub(r'\D', '', steam_id)
            
            if len(steam_id) != 17:
                raise ValidationError('Steam ID должен содержать ровно 17 цифр')
        return steam_id
    
    def clean_dota_mmr(self):
        mmr = self.cleaned_data.get('dota_mmr')
        if mmr is not None:
            mmr = int(mmr)
            
            if mmr < 0 or mmr > 15000:
                raise ValidationError('MMR должен быть от 0 до 15000')
        return mmr
    
    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        phone = cleaned_data.get('phone')
        
        if not email and not phone:
            raise ValidationError('Должен быть заполнен email или телефон')
        
        return cleaned_data


class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ['student', 'course', 'status']
        widgets = {
            'student': forms.Select(attrs={'required': True}),
            'course': forms.Select(attrs={'required': True}),
            'status': forms.Select(attrs={'required': True}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        student = cleaned_data.get('student')
        course = cleaned_data.get('course')
        
        if student and course:
            if Enrollment.objects.filter(student=student, course=course).exists():
                raise ValidationError('Этот студент уже записан на данный курс')
        
        return cleaned_data