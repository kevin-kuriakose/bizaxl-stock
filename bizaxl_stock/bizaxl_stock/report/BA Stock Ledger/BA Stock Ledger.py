import frappe
def execute(filters=None):
    filters = filters or {}
    columns = [
        {"fieldname": "posting_date", "label": "Date", "fieldtype": "Date", "width": 100},
        {"fieldname": "item", "label": "Item", "fieldtype": "Link", "options": "BA Item", "width": 160},
        {"fieldname": "warehouse", "label": "Warehouse", "fieldtype": "Link", "options": "BA Warehouse", "width": 140},
        {"fieldname": "actual_qty", "label": "Qty Change", "fieldtype": "Float", "width": 110},
        {"fieldname": "qty_after_transaction", "label": "Balance Qty", "fieldtype": "Float", "width": 110},
        {"fieldname": "valuation_rate", "label": "Val. Rate", "fieldtype": "Currency", "width": 120},
        {"fieldname": "voucher_type", "label": "Voucher Type", "fieldtype": "Data", "width": 140},
        {"fieldname": "voucher_no", "label": "Voucher No", "fieldtype": "Data", "width": 160},
    ]
    conditions = "WHERE is_cancelled = 0"
    values = {}
    if filters.get("item"):
        conditions += " AND item = %(item)s"
        values["item"] = filters["item"]
    if filters.get("warehouse"):
        conditions += " AND warehouse = %(warehouse)s"
        values["warehouse"] = filters["warehouse"]
    if filters.get("from_date"):
        conditions += " AND posting_date >= %(from_date)s"
        values["from_date"] = filters["from_date"]
    if filters.get("to_date"):
        conditions += " AND posting_date <= %(to_date)s"
        values["to_date"] = filters["to_date"]
    data = frappe.db.sql(f"""
        SELECT posting_date, item, warehouse, actual_qty,
               qty_after_transaction, valuation_rate, voucher_type, voucher_no
        FROM `tabBA Stock Ledger Entry`
        {conditions}
        ORDER BY posting_date DESC, creation DESC
    """, values, as_dict=True)
    return columns, data
