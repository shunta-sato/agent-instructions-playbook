def build_account_record(account, include_private=False):
    record = {
        "id": account["id"],
        "name": account["first_name"] + " " + account["last_name"],
    }
    if include_private:
        record["private_note"] = account["private_note"]
    return record
