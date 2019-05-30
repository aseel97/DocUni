from django.contrib import admin

from .models import University, Faculty, Course, File, Comment,Ip

admin.site.register(University)

admin.site.register(Faculty)
admin.site.register(Course)
admin.site.register(File)
admin.site.register(Ip)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'file', 'created', 'active')
    list_filter = ('active', 'created', 'updated')
    search_fields = ('user', 'body')
