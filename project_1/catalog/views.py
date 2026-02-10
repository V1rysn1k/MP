from django.shortcuts import render
from .data import COURSES, AUTHORS, SITE_INFO


def index(request):
    latest_courses = COURSES[:5]
    return render(request, "index.html", {"info": SITE_INFO, "latest_courses": latest_courses})


def courses_list(request):
    return render(request, "courses.html", {"courses": COURSES})


def course_detail(request, course_id):
    course = next((c for c in COURSES if c["id"] == course_id), None)
    if not course:
        return not_found_page(request, f"Курс с id={course_id} не найден")

    author = next((a for a in AUTHORS if a["id"] == course["author_id"]), None)
    return render(request, "course_detail.html", {"course": course, "author": author})


def authors_list(request):
    return render(request, "authors.html", {"authors": AUTHORS})


def author_detail(request, author_id):
    author = next((a for a in AUTHORS if a["id"] == author_id), None)
    if not author:
        return not_found_page(request, f"Автор с id={author_id} не найден")

    author_courses = [c for c in COURSES if c["author_id"] == author_id]
    return render(request, "author_details.html", {"author": author, "courses": author_courses})


def info(request):
    return render(request, "info.html", {"info": SITE_INFO})


def not_found_page(request, message="Такой страницы нет"):
    response = render(request, "not_found.html", {"message": message})
    response.status_code = 404
    return response

