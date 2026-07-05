from src.money import (
    format_credit_total,
    format_invoice_total,
    format_refund_total,
    format_subscription_total,
)


def invoice_line(cents):
    return {"kind": "invoice", "total": format_invoice_total(cents)}


def refund_line(cents):
    return {"kind": "refund", "total": format_refund_total(cents)}


def credit_line(cents):
    return {"kind": "credit", "total": format_credit_total(cents)}


def subscription_line(cents):
    return {"kind": "subscription", "total": format_subscription_total(cents)}
