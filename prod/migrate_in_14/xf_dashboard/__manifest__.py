# -*- coding: utf-8 -*-
{
    'name': 'XF Home Dashboard',
    'version': '1.2.0',
    'summary': """
    Intranet Dashboard and Landing Page with Customizable Widgets
    
    | Intranet Portal Page
    | Corporate Portal
    | Home Page Dashboard
    | Employee Dashboard
    | Employee Portal
    | Employee Intranet
    | Employee Quick Links
    | Most Visited Modules
    | Most Visited Apps
    | Home Dashboard Widgets
    """,
    'category': 'Extra Tools, Dashboard, Design',
    'author': 'XFanis',
    'support': 'dev@xfanis.ru',
    'website': 'https://xfanis.ru',
    'license': 'OPL-1',
    'price': 35,
    'currency': 'EUR',
    'description':
        """
XF Home Dashboard
=================
This module allows to create intranet home/landing page with several built-in widgets. 
Also module supports adding custom widgets. 
The procedure for adding new sub-modules with widgets is easy even for inexperienced developers.

Built-in widgets:
* Hello Widget
* Logo Widget
* Bookmarks (list + tiles)
* Popular Links (separate for each user and based on their activity)


----------------------

You can create custom widgets through administration panel using existing built-in widgets code as example. 
Each widget has many setting options to be able to customize it without writing code.
But if there are any complications, do not hesitate to contact me and I will try to help you.
If you have an idea or suggestion for a widget for this dashboard, you can share it with me. 
If I like the idea, I will implement this widget and publish it in the Odoo app store for free.

        """,
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/assets.xml',
        'views/menu.xml',
        'data/rows.xml',
        'views/adm_panel/dashboard.xml',
        'views/adm_panel/bookmarks.xml',
        'views/widgets/default_templates.xml',
        'views/widgets/bookmarks.xml',
        'views/widgets/tiles.xml',
        'views/widgets/hello.xml',
        'views/widgets/logo.xml',
        'views/widgets/popular_links.xml',
        'wizard/xf_dashboard_widget_template.xml',
        'data/icons.xml',
    ],
    'demo': [
        'data/demo.xml'
    ],
    'depends': ['web'],
    'qweb': [
        'static/src/xml/*.xml',
    ],
    'images': [
        'static/description/desktop_screenshot.png',
        'static/description/large_devices_screenshot.png',
        'static/description/medium_devices_screenshot.png',
        'static/description/small_devices_screenshot.png',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
