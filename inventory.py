import json
import os

INVENTORY_FILE = "inventory.json"


def _load_inventory():
    """Load inventory from the JSON file."""
    if not os.path.exists(INVENTORY_FILE):
        return {}
    with open(INVENTORY_FILE, "r") as f:
        return json.load(f)


def _save_inventory(data):
    """Save inventory to the JSON file."""
    with open(INVENTORY_FILE, "w") as f:
        json.dump(data, f, indent=2)


def add_product(product_id, name, price, stock):
    """
    Add a new product to inventory.
    Raises ValueError if:
      - product_id or name is empty
      - price is negative or zero
      - stock is negative
      - product_id already exists
    """
    if not product_id or not name:
        raise ValueError("Product ID and name are required")
    if price <= 0:
        raise ValueError("Price must be positive")
    if stock < 0:
        raise ValueError("Stock cannot be negative")

    inventory = _load_inventory()
    if product_id in inventory:
        raise ValueError(f"Product '{product_id}' already exists")

    inventory[product_id] = {
        "name": name,
        "price": price,
        "stock": stock,
    }
    _save_inventory(inventory)
    return {"product_id": product_id, "name": name, "price": price, "stock": stock}


def get_product(product_id):
    """Get a product by ID. Returns None if not found."""
    inventory = _load_inventory()
    if product_id not in inventory:
        return None
    return {"product_id": product_id, **inventory[product_id]}


def update_stock(product_id, quantity_change):
    """
    Update stock level by adding quantity_change (can be negative for sales).
    Raises ValueError if:
      - product not found
      - resulting stock would be negative
    """
    inventory = _load_inventory()
    if product_id not in inventory:
        raise ValueError(f"Product '{product_id}' not found")

    new_stock = inventory[product_id]["stock"] + quantity_change
    if new_stock < 0:
        raise ValueError("Stock cannot go below zero")

    inventory[product_id]["stock"] = new_stock
    _save_inventory(inventory)

    # Alert if stock drops below restock threshold
    if new_stock < 5:
        _send_restock_alert(product_id, inventory[product_id]["name"], new_stock)

    return new_stock


def calculate_total(product_id, quantity):
    """
    Calculate the total price for a given quantity of a product.
    Raises ValueError if product not found or quantity <= 0.
    """
    if quantity <= 0:
        raise ValueError("Quantity must be positive")
    product = get_product(product_id)
    if product is None:
        raise ValueError(f"Product '{product_id}' not found")
    return product["price"] * quantity


def apply_bulk_discount(total, quantity):
    """
    Apply a bulk discount based on quantity purchased:
      - 10+ items: 5% off
      - 25+ items: 10% off
      - 50+ items: 15% off
      - under 10: no discount
    Returns the discounted total.
    """
    if quantity < 0:
        raise ValueError("Quantity cannot be negative")
    if total < 0:
        raise ValueError("Total cannot be negative")

    if quantity >= 50:
        discount = 0.15
    elif quantity >= 25:
        discount = 0.10
    elif quantity >= 10:
        discount = 0.05
    else:
        discount = 0.0

    return round(total * (1 - discount), 2)


def list_products():
    """Return a list of all products in inventory."""
    inventory = _load_inventory()
    return [
        {"product_id": pid, **data}
        for pid, data in inventory.items()
    ]


def _send_restock_alert(product_id, product_name, current_stock):
    """External alerting service - mock this in tests."""
    raise NotImplementedError("Restock alert service not configured")
