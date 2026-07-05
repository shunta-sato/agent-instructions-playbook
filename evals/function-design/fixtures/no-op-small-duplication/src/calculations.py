def order_total(order):
    return sum(item["price"] * item["quantity"] for item in order["items"])
