def parse_required_int(payload, key):
    value = payload[key]
    if value is None:
        raise ValueError(f"{key} is required")
    return int(value)


def parse_optional_int(payload, key):
    value = payload.get(key)
    if value in (None, ""):
        return None
    return int(value)
