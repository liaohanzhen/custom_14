# -*- coding: utf-8 -*-

{
    'name' : "Sale, Purchase, Invoice, Employee and Expense Cost Center",
    "author": "Edge Technologies",
    'version': '14.0.1.0',
    'live_test_url': "https://youtu.be/VJzzEWQaPhU",
    "images":['static/description/main_screenshot.png'],
    'summary': 'This module helps user to add cost center in sale, purchase, invoice, employee and expense.',
    'description' : """
                    cost center, cost center in odoo, add cost center in odoo,
                    cost center on sales, cost center on sale order line,
                    cost center on purchase, cost center on purchase order line,
                    cost center on customer invoice, cost center on vendor bill,
                    cost center on invoice, cost center on employee,
                    cost center on employee expense, cost center on expense report. 

                    Cost Centers
cost centre Profit Center Cost centres Process Cost Centre Responsibility Centre
                    Odoo Cost Centers , expense Cost Centers
                    sale expense cost centers
                    Cost Centers  
                    Cost Accounting
                    cost budgeting
                    expense tracking
                    cost tracking 
                    expense budgeting 
                    expense cost
                    employee cost centers
                    manage different types of costs 
                    manage costs
                    Expense cost center
                    Manage different cost centers
Cost Principle , 
                cost managements 
                expense management 
                costing managements 
                account costing  


                    """,
    "license" : "OPL-1",
    'depends' : ['sale','sale_management','purchase', 'account','hr_expense','hr','stock'],
    'data': [
            'security/ir.model.access.csv',
            'views/cost_centers_view.xml',
            ],
    'installable': True,
    'auto_install': False,
    'price': 38,
    'currency': "EUR",
    'category': 'Accounting',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
