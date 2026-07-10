# Generated manually for the sound practice page.

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("phonics", "0013_letterprogress_completed_letterprogress_completed_at_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="SoundPracticeProgress",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("completed_items", models.JSONField(blank=True, default=list)),
                ("quiz_attempts", models.PositiveIntegerField(default=0)),
                ("quiz_correct", models.PositiveIntegerField(default=0)),
                ("mic_attempts", models.PositiveIntegerField(default=0)),
                ("mic_success", models.PositiveIntegerField(default=0)),
                ("worksheet_downloads", models.PositiveIntegerField(default=0)),
                ("last_item", models.CharField(blank=True, max_length=80)),
                ("last_payload", models.JSONField(blank=True, default=dict)),
                ("last_used_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="sound_practice_progress",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Sound practice progress",
                "verbose_name_plural": "Sound practice progress",
            },
        ),
    ]
