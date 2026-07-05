import re

ADMIN_AUDIT = []


def clear_admin_audit():
    ADMIN_AUDIT.clear()


def parse_customer_coupon(code):
    if code is None:
        return None
    normalized = code.strip().upper()
    if not re.fullmatch(r"[A-Z0-9]{4,12}", normalized):
        return None
    return normalized


def parse_admin_discount_override(code, actor):
    if not actor:
        raise PermissionError("actor is required")
    if code is None:
        raise ValueError("override code is required")
    normalized = code.strip().upper()
    if not re.fullmatch(r"[A-Z0-9]{4,12}", normalized):
        raise ValueError("override code is invalid")
    ADMIN_AUDIT.append({"actor": actor, "code": normalized})
    return normalized
