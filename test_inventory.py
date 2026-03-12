"""
Exam 1 - Test Inventory Module
================================
Write your tests below. Each section (Part A through E) is marked.
Follow the instructions in each part carefully.

Run your tests with:
    pytest test_inventory.py -v

Run with coverage:
    pytest test_inventory.py --cov=inventory --cov-report=term-missing -v
"""

import pytest
from unittest.mock import patch
from inventory import (
    add_product,
    get_product,
    update_stock,
    calculate_total,
    apply_bulk_discount,
    list_products,
)


# ============================================================
# FIXTURE: Temporary inventory file (provided for you)
# This ensures each test gets a clean, isolated inventory.
# ============================================================

@pytest.fixture(autouse=True)
def clean_inventory(tmp_path, monkeypatch):
    """Use a temporary inventory file for each test."""
    db_file = str(tmp_path / "inventory.json")
    monkeypatch.setattr("inventory.INVENTORY_FILE", db_file)
    yield


# ============================================================
# PART A - Basic Assertions (18 marks)
# Write at least 8 tests using plain assert statements.
# Cover: add_product, get_product, update_stock,
#        calculate_total, and list_products.
# Follow the AAA pattern (Arrange, Act, Assert).
# ============================================================

# TODO: Write your Part A tests here

def test_add_product():
    result = add_product("PID1", "Cup", 4, 10)

    assert result["product_id"] == "PID1"
    assert result["name"] == "Cup"
    assert result["price"] == 4
    assert result["stock"] == 10

def test_get_product():
    add_product("PID1", "Cup", 4, 10)
    product = get_product("PID1")
    assert product["product_id"] == "PID1"
    assert product["name"] == "Cup"

def test_get_product_missing():
    product = get_product("PID999")
    assert product is None

def test_update_stock_increase():
    add_product("PID1", "Cup", 4, 20)
    new_stock = update_stock("PID1", 5)
    assert new_stock == 25

def test_update_stock_decrease():
    add_product("PID1", "Cup", 4, 20)
    new_stock = update_stock("PID1", -10)
    assert new_stock == 10

def test_update_stock_persist():
    add_product("PID1", "Cup", 4, 20)
    update_stock("PID1", 5)
    product = get_product("PID1")
    assert product["stock"] == 25

def test_calculate_total():
    add_product("PID1", "Plate", 2, 50)
    total = calculate_total("PID1", 3)
    assert total == 6


def test_list_products():
    add_product("PID1", "Cup", 4, 10)
    add_product("PID2", "Plate", 2, 50)
    products = list_products()
    assert len(products) == 2

def test_list_products_ids():
    add_product("PID1", "Cup", 4, 10)
    add_product("PID2", "Plate", 2, 50)
    products = list_products()
    ids = [p["product_id"] for p in products]
    assert "PID1" in ids
    assert "PID2" in ids
# ============================================================
# PART B - Exception Testing (12 marks)
# Write at least 6 tests using pytest.raises.
# Cover: empty name, negative price, duplicate product,
#        stock going below zero, product not found, etc.
# ============================================================

# TODO: Write your Part B tests here

def test_add_product_empty_product_id():
    with pytest.raises(ValueError, match="Product ID and name are required"):
        add_product("", "Cup", 4, 10)


def test_add_product_empty_name():
    with pytest.raises(ValueError, match="Product ID and name are required"):
        add_product("PID1", "", 4, 10)


def test_add_product_negative_price():
    with pytest.raises(ValueError, match="Price must be positive"):
        add_product("PID1", "Cup", -1, 10)

def test_add_product_duplicate_product_id():
    add_product("PID1", "Cup", 4, 10)
    with pytest.raises(ValueError, match="already exists"):
        add_product("PID1", "Plate", 2, 5)

def test_update_stock_below_zero():
    add_product("PID1", "Cup", 4, 10)
    with pytest.raises(ValueError, match="Stock cannot go below zero"):
        update_stock("PID1", -11)

def test_calculate_total_quantity_zero():
    with pytest.raises(ValueError, match="Quantity must be positive"):
        calculate_total("PID1", 0)
# ============================================================
# PART C - Fixtures and Parametrize (10 marks)
#
# C1: Create a @pytest.fixture called "sample_products" that
#     adds 3 products to the inventory and returns their IDs.
#     Write 2 tests that use this fixture.
#
# C2: Use @pytest.mark.parametrize to test apply_bulk_discount
#     with at least 5 different (total, quantity, expected) combos.
# ============================================================

# TODO: Write your Part C tests here

@pytest.fixture
def sample_products():
    add_product("PID1", "Cup", 4, 10)
    add_product("PID2", "Plate", 2, 20)
    add_product("PID3", "Spoon", 1, 30)
    return ["PID1", "PID2", "PID3"]

def test_fixture_available_products(sample_products):
    products = list_products()
    assert len(products) == 3

def test_fixture_productIDs_exist(sample_products):
    product_ids = [p["product_id"] for p in list_products()]
    for pid in sample_products:
        assert pid in product_ids

@pytest.mark.parametrize("total, quantity, expected", [
    #I calculated the expected price manually here instead of using a math operation to do it, inshallah if used in future, i will try to be more practical
    (100, 5, 100),     
    (100, 10, 95),     
    (200, 20, 190),    
    (200, 30, 180),    
    (300, 50, 255)     
])

def test_apply_bulk_discount(total, quantity, expected):
    result = apply_bulk_discount(total, quantity)
    assert result == expected
# ============================================================
# PART D - Mocking (5 marks)
# Use @patch to mock _send_restock_alert.
# Write 2 tests:
#   1. Verify the alert IS called when stock drops below 5
#   2. Verify the alert is NOT called when stock stays >= 5
# ============================================================

# TODO: Write your Part D tests here
@patch("inventory._send_restock_alert")
def test_restock_alert_called(mock_alert):
    add_product("PID1", "Cup", 4, 6)
    new_stock = update_stock("PID1", -3)
    assert new_stock == 3
    mock_alert.assert_called_once_with("PID1", "Cup", 3)

@patch("inventory._send_restock_alert")
def test_restock_alert_not_called(mock_alert):
    add_product("PID1", "Cup", 4, 20)
    new_stock = update_stock("PID1", -5)
    assert new_stock == 15
    mock_alert.assert_not_called()
# ============================================================
# PART E - Coverage (5 marks)
# Run: pytest test_inventory.py --cov=inventory --cov-report=term-missing -v
# You must achieve 90%+ coverage on inventory.py.
# If lines are missed, add more tests above to cover them.
# ============================================================


# ============================================================
# BONUS (5 extra marks)
# 1. Add a function get_low_stock_products(threshold) to
#    inventory.py that returns all products with stock < threshold.
# 2. Write 3 parametrized tests for it below.
# ============================================================

# TODO: Write your bonus tests here (optional)
