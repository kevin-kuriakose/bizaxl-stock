import frappe
from frappe.utils import flt
def execute(filters=None):
    filters = filters or {}
    columns = [
        {"fieldname": "item", "label": "Item", "fieldtype": "Link", "options": "BA Item", "width": 180},
        {"fieldname": "item_name", "label": "Item Name", "fieldtype": "Data", "width": 200},
        {"fieldname": "item_group", "label": "Item Group", "fieldtype": "Data", "width": 130},
        {"fieldname": "warehouse", "label": "Warehouse", "fieldtype": "Link", "options": "BA Warehouse", "width": 160},
        {"fieldname": "actual_qty", "label": "Qty", "fieldtype": "Float", "width": 100},
        {"fieldname": "valuation_rate", "label": "Val. Rate", "fieldtype": "Currency", "width": 120},
        {"fieldname": "stock_value", "label": "Stock Value", "fieldtype": "Currency", "width": 130},
    ]
    conditions = "WHERE sle.is_cancelled = 0"
    values = {}
    if filters.get("warehouse"):
        conditions += " AND sle.warehouse = %(warehouse)s"
        values["warehouse"] = filters["warehouse"]
    if filters.get("item"):
        conditions += " AND sle.item = %(item)s"
        values["item"] = filters["item"]
    data = frappe.db.sql(f"""
        SELECT sle.item, i.item_name, i.item_group, sle.warehouse,
               SUM(sle.actual_qty) as actual_qty,
               AVG(sle.valuation_rate) as valuation_rate,
               SUM(sle.actual_qty) * AVG(sle.valuation_rate) as stock_value
        FROM `tabBA Stock Ledger Entry` sle
        LEFT JOIN `tabBA Item` i ON i.name = sle.item
        {conditions}
        GROUP BY sle.item, sle.warehouse
        HAVING actual_qty != 0
        ORDER BY i.item_name
    """, values, as_dict=True)
    return columns, data
