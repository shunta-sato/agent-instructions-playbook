"""Order-billing fixture module.

Implements the three functions specified in spec.md: SKU label formatting,
volume-discount-rate lookup, and refund processing through an injected
payment gateway. See spec.md for the full behavioral contract.
"""


class GatewayError(Exception):
    """Raised by a payment gateway when it fails to process a transfer."""


def sku_label(sku_code: str, name: str) -> str:
    """Return the display label for an order line's SKU.

    Pure formatting; callers guarantee non-empty strings, so there is no
    validation contract here.
    """
    return f"{sku_code}: {name}"


def volume_discount_rate(quantity: int) -> int:
    """Return the discount rate in percent for an order line quantity.

    Valid domain is 1 <= quantity <= 100; outside it raises ValueError.
    """
    if not 1 <= quantity <= 100:
        raise ValueError(f"quantity out of range (1-100): {quantity}")
    if quantity <= 10:
        return 0
    if quantity <= 50:
        return 5
    return 10


def apply_refund(balance_cents: int, refund_cents: int, gateway) -> int:
    """Refund money via gateway and return the new balance.

    Valid domain is 1 <= refund_cents <= balance_cents; outside it raises
    ValueError without contacting the gateway. On a valid refund,
    gateway.transfer(refund_cents) is called exactly once (a duplicate
    transfer would double-refund real money) before the new balance is
    computed and returned. If gateway.transfer raises GatewayError, that
    exception propagates and nothing is committed: the validation happens
    before the transfer, and the return value is only computed after the
    transfer succeeds, so a failed transfer leaves no observable balance
    change.
    """
    if not 1 <= refund_cents <= balance_cents:
        raise ValueError(
            f"refund_cents out of range (1-{balance_cents}): {refund_cents}"
        )
    gateway.transfer(refund_cents)
    new_balance = balance_cents - refund_cents
    gateway.log(f"refunded {refund_cents} cents; new balance {new_balance} cents")
    return new_balance
