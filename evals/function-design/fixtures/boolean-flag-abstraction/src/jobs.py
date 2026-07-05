from src.exporter import build_invoice_payload


def customer_export(invoice):
    return build_invoice_payload(invoice)


def tax_export(invoice):
    return build_invoice_payload(invoice, include_tax=True)
