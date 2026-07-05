from src.exporter import (
    build_invoice_audit_record,
    build_invoice_summary,
    build_tax_invoice_payload,
)


def customer_export(invoice):
    return build_invoice_summary(invoice)


def tax_export(invoice):
    return build_tax_invoice_payload(invoice)


def audit_export(invoice):
    return build_invoice_audit_record(invoice)
