from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin as DjangoGroupAdmin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import Group, User

from .admin_audit import log_admin_action
from .models import (
    Student, StudentProfile, LetterProgress,
    BirdTutorProgress, BirdReviewItem, SoundPracticeProgress, ExternalGame,
    CVCWord, CVCSentence, CVCStory, CVCProgress, CVCReadingProgress,
    EnglishFoundationProgress, UserSubscription, PaymentOrder, PaymentWebhookEvent,
    PaymentActivationReview, AdminAuditLog,
    TopGoalUnit, TopGoalVocabulary, TopGoalSentence, TopGoalQuiz
)


class ViewOnlyAdminMixin:
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        return {}


class ProtectedDeleteAdminMixin:
    def has_delete_permission(self, request, obj=None):
        return False


admin.site.unregister(User)
admin.site.unregister(Group)


@admin.register(User)
class AuditedUserAdmin(DjangoUserAdmin):
    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        fields = ("is_active", "is_staff", "is_superuser")
        before = User.objects.filter(pk=obj.pk).values(*fields).first() if change else {}
        super().save_model(request, obj, form, change)
        after = {field: getattr(obj, field) for field in fields}
        if before != after:
            log_admin_action(
                request,
                action="user_security_changed",
                target=obj,
                before_status=before,
                after_status=after,
                note="Changed account security flags through Django Admin.",
            )

    def save_related(self, request, form, formsets, change):
        user = form.instance
        before = {
            "groups": sorted(user.groups.values_list("name", flat=True)),
            "permissions": sorted(user.user_permissions.values_list("codename", flat=True)),
        }
        super().save_related(request, form, formsets, change)
        after = {
            "groups": sorted(user.groups.values_list("name", flat=True)),
            "permissions": sorted(user.user_permissions.values_list("codename", flat=True)),
        }
        if before != after:
            log_admin_action(
                request,
                action="user_permissions_changed",
                target=user,
                before_status=before,
                after_status=after,
                note="Changed staff groups or direct permissions through Django Admin.",
            )


@admin.register(Group)
class AuditedGroupAdmin(DjangoGroupAdmin):
    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        obj._audit_permissions_before = (
            sorted(obj.permissions.values_list("codename", flat=True)) if obj.pk else []
        )
        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        group = form.instance
        before = getattr(group, "_audit_permissions_before", [])
        super().save_related(request, form, formsets, change)
        after = sorted(group.permissions.values_list("codename", flat=True))
        if before != after:
            log_admin_action(
                request,
                action="group_permissions_changed",
                target=group,
                before_status={"permissions": before},
                after_status={"permissions": after},
                note="Changed role permissions through Django Admin.",
            )


@admin.register(Student)
class StudentAdmin(ProtectedDeleteAdminMixin, admin.ModelAdmin):
    list_display = ['name', 'school', 'total_score', 'letters_completed', 'created_at']
    search_fields = ['name', 'school']
    list_filter = ['created_at', 'letters_completed']
    readonly_fields = ['total_score', 'letters_completed', 'created_at', 'updated_at']


@admin.register(StudentProfile)
class StudentProfileAdmin(ProtectedDeleteAdminMixin, admin.ModelAdmin):
    list_display = ['user', 'display_name', 'student_name', 'city', 'masked_parent_phone', 'is_premium', 'is_vip', 'updated_at']
    search_fields = ['user__username', 'user__email', 'display_name', 'student_name', 'city', 'parent_phone']
    list_filter = ['is_premium', 'is_vip', 'created_at']
    readonly_fields = ['user', 'is_premium', 'is_vip', 'created_at', 'updated_at']
    list_select_related = ['user']

    @admin.display(description='Parent phone')
    def masked_parent_phone(self, obj):
        value = str(obj.parent_phone or '')
        return f"••••{value[-4:]}" if value else '—'


@admin.register(BirdTutorProgress)
class BirdTutorProgressAdmin(ViewOnlyAdminMixin, admin.ModelAdmin):
    list_display = ['user', 'xp', 'total_questions', 'correct_answers', 'wrong_answers', 'last_used_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    list_select_related = ['user']


@admin.register(BirdReviewItem)
class BirdReviewItemAdmin(ViewOnlyAdminMixin, admin.ModelAdmin):
    list_display = ['user', 'letter', 'word', 'question_type', 'mistakes_count', 'success_count', 'mastered', 'last_reviewed_at']
    list_filter = ['letter', 'question_type', 'mastered']
    search_fields = ['user__username', 'user__email', 'word']
    readonly_fields = ['created_at', 'updated_at']
    list_select_related = ['user']


@admin.register(EnglishFoundationProgress)
class EnglishFoundationProgressAdmin(ViewOnlyAdminMixin, admin.ModelAdmin):
    list_display = ['user', 'section', 'points', 'actions_count', 'completed', 'last_activity_type', 'last_activity_at']
    list_filter = ['section', 'completed', 'last_activity_at']
    search_fields = ['user__username', 'user__email', 'section']
    readonly_fields = ['created_at', 'updated_at']
    list_select_related = ['user']


@admin.register(UserSubscription)
class UserSubscriptionAdmin(ViewOnlyAdminMixin, admin.ModelAdmin):
    list_display = ['user', 'plan_code', 'status', 'starts_at', 'expires_at', 'activated_by_payment', 'updated_at']
    list_filter = ['plan_code', 'status', 'starts_at', 'expires_at']
    search_fields = ['user__username', 'user__email', 'plan_code']
    readonly_fields = [field.name for field in UserSubscription._meta.fields]
    list_select_related = ['user', 'activated_by_payment']
    date_hierarchy = 'created_at'
    list_per_page = 50


@admin.register(PaymentOrder)
class PaymentOrderAdmin(ViewOnlyAdminMixin, admin.ModelAdmin):
    list_display = [
        'reference', 'user', 'plan_code', 'method', 'status', 'amount_sar',
        'created_at', 'paid_at', 'activated_at', 'short_provider_payment_id'
    ]
    list_filter = ['status', 'method', 'plan_code', 'created_at', 'paid_at', 'activated_at']
    search_fields = ['=id', 'user__username', 'user__email', 'plan_code', 'provider_payment_id']
    readonly_fields = [field.name for field in PaymentOrder._meta.fields] + [
        'reference', 'short_provider_payment_id'
    ]
    actions = []
    list_select_related = ['user']
    date_hierarchy = 'created_at'
    list_per_page = 50

    @admin.display(description='Provider payment ID')
    def short_provider_payment_id(self, obj):
        value = str(obj.provider_payment_id or obj.moyasar_payment_id or '')
        if not value:
            return '—'
        return f"{value[:4]}…{value[-4:]}" if len(value) > 10 else '••••'

    def _is_support_agent(self, request):
        return (
            not request.user.is_superuser
            and request.user.groups.filter(name='Support Agent').exists()
        )

    def get_list_display(self, request):
        if self._is_support_agent(request):
            return ['reference', 'user', 'plan_code', 'status', 'failure_code', 'created_at']
        return super().get_list_display(request)

    def get_list_filter(self, request):
        if self._is_support_agent(request):
            return ['status', 'plan_code', 'created_at']
        return super().get_list_filter(request)

    def get_search_fields(self, request):
        if self._is_support_agent(request):
            return ['=id', 'user__username', 'user__email', 'plan_code']
        return super().get_search_fields(request)

    def get_fields(self, request, obj=None):
        if self._is_support_agent(request):
            return [
                'reference', 'user', 'plan_code', 'status', 'failure_code',
                'failure_message', 'created_at', 'paid_at', 'activated_at',
            ]
        return super().get_fields(request, obj)

@admin.register(PaymentWebhookEvent)
class PaymentWebhookEventAdmin(ViewOnlyAdminMixin, admin.ModelAdmin):
    list_display = [
        'provider', 'event_id', 'event_type', 'payment_reference',
        'processing_status', 'failure_code', 'received_at', 'processed_at',
    ]
    list_filter = ['processing_status', 'event_type', 'received_at', 'failure_code']
    search_fields = [
        'event_id', '=payment_order__id', 'payment_order__provider_payment_id',
        'payment_order__user__username', 'payment_order__user__email',
    ]
    readonly_fields = [field.name for field in PaymentWebhookEvent._meta.fields]
    list_select_related = ['payment_order', 'payment_order__user']
    date_hierarchy = 'received_at'
    list_per_page = 50

    @admin.display(description='Payment')
    def payment_reference(self, obj):
        return obj.payment_order.reference if obj.payment_order_id else '—'


@admin.register(PaymentActivationReview)
class PaymentActivationReviewAdmin(ViewOnlyAdminMixin, admin.ModelAdmin):
    list_display = ['payment_order', 'reason_code', 'status', 'created_at', 'resolved_at']
    list_filter = ['reason_code', 'status', 'created_at']
    search_fields = ['payment_order__id', 'payment_order__user__username']
    readonly_fields = [field.name for field in PaymentActivationReview._meta.fields]
    list_select_related = ['payment_order', 'payment_order__user']
    list_per_page = 50


@admin.register(SoundPracticeProgress)
class SoundPracticeProgressAdmin(ViewOnlyAdminMixin, admin.ModelAdmin):
    list_display = ['user', 'quiz_attempts', 'quiz_correct', 'worksheet_downloads', 'last_used_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = [field.name for field in SoundPracticeProgress._meta.fields]
    list_select_related = ['user']
    list_per_page = 50


@admin.register(CVCReadingProgress)
class CVCReadingProgressAdmin(ViewOnlyAdminMixin, admin.ModelAdmin):
    list_display = ['user', 'cvc_mastery_percentage', 'stories_completed', 'fluency_score', 'updated_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = [field.name for field in CVCReadingProgress._meta.fields]
    list_select_related = ['user']
    date_hierarchy = 'updated_at'
    list_per_page = 50


@admin.register(LetterProgress)
class LetterProgressAdmin(ViewOnlyAdminMixin, admin.ModelAdmin):
    list_display = ['user', 'student', 'letter', 'total_score', 'score', 'completed', 'passed', 'attempts', 'completed_at', 'last_updated_at']
    list_filter = ['letter', 'completed', 'passed']
    search_fields = ['user__username', 'user__email', 'student__name']
    readonly_fields = ['timestamp', 'created_at', 'last_updated_at']
    list_select_related = ['user', 'student']


@admin.register(ExternalGame)
class ExternalGameAdmin(admin.ModelAdmin):
    list_display = ['letter', 'title', 'is_premium', 'is_active', 'review_status', 'updated_at']
    list_filter = ['letter', 'is_premium', 'is_active', 'review_status']
    search_fields = ['letter', 'title', 'activity_url', 'notes']
    list_editable = ['is_active', 'review_status']
    readonly_fields = ['created_at', 'updated_at']
    fields = [
        'letter',
        'title',
        'activity_url',
        'is_premium',
        'is_active',
        'review_status',
        'notes',
        'created_at',
        'updated_at',
    ]


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
class CVCProgressAdmin(ViewOnlyAdminMixin, admin.ModelAdmin):
    list_display = ['student', 'words_completed', 'sentences_completed', 'stories_completed', 'total_score']
    search_fields = ['student__name']
    readonly_fields = ['last_activity', 'created_at']
    list_select_related = ['student']


@admin.register(AdminAuditLog)
class AdminAuditLogAdmin(ViewOnlyAdminMixin, admin.ModelAdmin):
    list_display = ['created_at', 'actor', 'action', 'target_model', 'target_id', 'short_target']
    list_filter = ['action', 'target_model', 'created_at']
    search_fields = ['actor__username', 'action', 'target_model', 'target_id', 'target_repr']
    readonly_fields = [field.name for field in AdminAuditLog._meta.fields]
    list_select_related = ['actor']
    date_hierarchy = 'created_at'
    list_per_page = 50

    @admin.display(description='Target')
    def short_target(self, obj):
        value = str(obj.target_repr or '')
        return value if len(value) <= 60 else f"{value[:57]}…"


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
