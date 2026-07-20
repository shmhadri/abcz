from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from zoneinfo import ZoneInfo

from django.contrib.auth.models import Group
from django.db.models import Q
from django.utils import timezone

from .plans import (
    ADDON_PLAN_CODES,
    PAID_MAIN_PLAN_CODES,
    PLAN_BASIC,
    PLAN_CATALOG,
    PLAN_DIAMOND,
    PLAN_FREE,
    PLAN_VIP,
    get_plan_definition,
    main_plan_rank,
    normalize_plan_code,
)


ACTIVE_STATUS = "active"
PENDING_PAYMENT_STATUSES = {
    "pending",
    "creating_invoice",
    "invoice_creation_unknown",
    "initiated",
    "awaiting_bank_review",
    "paid_requires_review",
}
COMPATIBILITY_GROUPS = {
    "basic": "Basic",
    "silver": "Silver",
    "vip": "VIP",
    "diamond": "Diamond",
}


class PurchaseNotAllowed(Exception):
    def __init__(self, code: str, message: str):
        self.code = code
        super().__init__(message)


@dataclass(frozen=True)
class PurchaseQuote:
    target_plan_code: str
    operation_type: str
    from_plan_code: str
    original_price: Decimal
    target_price: Decimal
    amount_due: Decimal
    current_expires_at: object = None
    ui_state: str = "purchase"
    ui_label: str = "اشترك الآن"


@dataclass(frozen=True)
class EntitlementSnapshot:
    main_subscription: object
    addon_subscriptions: tuple
    plan_codes: frozenset
    entitlements: frozenset


def _active_subscription_queryset(user, *, now=None, lock=False):
    from .models import UserSubscription

    now = now or timezone.now()
    queryset = UserSubscription.objects.filter(
        user=user,
        status=UserSubscription.Status.ACTIVE,
        starts_at__lte=now,
        expires_at__gt=now,
    )
    if lock:
        queryset = queryset.select_for_update()
    return queryset


def _select_main_subscription(subscriptions):
    main = [s for s in subscriptions if s.plan_code in PAID_MAIN_PLAN_CODES]
    if not main:
        return None
    return max(main, key=lambda s: (main_plan_rank(s.plan_code), s.expires_at, s.pk))


def get_active_main_subscription(user, *, now=None, lock=False):
    subscriptions = list(_active_subscription_queryset(user, now=now, lock=lock))
    return _select_main_subscription(subscriptions)


def get_active_addon_subscriptions(user, *, now=None, lock=False):
    return tuple(
        _active_subscription_queryset(user, now=now, lock=lock)
        .filter(plan_code__in=ADDON_PLAN_CODES)
        .order_by("plan_code", "expires_at")
    )


def synchronize_user_subscription_compatibility(user, *, snapshot=None) -> None:
    if not getattr(user, "is_authenticated", False):
        return

    from .models import StudentProfile

    snapshot = snapshot or get_user_entitlements(user, synchronize=False)
    desired_group = (
        COMPATIBILITY_GROUPS.get(snapshot.main_subscription.plan_code)
        if snapshot.main_subscription else None
    )
    paid_groups = Group.objects.filter(name__in=COMPATIBILITY_GROUPS.values())
    current_paid_names = set(user.groups.filter(pk__in=paid_groups).values_list("name", flat=True))
    desired_names = {desired_group} if desired_group else set()
    remove_names = current_paid_names - desired_names
    if remove_names:
        user.groups.remove(*paid_groups.filter(name__in=remove_names))
    if desired_group and desired_group not in current_paid_names:
        group, _ = Group.objects.get_or_create(name=desired_group)
        user.groups.add(group)

    rank = main_plan_rank(snapshot.main_subscription.plan_code) if snapshot.main_subscription else 0
    profile, _ = StudentProfile.objects.get_or_create(
        user=user,
        defaults={
            "display_name": user.get_full_name() or user.username,
            "student_name": user.get_full_name() or user.username,
            "school": "",
            "parent_phone": "",
        },
    )
    premium = rank >= main_plan_rank(PLAN_BASIC)
    vip = rank >= main_plan_rank(PLAN_VIP)
    update_fields = []
    if profile.is_premium != premium:
        profile.is_premium = premium
        update_fields.append("is_premium")
    if profile.is_vip != vip:
        profile.is_vip = vip
        update_fields.append("is_vip")
    if update_fields:
        update_fields.append("updated_at")
        profile.save(update_fields=update_fields)


def get_user_entitlements(user, *, now=None, synchronize=True) -> EntitlementSnapshot:
    if not getattr(user, "is_authenticated", False):
        return EntitlementSnapshot(None, (), frozenset(), frozenset())

    subscriptions = list(_active_subscription_queryset(user, now=now))
    main_subscription = _select_main_subscription(subscriptions)
    addons = tuple(s for s in subscriptions if s.plan_code in ADDON_PLAN_CODES)
    plan_codes = set()
    entitlements = set()
    if main_subscription:
        plan_codes.add(main_subscription.plan_code)
        main_plan = PLAN_CATALOG[main_subscription.plan_code]
        entitlements.update(main_plan["features"])
        plan_codes.update(main_plan["included_addons"])
    for addon in addons:
        plan_codes.add(addon.plan_code)
        entitlements.update(PLAN_CATALOG[addon.plan_code]["features"])
    snapshot = EntitlementSnapshot(
        main_subscription,
        addons,
        frozenset(plan_codes),
        frozenset(entitlements),
    )
    if synchronize:
        synchronize_user_subscription_compatibility(user, snapshot=snapshot)
    return snapshot


def user_has_entitlement(user, entitlement_code: str) -> bool:
    return entitlement_code in get_user_entitlements(user).entitlements


def quote_plan_purchase(user, target_plan_code: str, *, now=None, lock=False) -> PurchaseQuote:
    from .models import PaymentOrder, UserSubscription

    now = now or timezone.now()
    target_code = normalize_plan_code(target_plan_code)
    target = get_plan_definition(target_code)
    if not target or target_code == PLAN_FREE:
        raise PurchaseNotAllowed("invalid_plan", "هذه الباقة غير متاحة للشراء.")

    active = list(_active_subscription_queryset(user, now=now, lock=lock))
    current_main = _select_main_subscription(active)
    active_addons = {s.plan_code: s for s in active if s.plan_code in ADDON_PLAN_CODES}
    expired_target_query = UserSubscription.objects.filter(user=user, plan_code=target_code).filter(
        Q(status=UserSubscription.Status.EXPIRED)
        | Q(status=UserSubscription.Status.ACTIVE, expires_at__lte=now)
    )
    if lock:
        expired_target_query = expired_target_query.select_for_update()
    expired_target = expired_target_query.order_by("-expires_at", "-updated_at").first()
    pending_exists = PaymentOrder.objects.filter(
        user=user,
        to_plan_code=target_code,
        status__in=PENDING_PAYMENT_STATUSES,
    ).exists()

    target_price = Decimal(target["price"])
    if target["category"] == "addon":
        if current_main and current_main.plan_code == PLAN_DIAMOND:
            raise PurchaseNotAllowed("included_in_diamond", "هذه الإضافة مشمولة في باقتك الحالية.")
        current_addon = active_addons.get(target_code)
        if current_addon:
            raise PurchaseNotAllowed(
                "active_subscription",
                "أنت مشترك حاليًا في هذه الإضافة. يظهر التجديد بعد انتهاء الاشتراك.",
            )
        if expired_target:
            return PurchaseQuote(
                target_code,
                "renewal",
                target_code,
                target_price,
                target_price,
                target_price,
                expired_target.expires_at,
                "payment_pending" if pending_exists else "renewal",
                "عملية دفع قيد الاستكمال" if pending_exists else "تجديد",
            )
        return PurchaseQuote(
            target_code,
            "purchase",
            "",
            Decimal("0.00"),
            target_price,
            target_price,
            None,
            "payment_pending" if pending_exists else "purchase",
            "عملية دفع قيد الاستكمال" if pending_exists else "اشترك الآن",
        )

    if current_main:
        current_code = current_main.plan_code
        current_plan = PLAN_CATALOG[current_code]
        if target_code == current_code:
            raise PurchaseNotAllowed(
                "active_subscription",
                "أنت مشترك حاليًا في هذه الباقة. يظهر التجديد بعد انتهاء الاشتراك.",
            )
        if int(target["rank"]) < int(current_plan["rank"]):
            raise PurchaseNotAllowed("lower_main_plan", "لا يمكن شراء باقة أقل من باقتك الحالية.")
        amount_due = target_price - Decimal(current_plan["price"])
        if amount_due <= Decimal("0.00"):
            raise PurchaseNotAllowed("invalid_upgrade_amount", "تعذر حساب مبلغ الترقية.")
        return PurchaseQuote(
            target_code,
            "upgrade",
            current_code,
            Decimal(current_plan["price"]),
            target_price,
            amount_due,
            current_main.expires_at,
            "payment_pending" if pending_exists else "upgrade",
            "عملية دفع قيد الاستكمال" if pending_exists else "ترقية",
        )

    if expired_target:
        return PurchaseQuote(
            target_code,
            "renewal",
            target_code,
            target_price,
            target_price,
            target_price,
            expired_target.expires_at,
            "payment_pending" if pending_exists else "renewal",
            "عملية دفع قيد الاستكمال" if pending_exists else "تجديد",
        )

    return PurchaseQuote(
        target_code,
        "purchase",
        "",
        Decimal("0.00"),
        target_price,
        target_price,
        None,
        "payment_pending" if pending_exists else "purchase",
        "عملية دفع قيد الاستكمال" if pending_exists else "اشترك الآن",
    )


def purchase_options_for_user(user) -> dict:
    options = {}
    for code in PLAN_CATALOG:
        if code == PLAN_FREE:
            continue
        try:
            quote = quote_plan_purchase(user, code)
        except PurchaseNotAllowed as exc:
            if exc.code == "included_in_diamond":
                label = "مشمولة في باقتك الحالية"
            elif exc.code == "active_subscription":
                label = "مشترك حاليًا"
            else:
                label = "غير متاحة"
            options[code] = {
                "allowed": False,
                "state": exc.code,
                "label": label,
                "message": str(exc),
            }
        else:
            options[code] = {
                "allowed": True,
                "state": quote.ui_state,
                "label": quote.ui_label,
                "amount_due": quote.amount_due,
                "operation_type": quote.operation_type,
            }
    return options


def subscription_dashboard_context(user, *, now=None) -> dict:
    from .models import PaymentOrder, UserSubscription

    now = now or timezone.now()
    snapshot = get_user_entitlements(user, now=now)
    main = snapshot.main_subscription
    addons = list(snapshot.addon_subscriptions)
    latest = (
        UserSubscription.objects.filter(user=user)
        .order_by("-expires_at", "-updated_at")
        .first()
    )
    pending_orders = list(
        PaymentOrder.objects.filter(user=user, status__in=PENDING_PAYMENT_STATUSES)
        .order_by("-created_at")[:5]
    )

    reference_subscription = main or (addons[0] if addons else latest)
    remaining_seconds = 0
    if reference_subscription and reference_subscription.expires_at:
        remaining_seconds = max(0, int((reference_subscription.expires_at - now).total_seconds()))
    remaining_days, day_remainder = divmod(remaining_seconds, 86400)
    remaining_hours = day_remainder // 3600

    if main or addons:
        status = "ending_soon" if remaining_seconds <= (3 * 86400) else "active"
    elif pending_orders:
        status = "pending_payment"
    elif latest:
        status = "expired"
    else:
        status = "none"

    riyadh = ZoneInfo("Asia/Riyadh")
    options = purchase_options_for_user(user)
    upgrades = [
        {"code": code, **option}
        for code, option in options.items()
        if option.get("allowed") and option.get("operation_type") == "upgrade"
    ]
    main_definition = PLAN_CATALOG.get(main.plan_code) if main else None
    included_addons = list(main_definition["included_addons"]) if main_definition else []
    entitlement_set = get_user_entitlements(user, now=now, synchronize=False).entitlements
    content_labels = []
    if "letters_full" in entitlement_set:
        content_labels.append("المستوى الأول: الحروف والألعاب والتقدم")
    if "sounds_full" in entitlement_set:
        content_labels.append("المستوى الثاني: الصوتيات والنطق وأوراق العمل")
    if "bird_tutor" in entitlement_set:
        content_labels.append("ميزات VIP والعصفور الذكي والتقارير المتقدمة")
    if "cvc_words" in entitlement_set:
        content_labels.append("المستوى الثالث: قراءة CVC")
    if "level_four" in entitlement_set:
        content_labels.append("المستوى الرابع")

    renew_plan_code = ""
    if (
        status == "expired"
        and latest
        and latest.plan_code in PLAN_CATALOG
        and (
            latest.status == UserSubscription.Status.EXPIRED
            or (latest.status == UserSubscription.Status.ACTIVE and latest.expires_at <= now)
        )
    ):
        renew_plan_code = latest.plan_code

    return {
        "main_subscription": main,
        "main_plan": main_definition,
        "addon_subscriptions": addons,
        "included_addons": included_addons,
        "reference_subscription": reference_subscription,
        "starts_at_riyadh": (
            timezone.localtime(reference_subscription.starts_at, riyadh)
            if reference_subscription and reference_subscription.starts_at else None
        ),
        "expires_at_riyadh": (
            timezone.localtime(reference_subscription.expires_at, riyadh)
            if reference_subscription and reference_subscription.expires_at else None
        ),
        "remaining_days": remaining_days,
        "remaining_hours": remaining_hours,
        "status": status,
        "pending_orders": pending_orders,
        "content_labels": content_labels,
        "renew_plan_code": renew_plan_code,
        "upgrades": upgrades,
    }
