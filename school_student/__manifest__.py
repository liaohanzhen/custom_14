# -*- coding: utf-8 -*-


{
    'name': "School Student",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Extra Tools',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'school'],

    # always loaded
    'data': [
        'data/student.hobby.csv',
        'data/school.profile.csv',
        'data/school.student.csv',
        'data/student_data.xml',
        'security/ir.model.access.csv',

        'wizard/student_fees_update_wizard_view.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/menu.xml',
        'data/delete_data.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
