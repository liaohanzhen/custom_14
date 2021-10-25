# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
# noinspection PyStatementEffect
{
    'name': 'School Extended',
    'version': '1.1',
    'summary': 'School Management',
    'sequence': 10,
    'description': """School management""",
    'category': 'Extra Tools',
    'depends': ['school_student', ],
    'images': ['static/description/school.png'],
    'data': [
        'security/ir.model.access.csv',
        'views/student_view.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
