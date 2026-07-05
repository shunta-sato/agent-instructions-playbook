def normalize_and_save_user(raw_user, store):
    normalized = {
        "id": raw_user["id"].strip(),
        "email": raw_user["email"].strip().lower(),
        "name": " ".join(raw_user["name"].split()),
    }
    store[normalized["id"]] = normalized
    return normalized
