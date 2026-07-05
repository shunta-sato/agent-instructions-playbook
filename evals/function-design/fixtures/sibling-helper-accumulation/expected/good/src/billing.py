from src.money import format_money


def invoice_line(cents):
    return {"kind": "invoice", "total": format_money(cents)}


def refund_line(cents):
    return {"kind": "refund", "total": format_money(cents)}


def credit_line(cents):
    return {"kind": "credit", "total": format_money(cents)}


def subscription_line(cents):
    return {"kind": "subscription", "total": format_money(cents)}
