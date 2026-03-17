from django.contrib import admin
from .models import Teacher, TeacherInfo, Course, Student, Enrollment


class TeacherInfoInline(admin.StackedInline):
    model = TeacherInfo
    can_delete = False


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'get_email']
    search_fields = ['first_name', 'last_name']
    inlines = [TeacherInfoInline]
    
    def get_email(self, obj):
        """Получить email из связанной TeacherInfo"""
        return obj.info.email if hasattr(obj, 'info') else '-'
    get_email.short_description = 'Email'


@admin.register(TeacherInfo)
class TeacherInfoAdmin(admin.ModelAdmin):
    list_display = ['teacher', 'email']
    search_fields = ['teacher__first_name', 'teacher__last_name', 'email']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'teacher', 'level']
    list_filter = ['level', 'teacher']
    search_fields = ['title']


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email']
    search_fields = ['first_name', 'last_name', 'email']


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'status', 'enrollment_date']
    list_filter = ['status']