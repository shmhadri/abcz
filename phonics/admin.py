from django.contrib import admin
from .models import Student, LetterProgress, CVCWord, CVCSentence, CVCStory, CVCProgress


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['name', 'school', 'total_score', 'letters_completed', 'created_at']
    search_fields = ['name', 'school']
    list_filter = ['created_at', 'letters_completed']
    readonly_fields = ['total_score', 'letters_completed', 'created_at', 'updated_at']


@admin.register(LetterProgress)
class LetterProgressAdmin(admin.ModelAdmin):
    list_display = ['student', 'letter', 'score', 'passed', 'attempts', 'timestamp']
    list_filter = ['letter', 'passed']
    search_fields = ['student__name']
    readonly_fields = ['timestamp']


@admin.register(CVCWord)
class CVCWordAdmin(admin.ModelAdmin):
    list_display = ['word', 'arabic_meaning', 'category', 'difficulty_level', 'order']
    list_filter = ['category', 'difficulty_level']
    search_fields = ['word', 'arabic_meaning']
    ordering = ['order', 'word']


@admin.register(CVCSentence)
class CVCSentenceAdmin(admin.ModelAdmin):
    list_display = ['sentence', 'difficulty', 'time_limit', 'order']
    list_filter = ['difficulty']
    search_fields = ['sentence', 'arabic_translation']
    ordering = ['order', 'difficulty']


@admin.register(CVCStory)
class CVCStoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'difficulty', 'order']
    list_filter = ['difficulty']
    search_fields = ['title', 'content']
    ordering = ['order', 'difficulty']


@admin.register(CVCProgress)
class CVCProgressAdmin(admin.ModelAdmin):
    list_display = ['student', 'words_completed', 'sentences_completed', 'stories_completed', 'total_score']
    search_fields = ['student__name']
    readonly_fields = ['last_activity', 'created_at']
