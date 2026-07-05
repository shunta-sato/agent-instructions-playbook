import re

ADMIN_AUDIT = []


def clear_admin_audit():
    ADMIN_AUDIT.clear()


def parse_discount_code(code, *, strict=False, actor=None):
    if code is None:
        if strict:
            raise ValueError("override code is required")
        return None
    normalized = code.strip().upper()
    if not re.fullmatch(r"[A-Z0-9]{4,12}", normalized):
        if strict:
            raise ValueError("override code is invalid")
        return None
    if strict:
        ADMIN_AUDIT.append({"actor": actor, "code": normalized})
    return normalized


def parse_customer_coupon(code):
    return parse_discount_code(code, strict=False)


def parse_admin_discount_override(code, actor):
    if not actor:
        raise PermissionError("actor is required")
    return parse_discount_code(code, strict=True, actor=actor)
