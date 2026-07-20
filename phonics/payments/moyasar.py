from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from urllib.parse import urlparse

import requests
from django.conf import settings


logger = logging.getLogger("abcz.payments.moyasar")
ONE_HALALA = Decimal("0.01")


class MoyasarError(Exception):
    """Base class for safe, user-independent Moyasar integration errors."""


class MoyasarConfigurationError(MoyasarError):
    pass


class MoyasarNetworkError(MoyasarError):
    pass


class MoyasarAPIError(MoyasarError):
    def __init__(self, *, status_code: int, request_id: str = ""):
        self.status_code = status_code
        self.request_id = request_id
        super().__init__("Moyasar rejected or could not process the invoice request.")


class MoyasarInvalidResponseError(MoyasarError):
    pass


class MoyasarUnsafeCheckoutURLError(MoyasarInvalidResponseError):
    pass


@dataclass(frozen=True)
class MoyasarInvoice:
    invoice_id: str
    checkout_url: str
    amount_halalas: int
    currency: str
    status: str
    request_id: str = ""


def validate_amounts(amount_sar: Decimal, amount_halalas: int) -> int:
    """Return the canonical halala amount after an exact Decimal comparison."""
    if isinstance(amount_sar, float) or isinstance(amount_halalas, bool):
        raise ValueError("Payment amounts must use Decimal and integer values.")
    try:
        sar = Decimal(amount_sar)
        halalas = int(amount_halalas)
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise ValueError("Invalid payment amount.") from exc

    rounded = sar.quantize(ONE_HALALA, rounding=ROUND_HALF_UP)
    if sar != rounded or halalas <= 0 or int(rounded * 100) != halalas:
        raise ValueError("The SAR amount and halala amount do not match.")
    return halalas


def _configuration() -> tuple[str, str, tuple[int, int]]:
    secret_key = str(getattr(settings, "MOYASAR_SECRET_KEY", "") or "").strip()
    environment = str(getattr(settings, "MOYASAR_ENVIRONMENT", "test") or "test").strip().lower()
    if environment not in {"test", "live"}:
        raise MoyasarConfigurationError("Moyasar payment environment is invalid.")
    if environment != "test":
        raise MoyasarConfigurationError("Moyasar live mode is disabled during Sandbox integration.")
    if not secret_key:
        raise MoyasarConfigurationError("Moyasar payment is not configured.")
    expected_prefix = "sk_test_"
    if not secret_key.startswith(expected_prefix):
        raise MoyasarConfigurationError("Moyasar key does not match the configured environment.")

    api_url = str(getattr(settings, "MOYASAR_API_URL", "https://api.moyasar.com/v1")).rstrip("/")
    parsed_api_url = urlparse(api_url)
    if parsed_api_url.scheme != "https" or not parsed_api_url.hostname:
        raise MoyasarConfigurationError("Moyasar API URL must be HTTPS.")
    timeouts = (
        int(getattr(settings, "MOYASAR_CONNECT_TIMEOUT", 5)),
        int(getattr(settings, "MOYASAR_READ_TIMEOUT", 15)),
    )
    if min(timeouts) <= 0:
        raise MoyasarConfigurationError("Moyasar timeouts must be positive.")
    return secret_key, api_url, timeouts


def validate_checkout_url(checkout_url: str) -> str:
    value = str(checkout_url or "").strip()
    parsed = urlparse(value)
    hostname = (parsed.hostname or "").lower().rstrip(".")
    try:
        port = parsed.port
    except ValueError:
        port = -1
    allowed_hosts = {
        str(host).strip().lower().rstrip(".")
        for host in getattr(settings, "MOYASAR_CHECKOUT_ALLOWED_HOSTS", [])
        if str(host).strip()
    }
    if (
        parsed.scheme != "https"
        or not hostname
        or parsed.username
        or parsed.password
        or port not in {None, 443}
        or hostname not in allowed_hosts
    ):
        logger.warning("moyasar_checkout_host_rejected hostname=%s", hostname or "missing")
        raise MoyasarUnsafeCheckoutURLError("Moyasar returned an unsafe checkout URL.")
    return value


def _response_request_id(response) -> str:
    return str(
        response.headers.get("X-Request-ID")
        or response.headers.get("Request-ID")
        or response.headers.get("Request-Id")
        or ""
    )[:128]


def create_invoice(
    *,
    payment_order_id: int,
    user_id: int,
    plan_code: str,
    operation_type: str,
    quote_reference: str,
    amount_sar: Decimal,
    amount_halalas: int,
    currency: str,
    description: str,
    success_url: str,
    back_url: str,
    callback_url: str,
) -> MoyasarInvoice:
    canonical_halalas = validate_amounts(amount_sar, amount_halalas)
    if currency != "SAR":
        raise ValueError("Moyasar invoices must use SAR.")
    secret_key, api_url, timeouts = _configuration()
    payload = {
        "amount": canonical_halalas,
        "currency": "SAR",
        "description": str(description)[:255],
        "success_url": success_url,
        "back_url": back_url,
        "metadata": {
            "payment_order_id": str(payment_order_id),
            "user_id": str(user_id),
            "plan_code": str(plan_code),
            "operation_type": str(operation_type),
            "quote_reference": str(quote_reference),
        },
    }
    if callback_url:
        payload["callback_url"] = callback_url

    try:
        response = requests.post(
            f"{api_url}/invoices",
            auth=(secret_key, ""),
            json=payload,
            timeout=timeouts,
            allow_redirects=False,
        )
    except requests.RequestException as exc:
        logger.warning(
            "moyasar_invoice_network_error payment_order_id=%s error_type=%s",
            payment_order_id,
            type(exc).__name__,
        )
        raise MoyasarNetworkError("Could not connect to Moyasar.") from exc

    request_id = _response_request_id(response)
    logger.info(
        "moyasar_invoice_response payment_order_id=%s status_code=%s provider_request_id=%s",
        payment_order_id,
        response.status_code,
        request_id or "missing",
    )
    if response.status_code != 201:
        raise MoyasarAPIError(status_code=response.status_code, request_id=request_id)

    try:
        data = response.json()
    except (ValueError, TypeError) as exc:
        raise MoyasarInvalidResponseError("Moyasar returned an invalid response.") from exc
    if not isinstance(data, dict):
        raise MoyasarInvalidResponseError("Moyasar returned an invalid response.")

    raw_invoice_id = data.get("id")
    invoice_id = raw_invoice_id.strip() if isinstance(raw_invoice_id, str) else ""
    checkout_url = str(data.get("url") or "").strip()
    if not invoice_id:
        raise MoyasarInvalidResponseError("Moyasar response did not include an invoice ID.")
    if not checkout_url:
        raise MoyasarInvalidResponseError("Moyasar response did not include a checkout URL.")
    checkout_url = validate_checkout_url(checkout_url)

    response_amount = data.get("amount")
    if isinstance(response_amount, bool):
        raise MoyasarInvalidResponseError("Moyasar returned an invalid amount.")
    try:
        response_amount = int(response_amount)
    except (TypeError, ValueError) as exc:
        raise MoyasarInvalidResponseError("Moyasar returned an invalid amount.") from exc
    response_currency = str(data.get("currency") or "").upper()
    if response_amount != canonical_halalas:
        raise MoyasarInvalidResponseError("Moyasar invoice amount did not match the order.")
    if response_currency != currency:
        raise MoyasarInvalidResponseError("Moyasar invoice currency did not match the order.")
    raw_status = data.get("status")
    allowed_statuses = {
        "initiated", "paid", "failed", "refunded", "canceled", "on_hold", "expired", "voided"
    }
    if raw_status is not None and (not isinstance(raw_status, str) or raw_status not in allowed_statuses):
        raise MoyasarInvalidResponseError("Moyasar returned an invalid invoice status.")

    return MoyasarInvoice(
        invoice_id=invoice_id,
        checkout_url=checkout_url,
        amount_halalas=response_amount,
        currency=response_currency,
        status=raw_status or "initiated",
        request_id=request_id,
    )


def fetch_invoice(invoice_id: str) -> dict:
    """Fetch a trusted invoice snapshot without logging its response body."""
    invoice_id = str(invoice_id or "").strip()
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,120}", invoice_id):
        raise MoyasarInvalidResponseError("The stored Moyasar invoice ID is invalid.")
    secret_key, api_url, timeouts = _configuration()
    try:
        response = requests.get(
            f"{api_url}/invoices/{invoice_id}",
            auth=(secret_key, ""),
            timeout=timeouts,
            allow_redirects=False,
        )
    except requests.RequestException as exc:
        logger.warning(
            "moyasar_invoice_fetch_network_error invoice_reference_present=true error_type=%s",
            type(exc).__name__,
        )
        raise MoyasarNetworkError("Could not connect to Moyasar.") from exc

    request_id = _response_request_id(response)
    logger.info(
        "moyasar_invoice_fetch_response status_code=%s provider_request_id=%s",
        response.status_code,
        request_id or "missing",
    )
    if response.status_code != 200:
        raise MoyasarAPIError(status_code=response.status_code, request_id=request_id)
    try:
        data = response.json()
    except (ValueError, TypeError) as exc:
        raise MoyasarInvalidResponseError("Moyasar returned an invalid invoice response.") from exc
    if not isinstance(data, dict):
        raise MoyasarInvalidResponseError("Moyasar returned an invalid invoice response.")

    required_types = {
        "id": str,
        "status": str,
        "amount": int,
        "currency": str,
        "metadata": dict,
        "payments": list,
    }
    for field, field_type in required_types.items():
        value = data.get(field)
        if field == "amount" and isinstance(value, bool):
            raise MoyasarInvalidResponseError("Moyasar returned an invalid invoice amount.")
        if not isinstance(value, field_type):
            raise MoyasarInvalidResponseError(f"Moyasar invoice response is missing {field}.")
    return data
