import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(
            name="AssessmentResult",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("assessment_type", models.CharField(default="diagnostic", max_length=24)),
                ("level", models.CharField(blank=True, max_length=8)),
                ("score", models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ("skill_scores", models.JSONField(default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="english_assessments", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ("-created_at",)},
        ),
        migrations.CreateModel(
            name="UnitProgress",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("unit_code", models.CharField(max_length=12)),
                ("score", models.PositiveSmallIntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ("status", models.CharField(choices=[("started", "Started"), ("developing", "Developing"), ("mastered", "Mastered"), ("excellent", "Excellent")], default="started", max_length=12)),
                ("skill_scores", models.JSONField(blank=True, default=dict)),
                ("attempts", models.PositiveIntegerField(default=0)),
                ("last_activity_at", models.DateTimeField(auto_now=True)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="english_unit_progress", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ("unit_code",)},
        ),
        migrations.CreateModel(
            name="ReviewItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("unit_code", models.CharField(max_length=12)),
                ("item_key", models.CharField(max_length=80)),
                ("prompt", models.CharField(max_length=300)),
                ("answer", models.CharField(max_length=300)),
                ("skill", models.CharField(choices=[("vocabulary", "Vocabulary"), ("grammar", "Grammar"), ("reading", "Reading"), ("listening", "Listening"), ("speaking", "Speaking"), ("writing", "Writing")], max_length=16)),
                ("mastery", models.PositiveSmallIntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(5)])),
                ("interval_days", models.PositiveSmallIntegerField(default=1)),
                ("next_review_at", models.DateTimeField()),
                ("active", models.BooleanField(default=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="english_review_items", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ("next_review_at", "id")},
        ),
        migrations.AddConstraint(model_name="unitprogress", constraint=models.UniqueConstraint(fields=("user", "unit_code"), name="english_path_unique_user_unit")),
        migrations.AddConstraint(model_name="reviewitem", constraint=models.UniqueConstraint(fields=("user", "item_key"), name="english_path_unique_review_item")),
        migrations.AddIndex(model_name="reviewitem", index=models.Index(fields=["user", "active", "next_review_at"], name="english_review_due_idx")),
    ]
