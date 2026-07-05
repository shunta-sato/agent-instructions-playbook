def _parse_int(payload, key, required=True):
    if required:
        value = payload[key]
        if value is None:
            raise ValueError(f"{key} is required")
        return int(value)

    value = payload.get(key)
    if value in (None, ""):
        return None
    return int(value)


def parse_required_int(payload, key):
    return _parse_int(payload, key, required=True)


def parse_optional_int(payload, key):
    return _parse_int(payload, key, required=False)
