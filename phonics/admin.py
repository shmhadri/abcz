from django.contrib import admin
from django.utils import timezone
from .models import (
    Student, StudentProfile, LetterProgress,
    BirdTutorProgress, BirdReviewItem, ExternalGame,
    CVCWord, CVCSentence, CVCStory, CVCProgress,
    EnglishFoundationProgress, UserSubscription, PaymentOrder, PaymentWebhookEvent,
    PaymentActivationReview,
    BankTransferProof, activate_subscription_from_payment,
    TopGoalUnit, TopGoalVocabulary, TopGoalSentence, TopGoalQuiz
)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['name', 'school', 'total_score', 'letters_completed', 'created_at']
    search_fields = ['name', 'school']
    list_filter = ['created_at', 'letters_completed']
    readonly_fields = ['total_score', 'letters_completed', 'created_at', 'updated_at']


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'display_name', 'student_name', 'city', 'parent_phone', 'is_premium', 'is_vip', 'updated_at']
    search_fields = ['user__username', 'user__email', 'display_name', 'student_name', 'city', 'parent_phone']
    list_filter = ['is_premium', 'is_vip', 'created_at']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(BirdTutorProgress)
class BirdTutorProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'xp', 'total_questions', 'correct_answers', 'wrong_answers', 'last_used_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(BirdReviewItem)
class BirdReviewItemAdmin(admin.ModelAdmin):
    list_display = ['user', 'letter', 'word', 'question_type', 'mistakes_count', 'success_count', 'mastered', 'last_reviewed_at']
    list_filter = ['letter', 'question_type', 'mastered']
    search_fields = ['user__username', 'user__email', 'word']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(EnglishFoundationProgress)
class EnglishFoundationProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'section', 'points', 'actions_count', 'completed', 'last_activity_type', 'last_activity_at']
    list_filter = ['section', 'completed', 'last_activity_at']
    search_fields = ['user__username', 'user__email', 'section']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan_code', 'status', 'starts_at', 'expires_at', 'activated_by_payment', 'updated_at']
    list_filter = ['plan_code', 'status', 'starts_at', 'expires_at']
    search_fields = ['user__username', 'user__email', 'plan_code']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(PaymentOrder)
class PaymentOrderAdmin(admin.ModelAdmin):
    list_display = [
        'reference', 'user', 'plan_code', 'amount_sar', 'currency', 'method',
        'provider', 'status', 'activated_at', 'created_at'
    ]
    list_filter = ['plan_code', 'method', 'provider', 'status', 'created_at']
    search_fields = ['user__username', 'user__email', 'plan_code', 'provider_payment_id']
    readonly_fields = [
        'reference', 'amount_halalas', 'currency', 'provider_payment_id',
        'moyasar_invoice_id', 'moyasar_payment_id', 'payment_environment',
        'idempotency_key', 'invoice_creation_token', 'invoice_creation_started_at',
        'checkout_url', 'metadata', 'paid_at', 'failed_at',
        'canceled_at', 'failure_code', 'failure_message', 'activated_at',
        'created_at', 'updated_at'
    ]
    actions = ['approve_bank_transfer', 'reject_bank_transfer']

    @admin.action(description='Approve bank transfer and activate subscription')
    def approve_bank_transfer(self, request, queryset):
        approved = 0
        skipped = 0
        for order in queryset:
            if order.method != PaymentOrder.Method.BANK_TRANSFER:
                skipped += 1
                continue
            order.status = PaymentOrder.Status.BANK_APPROVED
            order.provider_status = 'approved_by_admin'
            order.save(update_fields=['status', 'provider_status', 'updated_at'])
            order.bank_proofs.filter(status=BankTransferProof.Status.PENDING_REVIEW).update(
                status=BankTransferProof.Status.APPROVED,
                reviewed_by=request.user,
                reviewed_at=timezone.now(),
            )
            activate_subscription_from_payment(order)
            approved += 1
        self.message_user(request, f'Approved {approved} bank transfer order(s). Skipped {skipped}.')

    @admin.action(description='Reject bank transfer')
    def reject_bank_transfer(self, request, queryset):
        rejected = 0
        for order in queryset.filter(method=PaymentOrder.Method.BANK_TRANSFER):
            if order.activated_at:
                continue
            order.status = PaymentOrder.Status.BANK_REJECTED
            order.provider_status = 'rejected_by_admin'
            order.save(update_fields=['status', 'provider_status', 'updated_at'])
            order.bank_proofs.filter(status=BankTransferProof.Status.PENDING_REVIEW).update(
                status=BankTransferProof.Status.REJECTED,
                reviewed_by=request.user,
                reviewed_at=timezone.now(),
            )
            rejected += 1
        self.message_user(request, f'Rejected {rejected} bank transfer order(s).')


@admin.register(PaymentWebhookEvent)
class PaymentWebhookEventAdmin(admin.ModelAdmin):
    list_display = [
        'event_id', 'event_type', 'payment_environment', 'payment_order',
        'processing_status', 'received_at', 'processed_at',
    ]
    list_filter = ['provider', 'event_type', 'payment_environment', 'processing_status', 'received_at']
    search_fields = ['event_id', 'payment_order__id', 'payment_order__user__username']
    readonly_fields = [
        'provider', 'event_id', 'event_type', 'payment_environment', 'payment_order',
        'received_at', 'processed_at', 'processing_status', 'failure_code', 'payload_hash',
    ]


@admin.register(PaymentActivationReview)
class PaymentActivationReviewAdmin(admin.ModelAdmin):
    list_display = ['payment_order', 'reason_code', 'status', 'created_at', 'resolved_at']
    list_filter = ['reason_code', 'status', 'created_at']
    search_fields = ['payment_order__id', 'payment_order__user__username']
    readonly_fields = ['payment_order', 'reason_code', 'created_at']


@admin.register(BankTransferProof)
class BankTransferProofAdmin(admin.ModelAdmin):
    list_display = ['payment_order', 'user', 'sender_name', 'bank_name', 'amount_sar', 'status', 'reviewed_by', 'created_at']
    list_filter = ['status', 'bank_name', 'created_at', 'reviewed_at']
    search_fields = ['user__username', 'user__email', 'sender_name', 'transfer_reference', 'payment_order__plan_code']
    readonly_fields = ['created_at']


@admin.register(LetterProgress)
class LetterProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'student', 'letter', 'total_score', 'score', 'completed', 'passed', 'attempts', 'completed_at', 'last_updated_at']
    list_filter = ['letter', 'completed', 'passed']
    search_fields = ['user__username', 'user__email', 'student__name']
    readonly_fields = ['timestamp', 'created_at', 'last_updated_at']


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
