from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count, Q
from schedule.models import Teacher, Course, Student, Enrollment


def index(request):
    """Главная страница"""
    latest_courses = Course.objects.all()[:5]
    return render(request, "index.html", {
        "info": {
            "title": "Каталог курсов по DOTA 2",
            "about": "Мини-сайт для улучшения умений игроков Defense Of The Ancients 2"
        },
        "latest_courses": latest_courses
    })


def courses_list(request):
    """Список всех курсов"""
    courses = Course.objects.all().select_related('teacher')
    return render(request, "courses.html", {"courses": courses})


def course_detail(request, course_id):
    """Детальная страница курса с формой записи"""
    course = get_object_or_404(Course, id=course_id)
    success_message = None
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        birth_date = request.POST.get('birth_date')
        
        student, created = Student.objects.get_or_create(
            email=email,
            defaults={
                'first_name': first_name,
                'last_name': last_name,
                'phone': phone,
                'birth_date': birth_date,
            }
        )
        
        if not created:
            student.first_name = first_name
            student.last_name = last_name
            student.phone = phone
            student.birth_date = birth_date
            student.save()
        
        enrollment, created = Enrollment.objects.get_or_create(
            student=student,
            course=course,
            defaults={'status': 'ENROLLED'}
        )
        
        success_message = f"{student.first_name} {student.last_name}, вы записаны на курс!"
    
    return render(request, "course_detail.html", {
        "course": course,
        "success_message": success_message
    })


def authors_list(request):
    """Список всех авторов"""
    authors = Teacher.objects.all().prefetch_related('courses')
    return render(request, "authors.html", {"authors": authors})


def author_detail(request, author_id):
    """Детальная страница автора"""
    author = get_object_or_404(Teacher, id=author_id)
    author_courses = author.courses.all()
    return render(request, "author_details.html", {
        "author": author,
        "courses": author_courses
    })


def info(request):
    """Страница информации"""
    return render(request, "info.html", {
        "info": {
            "title": "Каталог курсов по DOTA 2",
            "about": "Мини-сайт для улучшения умений игроков Defense Of The Ancients 2"
        }
    })


def not_found_page(request, message="Такой страницы нет"):
    """Страница 404"""
    response = render(request, "not_found.html", {"message": message})
    response.status_code = 404
    return response


def orm_queries(request):
    """Страница с демонстрацией ORM-запросов"""
    
    course_id = request.GET.get('course_id')
    n = request.GET.get('n', 1)
    
    try:
        n = int(n)
    except ValueError:
        n = 1
    
    all_courses = Course.objects.all()
    
    course_students = []
    selected_course = None
    
    if course_id:
        try:
            course_id = int(course_id)
            selected_course = Course.objects.filter(id=course_id).first()
            if selected_course:
                course_students = Student.objects.filter(enrollment__course_id=course_id)
        except ValueError:
            pass

    teachers_with_more_than_n_courses = Teacher.objects.annotate(
        course_count=Count('courses')
    ).filter(course_count__gt=n)
    
    students_without_courses = Student.objects.filter(enrollment__isnull=True)
    
    teachers_without_bio = Teacher.objects.filter(
        Q(info__isnull=True) | Q(info__bio__isnull=True) | Q(info__bio='')
    )
    
    context = {
        'all_courses': all_courses,
        'course_students': course_students,
        'selected_course': selected_course,
        'selected_course_id': course_id,
        'teachers_with_more_than_n_courses': teachers_with_more_than_n_courses,
        'n': n,
        'students_without_courses': students_without_courses,
        'teachers_without_bio': teachers_without_bio,
    }
    return render(request, 'orm_queries.html', context)