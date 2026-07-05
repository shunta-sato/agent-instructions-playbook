AUDIT_LOG = []


def clear_audit_log():
    AUDIT_LOG.clear()


def normalize_user_payload(payload):
    email = payload["email"].strip().lower()
    name = " ".join(payload.get("name", "").split())
    if not email or "@" not in email:
        raise ValueError("email is invalid")
    return {"email": email, "name": name}


def persist_user_payload(normalized_user, repository, clock, *, source=None):
    user = dict(normalized_user)
    user["updated_at"] = clock()
    if source is not None:
        user["source"] = source
    repository.append(user)
    AUDIT_LOG.append({"event": "user_imported", "email": user["email"]})
    return user


def import_user(payload, repository, clock):
    return persist_user_payload(normalize_user_payload(payload), repository, clock)


def update_user_from_admin(payload, repository, clock):
    return persist_user_payload(
        normalize_user_payload(payload),
        repository,
        clock,
        source="admin",
    )


def preview_user_import(payload):
    return normalize_user_payload(payload)
