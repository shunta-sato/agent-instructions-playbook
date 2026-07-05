def build_invoice_payload(invoice, include_tax=False, include_notes=False, mode="summary"):
    payload = {
        "id": invoice["id"],
        "customer": invoice["customer"],
        "total": invoice["total"],
    }
    if include_tax or mode == "tax":
        payload["tax"] = invoice["tax"]
    if include_notes or mode == "audit":
        payload["notes"] = invoice["notes"]
    return payload
