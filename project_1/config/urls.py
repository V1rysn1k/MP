from django.urls import path, re_path
from catalog import views


urlpatterns = [

    # Главная
    path("", views.index, name="index"),

    # Курсы
    path("courses/", views.courses_list, name="courses"),
    path("courses/<int:course_id>/", views.course_detail, name="course_detail"),

    # Авторы
    path("authors/", views.authors_list, name="authors"),
    path("authors/<int:author_id>/", views.author_detail, name="author_detail"), 

    # Info
    path("info/", views.info, name="info"),

    path("not-found/", views.not_found_page, name="not_found_page"),

    re_path(r"^.*$", views.not_found_page),
]

