def normalize_and_save_user(raw_user, store=None, persist=True):
    normalized = {
        "id": raw_user["id"].strip(),
        "email": raw_user["email"].strip().lower(),
        "name": " ".join(raw_user["name"].split()),
    }
    if persist and store is not None:
        store[normalized["id"]] = normalized
    return normalized
