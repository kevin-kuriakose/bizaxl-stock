import frappe
def execute(filters=None):
    filters = filters or {}
    columns = [
        {"fieldname": "item", "label": "Item", "fieldtype": "Link", "options": "BA Item", "width": 180},
        {"fieldname": "item_name", "label": "Item Name", "fieldtype": "Data", "width": 200},
        {"fieldname": "item_group", "label": "Group", "fieldtype": "Data", "width": 130},
        {"fieldname": "price_list_rate", "label": "Price", "fieldtype": "Currency", "width": 120},
        {"fieldname": "currency", "label": "Currency", "fieldtype": "Data", "width": 80},
        {"fieldname": "valid_from", "label": "Valid From", "fieldtype": "Date", "width": 100},
        {"fieldname": "valid_upto", "label": "Valid Upto", "fieldtype": "Date", "width": 100},
    ]
    data = frappe.db.sql("""
        SELECT ip.item, i.item_name, i.item_group,
               ip.price_list_rate, ip.currency,
               ip.valid_from, ip.valid_upto
        FROM `tabBA Item Price` ip
        LEFT JOIN `tabBA Item` i ON i.name = ip.item
        ORDER BY i.item_name
    """, as_dict=True)
    return columns, data
