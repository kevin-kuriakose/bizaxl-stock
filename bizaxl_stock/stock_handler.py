import frappe
from frappe.utils import flt


def make_sle(item_code, warehouse, actual_qty, incoming_rate,
             posting_date, voucher_type, voucher_no,
             batch_no=None, serial_no=None):
    """Create a Stock Ledger Entry and update bin quantity."""

    # Get current qty
    current_qty = get_stock_balance(item_code, warehouse)
    qty_after = current_qty + actual_qty

    # Get current valuation rate
    current_rate = get_valuation_rate(item_code, warehouse)
    if actual_qty > 0 and incoming_rate:
        # Weighted average valuation
        current_value = current_qty * current_rate
        new_value = actual_qty * incoming_rate
        if (current_qty + actual_qty) > 0:
            valuation_rate = (current_value + new_value) / (current_qty + actual_qty)
        else:
            valuation_rate = incoming_rate
    else:
        valuation_rate = current_rate

    stock_value = qty_after * valuation_rate

    sle = frappe.get_doc({
        "doctype": "BA Stock Ledger Entry",
        "item_code": item_code,
        "warehouse": warehouse,
        "posting_date": posting_date,
        "actual_qty": actual_qty,
        "qty_after_transaction": qty_after,
        "incoming_rate": incoming_rate,
        "valuation_rate": valuation_rate,
        "stock_value": stock_value,
        "voucher_type": voucher_type,
        "voucher_no": voucher_no,
        "batch_no": batch_no,
        "serial_no": serial_no,
        "is_cancelled": 0,
    })
    sle.flags.ignore_permissions = True
    sle.insert()
    return sle


def get_stock_balance(item_code, warehouse):
    """Get current stock qty for item in warehouse."""
    result = frappe.db.sql("""
        SELECT COALESCE(SUM(actual_qty), 0)
        FROM `tabBA Stock Ledger Entry`
        WHERE item_code = %s
        AND warehouse = %s
        AND is_cancelled = 0
    """, (item_code, warehouse))
    return flt(result[0][0]) if result else 0.0


def get_valuation_rate(item_code, warehouse):
    """Get current valuation rate for item in warehouse."""
    result = frappe.db.sql("""
        SELECT valuation_rate
        FROM `tabBA Stock Ledger Entry`
        WHERE item_code = %s
        AND warehouse = %s
        AND is_cancelled = 0
        ORDER BY posting_date DESC, creation DESC
        LIMIT 1
    """, (item_code, warehouse))
    return flt(result[0][0]) if result else 0.0


def get_stock_summary(warehouse=None, item_code=None):
    """Get stock summary — current qty and value per item/warehouse."""
    conditions = "WHERE is_cancelled = 0"
    values = []
    if warehouse:
        conditions += " AND warehouse = %s"
        values.append(warehouse)
    if item_code:
        conditions += " AND item_code = %s"
        values.append(item_code)

    return frappe.db.sql(f"""
        SELECT
            item_code,
            warehouse,
            SUM(actual_qty) as qty,
            MAX(valuation_rate) as valuation_rate,
            SUM(actual_qty) * MAX(valuation_rate) as stock_value
        FROM `tabBA Stock Ledger Entry`
        {conditions}
        GROUP BY item_code, warehouse
        HAVING SUM(actual_qty) != 0
        ORDER BY item_code
    """, values, as_dict=True)


# Hooks from BA Sales Invoice — deduct stock on submit
def on_sales_invoice_submit(doc, method):
    """Deduct stock when sales invoice is submitted."""
    for item in doc.items:
        if not frappe.db.exists("BA Item", item.item_code):
            continue
        ba_item = frappe.get_value("BA Item", item.item_code, "is_stock_item")
        if not ba_item:
            continue
        # Get default warehouse from company or item
        warehouse = frappe.db.get_value(
            "BA Warehouse",
            {"company": doc.company, "warehouse_type": "Store"},
            "name"
        )
        if warehouse:
            make_sle(
                item_code=item.item_code,
                warehouse=warehouse,
                actual_qty=-flt(item.qty),
                incoming_rate=0,
                posting_date=doc.posting_date,
                voucher_type="BA Sales Invoice",
                voucher_no=doc.name,
            )


def on_sales_invoice_cancel(doc, method):
    frappe.db.set_value("BA Stock Ledger Entry",
        {"voucher_type": "BA Sales Invoice", "voucher_no": doc.name},
        "is_cancelled", 1)


def on_purchase_invoice_submit(doc, method):
    """Add stock when purchase invoice is submitted."""
    for item in doc.items:
        if not frappe.db.exists("BA Item", item.item_code):
            continue
        ba_item = frappe.get_value("BA Item", item.item_code, "is_stock_item")
        if not ba_item:
            continue
        warehouse = frappe.db.get_value(
            "BA Warehouse",
            {"company": doc.company, "warehouse_type": "Store"},
            "name"
        )
        if warehouse:
            make_sle(
                item_code=item.item_code,
                warehouse=warehouse,
                actual_qty=flt(item.qty),
                incoming_rate=flt(item.rate),
                posting_date=doc.posting_date,
                voucher_type="BA Purchase Invoice",
                voucher_no=doc.name,
            )


def on_purchase_invoice_cancel(doc, method):
    frappe.db.set_value("BA Stock Ledger Entry",
        {"voucher_type": "BA Purchase Invoice", "voucher_no": doc.name},
        "is_cancelled", 1)
