# BizAxl Stock

Stock & Inventory management for BizAxl ERP.

## Requires
- bizaxl_erp

## DocTypes
- BA Item, BA Item Group, BA Warehouse
- BA Stock Entry (receipt, issue, transfer)
- BA Stock Ledger Entry (audit trail)
- BA Item Price, BA Batch, BA Serial No

## Installation
```bash
bench get-app https://github.com/kevin-kuriakose/bizaxl-stock.git
bench --site yoursite install-app bizaxl_stock
bench --site yoursite migrate
```
