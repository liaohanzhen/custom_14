{
    # App information

    'name': "Import Sale Order From Excel",
    'category': 'Sale',
    'version': '11.0',
    'summary': 'Save your time by easily manage large Sale Orders through Excel/CSV by Importing/Mass updating bulk Sales lines in one time & Export Order lines to Excel',
    'license': 'OPL-1',

    # Author

    "author": "Emipro Technologies Pvt. Ltd.",
    'website': 'http://www.emiprotechnologies.com/',
    'maintainer': 'Emipro Technologies Pvt. Ltd.',

    # Dependencies

    'depends': ['base', 'sale_management', 'sale'],

    'data': [
        'security/ir.model.access.csv',
        'security/sale_security_group.xml',
        'view/configuration_setting.xml',
        'wizard/import_order.xml',
        'wizard/process_order.xml',

    ],

    # Technical

    'images': ['static/description/Import-sale-order-from-excel-cover.jpg'],
    'installable': True,
    'auto_install': False,
    'application': True,
    'price': 25.00,
    'currency': 'EUR',

}
