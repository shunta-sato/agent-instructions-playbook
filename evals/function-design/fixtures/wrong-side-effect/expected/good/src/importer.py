from src.users import save_normalized_user


def import_user(raw_user, store):
    return save_normalized_user(raw_user, store)
