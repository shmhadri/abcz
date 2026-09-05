from django.contrib import admin

from english_path.models import AssessmentResult, ReviewItem, ReviewSession, UnitProgress


@admin.register(UnitProgress)
class UnitProgressAdmin(admin.ModelAdmin):
    list_display = ("user", "unit_code", "score", "status", "attempts", "last_activity_at")
    list_filter = ("status", "unit_code")
    search_fields = ("user__username", "user__email", "unit_code")


@admin.register(ReviewItem)
class ReviewItemAdmin(admin.ModelAdmin):
    list_display = ("user", "unit_code", "skill", "mastery", "active", "next_review_at")
    list_filter = ("skill", "active")
    search_fields = ("user__username", "item_key", "prompt")


@admin.register(AssessmentResult)
class AssessmentResultAdmin(admin.ModelAdmin):
    list_display = ("user", "assessment_type", "level", "score", "created_at")
    list_filter = ("assessment_type", "level")


@admin.register(ReviewSession)
class ReviewSessionAdmin(admin.ModelAdmin):
    list_display = ("user", "created_at", "completed_at")
    readonly_fields = ("item_ids", "created_at")
