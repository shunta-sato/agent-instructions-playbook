def normalize_user(raw_user):
    return {
        "id": raw_user["id"].strip(),
        "email": raw_user["email"].strip().lower(),
        "name": " ".join(raw_user["name"].split()),
    }


def save_normalized_user(raw_user, store):
    normalized = normalize_user(raw_user)
    store[normalized["id"]] = normalized
    return normalized
