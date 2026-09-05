from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class UnitProgress(models.Model):
    class Status(models.TextChoices):
        STARTED = "started", "Started"
        DEVELOPING = "developing", "Developing"
        MASTERED = "mastered", "Mastered"
        EXCELLENT = "excellent", "Excellent"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="english_unit_progress")
    unit_code = models.CharField(max_length=12)
    score = models.PositiveSmallIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.STARTED)
    skill_scores = models.JSONField(default=dict, blank=True)
    attempts = models.PositiveIntegerField(default=0)
    last_activity_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("unit_code",)
        constraints = [models.UniqueConstraint(fields=("user", "unit_code"), name="english_path_unique_user_unit")]

    def __str__(self):
        return f"{self.user_id}: {self.unit_code} ({self.score}%)"


class ReviewItem(models.Model):
    class Skill(models.TextChoices):
        VOCABULARY = "vocabulary", "Vocabulary"
        GRAMMAR = "grammar", "Grammar"
        READING = "reading", "Reading"
        LISTENING = "listening", "Listening"
        SPEAKING = "speaking", "Speaking"
        WRITING = "writing", "Writing"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="english_review_items")
    unit_code = models.CharField(max_length=12)
    item_key = models.CharField(max_length=80)
    prompt = models.CharField(max_length=300)
    answer = models.CharField(max_length=300)
    skill = models.CharField(max_length=16, choices=Skill.choices)
    subskill = models.CharField(max_length=64, default="general")
    difficulty = models.PositiveSmallIntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(5)])
    error_count = models.PositiveIntegerField(default=1)
    mastery = models.PositiveSmallIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(5)])
    interval_days = models.PositiveSmallIntegerField(default=1)
    next_review_at = models.DateTimeField()
    active = models.BooleanField(default=True)
    last_seen_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("next_review_at", "id")
        constraints = [models.UniqueConstraint(fields=("user", "item_key"), name="english_path_unique_review_item")]
        indexes = [models.Index(fields=("user", "active", "next_review_at"), name="english_review_due_idx")]

    def __str__(self):
        return f"{self.user_id}: {self.item_key}"


class AssessmentResult(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="english_assessments")
    assessment_type = models.CharField(max_length=24, default="diagnostic")
    level = models.CharField(max_length=16, blank=True)
    score = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    skill_scores = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)


class ReviewSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="english_review_sessions")
    item_ids = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)
