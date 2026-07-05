from src.users import normalize_and_save_user


def import_user(raw_user, store):
    return normalize_and_save_user(raw_user, store)
