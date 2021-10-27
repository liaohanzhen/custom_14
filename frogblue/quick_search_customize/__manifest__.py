# -*- coding: utf-8 -*-
{
    "name": "Advance Search & Quick Search",
    "version": "1.0",
    "category": "Extra Tools",
    "summary": "Search on top of list view with your own customization fields.",
    "description": """
Allows advanced search on top of list view. This module allows one to customize own search columns for each model.
    """,
    "author": "Ivan Yang",
    "support": "ivan.yangkaivan@gmail.com",
    "maintainer": "Ivan Yang",
    "depends": [],
    "data": [
        "data/quick_search_data.xml",
        "security/quick_search_security.xml",
        "security/ir.model.access.csv",
        "views/webclient_templates.xml",
        "views/quick_search_views.xml",
        "views/res_config_settings_views.xml"
    ],
    "images": ["static/description/banner.png"],
    "qweb": [
        "static/src/xml/*.xml",
    ],
    "license": "OPL-1",
    "price": 39.99,
    "currency": "EUR",
    "demo": [],
    "live_test_url": "https://www.youtube.com/watch?v=jQqJeQ-plS8"
}