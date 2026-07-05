from src.users import normalize_and_save_user


def preview_user(raw_user):
    return normalize_and_save_user(raw_user, persist=False)
