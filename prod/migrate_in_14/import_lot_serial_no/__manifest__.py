# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Import Serial Number and lot number in picking(Shipment/Delivery) from Excel File',
    'version': '14.0.0.1',
    'summary': 'This module helps to import serial number/Lot number with incoming shipment/delivery order using csv or excel file',
    'description': """
	BrowseInfo developed a new odoo/OpenERP module apps.
	This module is useful for import  serial number/Lot number with picking from Excel and CSV file .
        Its also usefull for import opening stock balance with serial number from XLS or CSV file.
	    -Import serial number.
        -Import lot number inside picking.
	-Import product lot number, import product serial number
	-Inventory import from CSV, stock import from CSV, Inventory adjustment import, Opening stock import. Import warehouse stock, Import product stock.Manage Inventory, import inventory with lot number, import inventory with serial number, import inventory adjustment with serial number, import inventory adjustment with lot number. import inventory data, import stock data, import opening stock with lot number, import lot number from excel, import serial number from excel.

	    -Import serial number in incoming shipment, import lot number in shipment.
        -Import lot number in delivery order.
	-Import product lot number in delivery, import product serial number in delivery note
	-delivery serial import from CSV, lot import from CSV, Inventory serial number import, serial number import. Import lot number stock, Import product serial on picking .Manage Inventory, import shipment with lot number, import delivery order with serial number, import lot number inside delivery order, import serial number inside delivery order. import lot number data, import serial number data, import stock lot number in picking, import lot number from excel, import serial number from excel.




 """,
    'author':'Alitec Pte Ltd',
    'license': 'LGPL-3',
    'website': 'alitec.sg',  
    'depends': ['base','sale','purchase','stock'],
    'data': [
              'security/ir.model.access.csv',
    		  'views/import_lot_serial_no_view.xml',
            ],
    'demo': [],
    'test': [],
    'installable':True,
    'auto_install':False,
    'application':False,
    "images":["static/description/Banner.png"],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
