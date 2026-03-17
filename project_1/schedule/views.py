from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count
from .models import Teacher, TeacherInfo, Course, Student, Enrollment
from .forms import TeacherForm


def index(request):
    """Главная страница приложения schedule"""
    context = {
        'teachers_count': Teacher.objects.count(),
        'courses_count': Course.objects.count(),
        'students_count': Student.objects.count(),
    }
    return render(request, 'schedule_index.html', context)


def teacher_list(request):
    """Список преподавателей"""
    teachers = Teacher.objects.all().prefetch_related('courses')
    return render(request, 'teacher_list.html', {'teachers': teachers})


def teacher_detail(request, teacher_id):
    """Детальная страница преподавателя"""
    teacher = get_object_or_404(Teacher, id=teacher_id)
    courses = teacher.courses.all()
    return render(request, 'teacher_detail.html', {
        'teacher': teacher,
        'courses': courses
    })


def student_list(request):
    """Список студентов"""
    students = Student.objects.all()
    return render(request, 'student_list.html', {'students': students})


def student_detail(request, student_id):
    """Детальная страница студента"""
    student = get_object_or_404(Student, id=student_id)
    enrollments = Enrollment.objects.filter(student=student).select_related('course')
    courses = [e.course for e in enrollments]
    return render(request, 'student_detail.html', {
        'student': student,
        'courses': courses
    })

def teacher_add(request):
    """Добавление нового преподавателя с использованием формы"""
    if request.method == 'POST':
        form = TeacherForm(request.POST)
        
        if form.is_valid():
            teacher = Teacher.objects.create(
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name']
            )
            
            TeacherInfo.objects.create(
                teacher=teacher,
                email=form.cleaned_data['email'],
                bio=form.cleaned_data['bio']
            )
            
            return redirect('/schedule/teachers/')
    else:
        form = TeacherForm()
    
    return render(request, 'teacher_add.html', {'form': form})

def course_add(request):
    """Добавление нового курса (без форм)"""
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        teacher_id = request.POST.get('teacher')
        level = request.POST.get('level')
        
        Course.objects.create(
            title=title,
            description=description,
            teacher_id=teacher_id,
            level=level
        )
        return redirect('/schedule/courses/')
    
    teachers = Teacher.objects.all()
    levels = Course.DOTA_RANKS
    return render(request, 'course_add.html', {
        'teachers': teachers,
        'levels': levels
    })

def course_list(request):
    """Список всех курсов"""
    courses = Course.objects.all().select_related('teacher')
    return render(request, 'course_list.html', {'courses': courses})

def course_detail(request, course_id):
    """Детальная страница курса"""
    course = get_object_or_404(Course, id=course_id)
    return render(request, 'course_detail.html', {'course': course})

def teacher_add(request):
    """Добавление нового преподавателя с использованием формы"""
    if request.method == 'POST':
        form = TeacherForm(request.POST)
        if form.is_valid():
            # Данные валидны - сохраняем
            teacher = Teacher.objects.create(
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name']
            )
            TeacherInfo.objects.create(
                teacher=teacher,
                email=form.cleaned_data['email'],
                bio=form.cleaned_data['bio']
            )
            return redirect('/schedule/teachers/')
        # Если форма невалидна - будет показана с ошибками
    else:
        form = TeacherForm()  # Пустая форма для GET запроса
    
    return render(request, 'teacher_add.html', {'form': form})