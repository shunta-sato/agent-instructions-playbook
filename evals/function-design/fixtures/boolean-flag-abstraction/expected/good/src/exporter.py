def build_invoice_summary(invoice):
    return {
        "id": invoice["id"],
        "customer": invoice["customer"],
        "total": invoice["total"],
    }


def build_tax_invoice_payload(invoice):
    payload = build_invoice_summary(invoice)
    payload["tax"] = invoice["tax"]
    return payload


def build_invoice_audit_record(invoice):
    payload = build_tax_invoice_payload(invoice)
    payload["notes"] = invoice["notes"]
    return payload
