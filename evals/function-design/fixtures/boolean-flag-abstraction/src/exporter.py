def build_invoice_payload(invoice, include_tax=False):
    payload = {
        "id": invoice["id"],
        "customer": invoice["customer"],
        "total": invoice["total"],
    }
    if include_tax:
        payload["tax"] = invoice["tax"]
    return payload
