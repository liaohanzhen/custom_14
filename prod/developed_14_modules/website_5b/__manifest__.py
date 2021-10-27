# -*- coding: utf-8 -*-
{
    'name': "5B Website",

    'summary': """
        5B Custom website module""",

    'description': """
        5B Custom website module
    """,

    'author': "Lekha Paudel",
    'website': "http://www.5b.com.au",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Website',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['web', 'website', 'http_routing'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/home.xml',
        'views/about.xml',
        'views/projects.xml',
        'views/solutions.xml',
        'views/news.xml',
        'views/faqs.xml',
        'views/media.xml',
        'views/templates.xml',
        'views/contact.xml',
        'views/careers.xml',
        'views/joinus.xml',
        'views/views.xml',
        'views/team.xml',
        'views/page_static.xml',
        'views/success.xml',
        'views/failed.xml',
        'views/login.xml',
        'views/reset_password.xml',
        'views/http_routing_template_extend.xml',
        'views/ecosystem.xml',
        'views/sitemap.xml',
        'views/privacy_policy.xml',
        'views/terms_and_conditions.xml',
        'views/menu.xml',
        
    ],
    # only loaded in demonstration mode
    'qweb': [
        #'static/src/js/extended_template.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
}
