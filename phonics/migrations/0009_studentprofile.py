# Generated manually for the accounts foundation sprint.

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("phonics", "0008_externalgame"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="StudentProfile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("student_name", models.CharField(max_length=200, verbose_name="اسم الطالب")),
                ("school", models.CharField(blank=True, max_length=200, verbose_name="المدرسة")),
                (
                    "parent_phone",
                    models.CharField(blank=True, max_length=30, verbose_name="جوال ولي الأمر"),
                ),
                ("is_premium", models.BooleanField(default=False, verbose_name="Premium user")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="student_profile",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="User",
                    ),
                ),
            ],
            options={
                "verbose_name": "Student profile",
                "verbose_name_plural": "Student profiles",
            },
        ),
    ]
