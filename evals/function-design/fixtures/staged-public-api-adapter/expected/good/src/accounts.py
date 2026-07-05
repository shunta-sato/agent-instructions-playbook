def build_customer_profile(account):
    return {
        "id": account["id"],
        "display_name": account["first_name"] + " " + account["last_name"],
    }


def build_account_record(account, include_private=False):
    record = build_customer_profile(account)
    record["name"] = record.pop("display_name")
    if include_private:
        record["private_note"] = account["private_note"]
    return record
