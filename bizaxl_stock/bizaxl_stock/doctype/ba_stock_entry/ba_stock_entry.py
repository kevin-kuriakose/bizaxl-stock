import frappe
from frappe.model.document import Document
from frappe.utils import flt


class BAStockEntry(Document):

    def validate(self):
        self.calculate_totals()
        self.validate_warehouses()

    def calculate_totals(self):
        total = 0
        for item in self.items:
            item.amount = flt(item.qty) * flt(item.basic_rate)
            total += item.amount
        self.total_amount = total

    def validate_warehouses(self):
        for item in self.items:
            if self.stock_entry_type == "Material Receipt" and not item.t_warehouse:
                item.t_warehouse = self.to_warehouse
            elif self.stock_entry_type == "Material Issue" and not item.s_warehouse:
                item.s_warehouse = self.from_warehouse
            elif self.stock_entry_type == "Material Transfer":
                if not item.s_warehouse:
                    item.s_warehouse = self.from_warehouse
                if not item.t_warehouse:
                    item.t_warehouse = self.to_warehouse

    def on_submit(self):
        self.make_stock_ledger_entries()

    def on_cancel(self):
        frappe.db.set_value("BA Stock Ledger Entry",
            {"voucher_type": "BA Stock Entry", "voucher_no": self.name},
            "is_cancelled", 1)

    def make_stock_ledger_entries(self):
        from bizaxl_stock.bizaxl_stock.stock_handler import make_sle

        for item in self.items:
            # Source warehouse — decrease stock
            if item.s_warehouse:
                make_sle(
                    item_code=item.item_code,
                    warehouse=item.s_warehouse,
                    actual_qty=-flt(item.qty),
                    incoming_rate=0,
                    posting_date=self.posting_date,
                    voucher_type="BA Stock Entry",
                    voucher_no=self.name,
                    batch_no=item.batch_no,
                )
            # Target warehouse — increase stock
            if item.t_warehouse:
                make_sle(
                    item_code=item.item_code,
                    warehouse=item.t_warehouse,
                    actual_qty=flt(item.qty),
                    incoming_rate=flt(item.basic_rate),
                    posting_date=self.posting_date,
                    voucher_type="BA Stock Entry",
                    voucher_no=self.name,
                    batch_no=item.batch_no,
                )
