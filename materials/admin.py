from django.contrib import admin

from materials.models import Course, Lesson


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ["title", "description"]
    search_fields = ["title"]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ["title", "course", "description", "video_url"]
    list_filter = ["course"]
    search_fields = ["title"]
