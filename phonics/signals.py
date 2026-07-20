from __future__ import annotations

from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in
from django.db import transaction
from django.db.models.signals import m2m_changed, post_delete, post_save
from django.dispatch import receiver

from .cache_helpers import invalidate_user_subscription_cache
from .models import StudentProfile, UserSubscription


def _invalidate_on_commit(user_id: int | None) -> None:
    if not user_id:
        return
    transaction.on_commit(lambda: invalidate_user_subscription_cache(user_id))


@receiver(post_save, sender=UserSubscription)
@receiver(post_delete, sender=UserSubscription)
def invalidate_subscription_cache(sender, instance, **kwargs):
    _invalidate_on_commit(instance.user_id)


@receiver(post_save, sender=StudentProfile)
@receiver(post_delete, sender=StudentProfile)
def invalidate_profile_subscription_cache(sender, instance, **kwargs):
    _invalidate_on_commit(instance.user_id)


@receiver(m2m_changed, sender=get_user_model().groups.through)
def invalidate_group_membership_cache(sender, instance, action, reverse, pk_set, **kwargs):
    if action not in {"post_add", "post_remove", "post_clear", "pre_clear"}:
        return

    if reverse:
        if pk_set:
            user_ids = list(pk_set)
        elif action == "pre_clear":
            user_ids = list(instance.user_set.values_list("pk", flat=True))
        else:
            user_ids = []
    else:
        user_ids = [instance.pk]

    for user_id in user_ids:
        _invalidate_on_commit(user_id)


@receiver(user_logged_in)
def synchronize_subscription_state_on_login(sender, request, user, **kwargs):
    from .subscriptions import synchronize_user_subscription_compatibility

    synchronize_user_subscription_compatibility(user)
