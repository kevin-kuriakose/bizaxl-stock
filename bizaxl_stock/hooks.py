app_name = "bizaxl_stock"
app_title = "BizAxl Stock"
app_publisher = "BizAxl"
app_description = "Stock & Inventory management for BizAxl ERP"
app_email = "dev@bizaxl.com"
app_license = "mit"
app_version = "1.0.0"

required_apps = ["frappe", "bizaxl_erp"]

doc_events = {
    "BA Sales Invoice": {
        "on_submit": "bizaxl_stock.stock_handler.on_sales_invoice_submit",
        "on_cancel": "bizaxl_stock.stock_handler.on_sales_invoice_cancel",
    },
    "BA Purchase Invoice": {
        "on_submit": "bizaxl_stock.stock_handler.on_purchase_invoice_submit",
        "on_cancel": "bizaxl_stock.stock_handler.on_purchase_invoice_cancel",
    },
}
