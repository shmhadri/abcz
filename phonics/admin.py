from django.contrib import admin
from .models import (
    Student, LetterProgress, 
    CVCWord, CVCSentence, CVCStory, CVCProgress,
    TopGoalUnit, TopGoalVocabulary, TopGoalSentence, TopGoalQuiz
)


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


@admin.register(TopGoalUnit)
class TopGoalUnitAdmin(admin.ModelAdmin):
    list_display = ['title', 'grade', 'unit_number']
    ordering = ['grade', 'unit_number']

@admin.register(TopGoalVocabulary)
class TopGoalVocabularyAdmin(admin.ModelAdmin):
    list_display = ['word', 'arabic_meaning', 'unit', 'order']
    list_filter = ['unit']
    search_fields = ['word', 'arabic_meaning']
    ordering = ['unit', 'order']

@admin.register(TopGoalSentence)
class TopGoalSentenceAdmin(admin.ModelAdmin):
    list_display = ['english_text', 'unit', 'order']
    list_filter = ['unit']
    search_fields = ['english_text']
    ordering = ['unit', 'order']

@admin.register(TopGoalQuiz)
class TopGoalQuizAdmin(admin.ModelAdmin):
    list_display = ['question_text', 'question_type', 'unit', 'order']
    list_filter = ['unit', 'question_type']
    search_fields = ['question_text']
    ordering = ['unit', 'order']
