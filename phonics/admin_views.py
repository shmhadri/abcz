from datetime import timedelta
from decimal import Decimal

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q, Sum
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET

from .models import PaymentOrder, PaymentWebhookEvent, UserSubscription


@never_cache
@require_GET
def operations_dashboard(request):
    if not (
        request.user.is_superuser
        or request.user.has_perm("phonics.view_operations_dashboard")
    ):
        raise PermissionDenied

    now = timezone.now()
    day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = now - timedelta(days=7)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_30_days = now - timedelta(days=30)
    user_model = get_user_model()

    paid_orders = PaymentOrder.objects.filter(
        status=PaymentOrder.Status.PAID,
        activated_at__isnull=False,
    )
    paid_last_30_days = paid_orders.filter(paid_at__gte=last_30_days)
    registered_last_30_days = user_model.objects.filter(date_joined__gte=last_30_days).count()
    converted_users = paid_last_30_days.values("user_id").distinct().count()
    conversion_rate = (
        round((converted_users / registered_last_30_days) * 100, 1)
        if registered_last_30_days
        else 0
    )
    top_plan = (
        paid_last_30_days.values("plan_code")
        .annotate(total=Count("id"))
        .order_by("-total", "plan_code")
        .first()
    )

    context = admin.site.each_context(request)
    context.update({
        "title": "Operations dashboard",
        "users_today": user_model.objects.filter(date_joined__gte=day_start).count(),
        "users_week": user_model.objects.filter(date_joined__gte=week_start).count(),
        "users_month": user_model.objects.filter(date_joined__gte=month_start).count(),
        "new_subscriptions": UserSubscription.objects.filter(
            status=UserSubscription.Status.ACTIVE,
            created_at__gte=month_start,
        ).count(),
        "revenue_total": paid_orders.aggregate(total=Sum("amount_sar"))["total"] or Decimal("0.00"),
        "top_plan": top_plan,
        "conversion_rate": conversion_rate,
        "attribution_available": False,
        "can_view_sensitive_operations": request.user.is_superuser,
    })

    if request.user.is_superuser:
        pending_statuses = {
            PaymentOrder.Status.PENDING,
            PaymentOrder.Status.CREATING_INVOICE,
            PaymentOrder.Status.INVOICE_CREATION_UNKNOWN,
            PaymentOrder.Status.INITIATED,
        }
        context.update({
            "active_subscriptions": UserSubscription.objects.filter(
                status=UserSubscription.Status.ACTIVE,
                starts_at__lte=now,
                expires_at__gt=now,
            ).count(),
            "expired_subscriptions": UserSubscription.objects.filter(
                Q(status=UserSubscription.Status.EXPIRED) | Q(expires_at__lte=now)
            ).count(),
            "revenue_today": paid_orders.filter(paid_at__gte=day_start).aggregate(
                total=Sum("amount_sar")
            )["total"] or Decimal("0.00"),
            "revenue_month": paid_orders.filter(paid_at__gte=month_start).aggregate(
                total=Sum("amount_sar")
            )["total"] or Decimal("0.00"),
            "successful_orders": paid_orders.count(),
            "failed_orders": PaymentOrder.objects.filter(status=PaymentOrder.Status.FAILED).count(),
            "pending_orders": PaymentOrder.objects.filter(status__in=pending_statuses).count(),
            "stale_initiated_orders": PaymentOrder.objects.filter(
                status=PaymentOrder.Status.INITIATED,
                created_at__lt=now - timedelta(minutes=30),
            ).count(),
            "webhook_failures": PaymentWebhookEvent.objects.filter(
                processing_status__in={
                    PaymentWebhookEvent.ProcessingStatus.FAILED,
                    PaymentWebhookEvent.ProcessingStatus.MISMATCH,
                }
            ).count(),
            "latest_orders": PaymentOrder.objects.select_related("user").order_by("-created_at")[:20],
            "latest_users": user_model.objects.order_by("-date_joined")[:20],
        })

    return render(request, "admin/operations_dashboard.html", context)
