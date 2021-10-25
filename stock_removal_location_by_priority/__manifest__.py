# -*- coding: utf-8 -*-

{
    "name": "Stock Removal Location by Priority",
    "summary": "Establish a removal priority on stock locations.",
    "version": "14.0.0.0.0",
    "author": "ForgeFlow, " "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "category": "Warehouse",
    "depends": ["stock_barcode", "stock"],
    "data": [
        "security/stock_security.xml",
        "views/res_config_settings_views.xml",
        "views/stock_location_view.xml",
        "report/report_deliveryslip.xml",
        "report/report_stock_picking_operations.xml",
    ],
    'qweb': [
    ],
    "license": "AGPL-3",
    "installable": True,
    "application": False,
    "pre_init_hook": "pre_init_hook",
}
