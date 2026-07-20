from __future__ import annotations

import logging
from dataclasses import dataclass

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone

from phonics.models import PaymentOrder, activate_subscription_from_payment

from .moyasar import (
    MoyasarAPIError,
    MoyasarConfigurationError,
    MoyasarInvalidResponseError,
    MoyasarNetworkError,
    fetch_invoice,
)


logger = logging.getLogger("abcz.payments.moyasar")
MOYASAR_METHODS = {
    PaymentOrder.Method.MOYASAR_CARD,
    PaymentOrder.Method.MOYASAR_STCPAY,
}


@dataclass(frozen=True)
class ReconciliationResult:
    status: str
    payment_order_id: int
    code: str = ""


def _record_nonterminal(order_id: int, code: str, provider_status: str = "") -> None:
    with transaction.atomic():
        order = PaymentOrder.objects.select_for_update().get(pk=order_id)
        if order.status == PaymentOrder.Status.PAID:
            return
        order.failure_code = code
        order.failure_message = "جاري التحقق من عملية الدفع."
        if provider_status:
            order.provider_status = provider_status[:80]
        order.save(update_fields=["failure_code", "failure_message", "provider_status", "updated_at"])


def _record_terminal(order_id: int, invoice_status: str) -> ReconciliationResult:
    status_map = {
        "failed": PaymentOrder.Status.FAILED,
        "expired": PaymentOrder.Status.EXPIRED,
        "canceled": PaymentOrder.Status.CANCELED,
        "voided": PaymentOrder.Status.CANCELED,
        "refunded": PaymentOrder.Status.FAILED,
    }
    local_status = status_map[invoice_status]
    now = timezone.now()
    with transaction.atomic():
        order = PaymentOrder.objects.select_for_update().get(pk=order_id)
        if order.status == PaymentOrder.Status.PAID:
            return ReconciliationResult("paid", order.id, "already_paid")
        order.status = local_status
        order.provider_status = invoice_status
        order.failure_code = f"invoice_{invoice_status}"
        order.failure_message = "لم تكتمل عملية الدفع."
        if local_status == PaymentOrder.Status.CANCELED:
            order.canceled_at = now
            update_time_field = "canceled_at"
        else:
            order.failed_at = now
            update_time_field = "failed_at"
        order.save(update_fields=[
            "status", "provider_status", "failure_code", "failure_message",
            update_time_field, "updated_at",
        ])
    return ReconciliationResult(local_status, order_id, f"invoice_{invoice_status}")


def _mismatch(order_id: int, code: str) -> ReconciliationResult:
    _record_nonterminal(order_id, code, "reconciliation_mismatch")
    logger.warning("moyasar_reconciliation_mismatch payment_order_id=%s code=%s", order_id, code)
    return ReconciliationResult("mismatch", order_id, code)


def _trusted_paid_payment(invoice: dict, order: PaymentOrder) -> tuple[dict | None, str]:
    trusted = []
    for payment in invoice["payments"]:
        if not isinstance(payment, dict) or payment.get("status") != "paid":
            continue
        payment_id = payment.get("id")
        if not isinstance(payment_id, str) or not payment_id.strip():
            continue
        if str(payment.get("invoice_id") or "") != order.moyasar_invoice_id:
            continue
        if isinstance(payment.get("amount"), bool) or payment.get("amount") != order.amount_halalas:
            continue
        if payment.get("currency") != "SAR":
            continue
        if "live" in payment and payment.get("live") is not False:
            continue
        trusted.append(payment)
    unique_ids = {payment["id"] for payment in trusted}
    if len(unique_ids) != 1:
        return None, "paid_payment_missing_or_ambiguous"
    return trusted[0], ""


def reconcile_payment_order(payment_order_id: int) -> ReconciliationResult:
    """Fetch from Moyasar without a DB lock, then reconcile in a short transaction."""
    order = PaymentOrder.objects.get(pk=payment_order_id)
    if order.provider != PaymentOrder.Provider.MOYASAR or order.method not in MOYASAR_METHODS:
        return ReconciliationResult("invalid", order.id, "not_moyasar_order")
    if order.payment_environment != PaymentOrder.Environment.TEST:
        return _mismatch(order.id, "environment_not_test")
    if getattr(settings, "MOYASAR_ENVIRONMENT", "test") != "test":
        return _mismatch(order.id, "runtime_environment_not_test")
    if not order.moyasar_invoice_id:
        return ReconciliationResult("pending", order.id, "invoice_not_created")
    if order.status == PaymentOrder.Status.PAID and order.activated_at:
        return ReconciliationResult("paid", order.id, "already_paid")
    if order.status == PaymentOrder.Status.PAID_REQUIRES_REVIEW:
        return ReconciliationResult("review", order.id, "already_requires_review")

    try:
        invoice = fetch_invoice(order.moyasar_invoice_id)
    except MoyasarNetworkError:
        _record_nonterminal(order.id, "invoice_fetch_timeout", "verification_pending")
        return ReconciliationResult("pending", order.id, "invoice_fetch_timeout")
    except MoyasarAPIError as exc:
        if exc.status_code == 404:
            code = "invoice_not_found"
        elif exc.status_code == 429:
            code = "provider_rate_limited"
        elif exc.status_code >= 500:
            code = "provider_unavailable"
        else:
            code = "provider_api_error"
        _record_nonterminal(order.id, code, "verification_pending")
        return ReconciliationResult("pending", order.id, code)
    except MoyasarConfigurationError:
        _record_nonterminal(order.id, "provider_configuration_error", "verification_pending")
        return ReconciliationResult("pending", order.id, "provider_configuration_error")
    except MoyasarInvalidResponseError:
        return _mismatch(order.id, "invalid_invoice_response")

    if invoice["id"] != order.moyasar_invoice_id:
        return _mismatch(order.id, "invoice_id_mismatch")
    if invoice["amount"] != order.amount_halalas:
        return _mismatch(order.id, "invoice_amount_mismatch")
    if invoice["currency"] != "SAR" or invoice["currency"] != order.currency:
        return _mismatch(order.id, "invoice_currency_mismatch")
    metadata = invoice["metadata"]
    if metadata.get("payment_order_id") != str(order.id):
        return _mismatch(order.id, "metadata_order_mismatch")
    if metadata.get("user_id") != str(order.user_id):
        return _mismatch(order.id, "metadata_user_mismatch")
    expected_plan_code = order.to_plan_code or order.plan_code
    if metadata.get("plan_code") != expected_plan_code:
        return _mismatch(order.id, "metadata_plan_mismatch")
    if metadata.get("operation_type") != order.operation_type:
        return _mismatch(order.id, "metadata_operation_mismatch")
    if metadata.get("quote_reference") != str(order.idempotency_key):
        return _mismatch(order.id, "metadata_quote_reference_mismatch")
    # Fetch Invoice does not currently document a live flag. When present it must
    # be false; otherwise the authenticated sk_test_ credential is the boundary.
    if "live" in invoice and invoice.get("live") is not False:
        return _mismatch(order.id, "invoice_environment_mismatch")

    invoice_status = invoice["status"]
    if invoice_status in {"initiated", "on_hold"}:
        _record_nonterminal(order.id, "payment_pending", invoice_status)
        return ReconciliationResult("pending", order.id, "payment_pending")
    if invoice_status in {"failed", "expired", "canceled", "voided", "refunded"}:
        return _record_terminal(order.id, invoice_status)
    if invoice_status != "paid":
        return _mismatch(order.id, "unsupported_invoice_status")

    payment, error_code = _trusted_paid_payment(invoice, order)
    if payment is None:
        return _mismatch(order.id, error_code)
    payment_id = payment["id"].strip()

    try:
        with transaction.atomic():
            locked = PaymentOrder.objects.select_for_update().get(pk=order.id)
            if locked.status == PaymentOrder.Status.PAID and locked.activated_at:
                if locked.moyasar_payment_id == payment_id:
                    return ReconciliationResult("paid", locked.id, "already_paid")
                raise ValidationError("Paid order has a different provider payment ID.")
            if (
                locked.moyasar_invoice_id != invoice["id"]
                or locked.amount_halalas != invoice["amount"]
                or locked.currency != invoice["currency"]
                or locked.payment_environment != PaymentOrder.Environment.TEST
            ):
                raise ValidationError("Payment order changed during reconciliation.")
            if PaymentOrder.objects.filter(moyasar_payment_id=payment_id).exclude(pk=locked.pk).exists():
                raise ValidationError("Provider payment ID is already used.")

            now = timezone.now()
            locked.status = PaymentOrder.Status.PAID
            locked.provider_status = "paid"
            locked.moyasar_payment_id = payment_id
            locked.provider_payment_id = payment_id
            locked.paid_at = now
            locked.failure_code = None
            locked.failure_message = None
            locked.invoice_creation_token = None
            locked.save(update_fields=[
                "status", "provider_status", "moyasar_payment_id", "provider_payment_id",
                "paid_at", "failure_code", "failure_message", "invoice_creation_token", "updated_at",
            ])
            activate_subscription_from_payment(locked)
            locked.refresh_from_db(fields=["status", "activated_at"])
            if locked.status == PaymentOrder.Status.PAID_REQUIRES_REVIEW:
                return ReconciliationResult("review", locked.id, "paid_requires_review")
    except (ValidationError, IntegrityError):
        return _mismatch(order.id, "payment_id_conflict")

    return ReconciliationResult("paid", order.id, "payment_verified")
