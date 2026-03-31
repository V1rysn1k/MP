from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count, Q
from .models import Teacher, TeacherInfo, Course, Student, Enrollment
from .forms import TeacherForm, TeacherInfoForm, CourseForm, StudentForm, EnrollmentForm


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


def teacher_add(request):
    """Добавление нового преподавателя"""
    if request.method == 'POST':
        teacher_form = TeacherForm(request.POST)
        info_form = TeacherInfoForm(request.POST)
        
        if teacher_form.is_valid() and info_form.is_valid():
            teacher = teacher_form.save()
            info = info_form.save(commit=False)
            info.teacher = teacher
            info.save()
            return redirect('/schedule/teachers/')
    else:
        teacher_form = TeacherForm()
        info_form = TeacherInfoForm()
    
    return render(request, 'teacher_add.html', {
        'teacher_form': teacher_form,
        'info_form': info_form
    })


def teacher_edit(request, teacher_id):
    """Редактирование преподавателя"""
    teacher = get_object_or_404(Teacher, id=teacher_id)
    if request.method == 'POST':
        form = TeacherForm(request.POST, instance=teacher)
        if form.is_valid():
            form.save()
            return redirect('/schedule/teachers/')
    else:
        form = TeacherForm(instance=teacher)
    return render(request, 'teacher_edit.html', {'form': form, 'teacher': teacher})


def teacher_detail(request, teacher_id):
    """Детальная страница преподавателя"""
    teacher = get_object_or_404(Teacher, id=teacher_id)
    courses = teacher.courses.all()
    return render(request, 'teacher_detail.html', {
        'teacher': teacher,
        'courses': courses
    })


def course_list(request):
    """Список курсов"""
    courses = Course.objects.all().select_related('teacher')
    return render(request, 'course_list.html', {'courses': courses})


def course_add(request):
    """Добавление нового курса"""
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/schedule/courses/')
    else:
        form = CourseForm()
    return render(request, 'course_add.html', {'form': form})


def course_detail(request, course_id):
    """Детальная страница курса"""
    course = get_object_or_404(Course, id=course_id)
    return render(request, 'course_detail.html', {'course': course})


def student_list(request):
    """Список студентов"""
    students = Student.objects.all()
    return render(request, 'student_list.html', {'students': students})


def student_add(request):
    """Добавление нового студента"""
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/schedule/students/')
    else:
        form = StudentForm()
    return render(request, 'student_add.html', {'form': form})


def student_detail(request, student_id):
    """Детальная страница студента"""
    student = get_object_or_404(Student, id=student_id)
    enrollments = Enrollment.objects.filter(student=student).select_related('course')
    courses = [e.course for e in enrollments]
    return render(request, 'student_detail.html', {
        'student': student,
        'courses': courses
    })