from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from phonics.models import (
    CVCReadingProgress,
    EnglishFoundationProgress,
    SoundPracticeProgress,
    StudentProfile,
    UserSubscription,
)
from phonics.views import PLAN_DIAMOND, PLAN_LEVEL_FOUR, PLAN_LEVEL_THREE, PLAN_SILVER


LOAD_TEST_EMAIL_DOMAIN = "loadtest.local"
LOAD_TEST_SCHOOL = "__LOAD_TEST__"
PLAN_BY_ROLE = {
    "silver": PLAN_SILVER,
    "diamond": PLAN_DIAMOND,
    "level3": PLAN_LEVEL_THREE,
    "level4": PLAN_LEVEL_FOUR,
}


class Command(BaseCommand):
    help = "Create isolated load-test users and subscriptions. Never use real user data."

    def add_arguments(self, parser):
        parser.add_argument("--users", type=int, default=100, help="Users per authenticated role.")
        parser.add_argument("--prefix", default="loadtest_user_", help="Safe username prefix.")
        parser.add_argument("--password", default="LoadTestPass123!", help="Shared password for generated users.")

    def handle(self, *args, **options):
        users_per_role = max(1, min(options["users"], 5000))
        prefix = options["prefix"]
        password = options["password"]
        if not prefix.startswith("loadtest_"):
            raise SystemExit("Refusing unsafe prefix. Prefix must start with 'loadtest_'.")

        roles = ["basic", "silver", "diamond", "level3", "level4"]
        now = timezone.now()
        User = get_user_model()
        created = 0
        updated = 0

        with transaction.atomic():
            for role in roles:
                for index in range(1, users_per_role + 1):
                    username = f"{prefix}{role}_{index:04d}"
                    email = f"{username}@{LOAD_TEST_EMAIL_DOMAIN}"
                    user, was_created = User.objects.get_or_create(
                        username=username,
                        defaults={
                            "email": email,
                            "first_name": "Load",
                            "last_name": f"Test {role}",
                        },
                    )
                    if was_created:
                        user.set_password(password)
                        created += 1
                    else:
                        updated += 1
                        if user.email != email:
                            user.email = email
                    user.is_active = True
                    user.save()

                    StudentProfile.objects.update_or_create(
                        user=user,
                        defaults={
                            "display_name": f"Load Test {role} {index}",
                            "student_name": f"Load Test {role} {index}",
                            "school": LOAD_TEST_SCHOOL,
                            "grade": "load-test",
                            "parent_phone": "",
                        },
                    )

                    plan_code = PLAN_BY_ROLE.get(role)
                    if plan_code:
                        UserSubscription.objects.update_or_create(
                            user=user,
                            plan_code=plan_code,
                            defaults={
                                "status": UserSubscription.Status.ACTIVE,
                                "starts_at": now - timedelta(minutes=5),
                                "expires_at": now + timedelta(days=7),
                            },
                        )

                    if role in {"silver", "diamond"}:
                        SoundPracticeProgress.objects.get_or_create(user=user)
                    if role in {"level3", "diamond"}:
                        CVCReadingProgress.objects.get_or_create(user=user)
                    if role in {"level4", "diamond"}:
                        for section in ["vocabulary", "grammar", "conversations", "common_sentences"]:
                            EnglishFoundationProgress.objects.get_or_create(user=user, section=section)

        total = users_per_role * len(roles)
        self.stdout.write(self.style.SUCCESS(
            f"Load-test data ready: total={total}, created={created}, updated={updated}, prefix={prefix}"
        ))
