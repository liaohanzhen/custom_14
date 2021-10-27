# -*- coding: utf-8 -*-
{
    # Module Info
    'name': "Website Quick Order",
    'version': '1.0',
    'category': 'Website/Website',
    'summary': "This module is for creating a Quick Order from website",
    'description': "This module is for creating a Quick Order from website",

    # Author
    'author': "Rolustech",
    'website': "http://www.rolustech.com",

    # Dependencies
    'depends': ['base', 'website','website_sale', 'stock'],

    # Data
    'data': [
        "view/web_form.xml",
        "view/template.xml",
        "view/res_config_settings.xml"
    ],
    'qweb': [],

    # Technical Specif.
    'installable': True,
    'auto_install': False,
    'application': True,
}