{
    #  Information
    'name': 'Syscoon Sales Team Automation',
    'version': '14.0.0.1',
    'summary': 'Sales Team Automation',
    'description': 'Sales Team Automation',
    'category': 'Custom',

    # Author
    'author': 'Odoo-Ps',
    'website': 'https://www.odoo.com',
    'license': '',

    # Dependency
    'depends': ['sale_management', 'sale_crm'],
    'data': [
        'security/ir.model.access.csv',
        'views/sales_team_automation_views.xml'
    ],

    # Other
    'application': True,
    'installable': True,
    'auto_install': False,
}
