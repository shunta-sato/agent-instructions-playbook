AUDIT_LOG = []


def clear_audit_log():
    AUDIT_LOG.clear()


def parse_user_payload(payload, repository=None, clock=None, *, persist=True, source=None):
    email = payload["email"].strip().lower()
    name = " ".join(payload.get("name", "").split())
    if not email or "@" not in email:
        raise ValueError("email is invalid")

    user = {"email": email, "name": name}
    if persist:
        user["updated_at"] = clock()
        if source is not None:
            user["source"] = source
        repository.append(user)
        AUDIT_LOG.append({"event": "user_imported", "email": email})
    return user


def import_user(payload, repository, clock):
    return parse_user_payload(payload, repository, clock)


def update_user_from_admin(payload, repository, clock):
    return parse_user_payload(payload, repository, clock, source="admin")


def preview_user_import(payload):
    return parse_user_payload(payload, persist=False)
