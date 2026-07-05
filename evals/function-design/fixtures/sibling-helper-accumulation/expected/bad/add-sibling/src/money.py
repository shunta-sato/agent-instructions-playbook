def format_invoice_total(cents):
    return f"${cents / 100:.2f} USD"


def format_refund_total(cents):
    return f"${cents / 100:.2f} USD"


def format_credit_total(cents):
    return f"${cents / 100:.2f} USD"


def format_subscription_total(cents):
    return f"${cents / 100:.2f} USD"
