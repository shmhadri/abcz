from datetime import timedelta

from django.utils import timezone

from phonics.models import UserSubscription


def grant_active_subscription(user, plan_code, *, starts_at=None, expires_at=None):
    now = timezone.now()
    return UserSubscription.objects.update_or_create(
        user=user,
        plan_code=plan_code,
        defaults={
            "status": UserSubscription.Status.ACTIVE,
            "starts_at": starts_at or (now - timedelta(minutes=1)),
            "expires_at": expires_at or (now + timedelta(days=30)),
        },
    )[0]
