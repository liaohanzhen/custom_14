# -*- coding: utf-8 -*-
{
    "name": "Cloud Storage Solutions",
    "version": "14.0.1.1.2",
    "category": "Document Management",
    "author": "faOtools",
    "website": "https://faotools.com/apps/14.0/cloud-storage-solutions-516",
    "license": "Other proprietary",
    "application": True,
    "installable": True,
    "auto_install": False,
    "depends": [
        "mail"
    ],
    "data": [
        "data/data.xml",
        "data/cron.xml",
        "data/sync_formats_data.xml",
        "views/sync_model.xml",
        "views/ir_attachment.xml",
        "views/sync_log.xml",
        "views/res_config_settings.xml",
        "views/view.xml",
        "security/ir.model.access.csv"
    ],
    "qweb": [
        "static/src/components/attachment/attachment.xml",
        "static/src/components/attachment_box/attachment_box.xml",
        "static/src/xml/js_tree.xml"
    ],
    "js": [
        
    ],
    "demo": [
        
    ],
    "external_dependencies": {},
    "summary": "The technical core to synchronize your cloud storage solution with Odoo",
    "description": """
For the full details look at static/description/index.html

* Features * 




#odootools_proprietary

    """,
    "images": [
        "static/description/main.png"
    ],
    "price": "130.0",
    "currency": "EUR",
    "live_test_url": "https://faotools.com/my/tickets/newticket?&url_app_id=11&ticket_version=14.0&url_type_id=3",
}