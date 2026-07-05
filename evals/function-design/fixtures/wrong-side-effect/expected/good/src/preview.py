from src.users import normalize_user


def preview_user(raw_user):
    normalized = normalize_user(raw_user)
    return {
        "id": normalized["id"],
        "email": normalized["email"],
        "name": normalized["name"],
    }
