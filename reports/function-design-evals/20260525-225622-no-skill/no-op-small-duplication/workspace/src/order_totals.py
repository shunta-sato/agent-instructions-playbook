def subtotal_cents(lines):
    return sum(line["unit_cents"] * line["quantity"] for line in lines)


def shipping_cents(subtotal, country):
    if country == "US" and subtotal >= 5000:
        return 0
    return 900


def total_cents(lines, country):
    subtotal = subtotal_cents(lines)
    return subtotal + shipping_cents(subtotal, country)
