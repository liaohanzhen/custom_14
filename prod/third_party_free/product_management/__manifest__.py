# -*- coding: utf-8 -*-
{
    "name": "Product Management Interface",
    "version": "14.0.1.0.3",
    "category": "Sales",
    "author": "faOtools",
    "website": "https://faotools.com/apps/14.0/product-management-interface-501",
    "license": "Other proprietary",
    "application": True,
    "installable": True,
    "auto_install": False,
    "depends": [
        "product"
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/view.xml",
        "views/res_config_settings.xml",
        "wizard/change_prm_category.xml",
        "wizard/update_prm_attributes.xml",
        "wizard/update_prm_followers.xml",
        "wizard/update_prm_product_type.xml",
        "wizard/update_prm_price.xml",
        "views/product_template.xml",
        "views/menu.xml",
        "data/data.xml"
    ],
    "qweb": [
        "static/src/xml/*.xml"
    ],
    "js": [
        
    ],
    "demo": [
        
    ],
    "external_dependencies": {},
    "summary": "The tool to search, select and mass update product templates",
    "description": """
For the full details look at static/description/index.html

* Features * 

- Configurable mass actions for product templates



#odootools_proprietary

    """,
    "images": [
        "static/description/main.png"
    ],
    "price": "149.0",
    "currency": "EUR",
    "live_test_url": "https://faotools.com/my/tickets/newticket?&url_app_id=86&ticket_version=14.0&url_type_id=3",
}