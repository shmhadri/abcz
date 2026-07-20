from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from django.db.models import Count, Q
from django.utils import timezone

from phonics.models import PaymentOrder, UserSubscription
from phonics.plans import ADDON_PLAN_CODES, PAID_MAIN_PLAN_CODES, PLAN_DIAMOND


class Command(BaseCommand):
    help = "Read-only preflight for payment and subscription migrations."

    def handle(self, *args, **options):
        findings = {}
        payment_table = PaymentOrder._meta.db_table
        with connection.cursor() as cursor:
            payment_columns = {
                column.name
                for column in connection.introspection.get_table_description(cursor, payment_table)
            }

        def add(name, queryset):
            ids = list(queryset.order_by("pk").values_list("pk", flat=True))
            if ids:
                findings[name] = ids

        add("payment_amount_nonpositive", PaymentOrder.objects.filter(amount_halalas__lte=0))
        add("payment_currency_not_sar", PaymentOrder.objects.exclude(currency="SAR"))

        for field in ("moyasar_invoice_id", "moyasar_payment_id"):
            if field not in payment_columns:
                continue
            duplicate_values = (
                PaymentOrder.objects.exclude(**{f"{field}__isnull": True})
                .exclude(**{field: ""})
                .values(field)
                .annotate(total=Count("pk"))
                .filter(total__gt=1)
                .values_list(field, flat=True)
            )
            add(f"duplicate_{field}", PaymentOrder.objects.filter(**{f"{field}__in": duplicate_values}))

        snapshot_columns = {"to_plan_code", "operation_type", "amount_due", "target_price", "metadata"}
        if snapshot_columns.issubset(payment_columns):
            modern_orders = PaymentOrder.objects.filter(
                provider=PaymentOrder.Provider.MOYASAR,
                metadata__schema_version=2,
            )
            add(
                "modern_order_snapshot_missing",
                modern_orders.filter(
                    Q(to_plan_code="")
                    | Q(operation_type="")
                    | Q(amount_due__isnull=True)
                    | Q(target_price__isnull=True)
                ),
            )

        now = timezone.now()
        active = UserSubscription.objects.filter(
            status=UserSubscription.Status.ACTIVE,
            starts_at__lte=now,
            expires_at__gt=now,
        )
        overlapping_user_ids = (
            active.filter(plan_code__in=PAID_MAIN_PLAN_CODES)
            .values("user_id")
            .annotate(total=Count("pk"))
            .filter(total__gt=1)
            .values_list("user_id", flat=True)
        )
        add("overlapping_active_main", active.filter(user_id__in=overlapping_user_ids, plan_code__in=PAID_MAIN_PLAN_CODES))

        diamond_user_ids = active.filter(plan_code=PLAN_DIAMOND).values_list("user_id", flat=True)
        add("diamond_with_active_addon", active.filter(user_id__in=diamond_user_ids, plan_code__in=ADDON_PLAN_CODES))

        add(
            "paid_without_activation",
            PaymentOrder.objects.filter(status=PaymentOrder.Status.PAID, activated_at__isnull=True),
        )

        activated_missing = []
        activated_fields = ["pk", "user_id", "plan_code"]
        if "to_plan_code" in payment_columns:
            activated_fields.append("to_plan_code")
        for order in PaymentOrder.objects.filter(activated_at__isnull=False).only(*activated_fields):
            target = getattr(order, "to_plan_code", "") or order.plan_code
            if not UserSubscription.objects.filter(
                user_id=order.user_id,
                plan_code=target,
                activated_by_payment_id=order.pk,
            ).exists():
                activated_missing.append(order.pk)
        if activated_missing:
            findings["activated_without_matching_subscription"] = sorted(activated_missing)

        if findings:
            for name, ids in sorted(findings.items()):
                self.stderr.write(f"{name}: IDs {','.join(map(str, ids))}")
            raise CommandError(f"Preflight found {sum(len(ids) for ids in findings.values())} blocking record(s).")

        self.stdout.write(self.style.SUCCESS("Payment/subscription migration preflight: clean."))
