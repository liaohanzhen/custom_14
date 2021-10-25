# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'School',
    'version' : '1.1',
    'summary': 'School managment',
    'sequence': 10,
    'description': """School managment""",
    'category': 'Extra Tools',
    'depends' : [ ],
    'images': ['static/description/school.png'],
    'data': [
        'data/school_data.xml',
        'data/sequence.xml',
        'security/ir.model.access.csv',
        'views/school_view.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
