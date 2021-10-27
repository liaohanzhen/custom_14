# -*- coding: utf-8 -*-
{
    "name": "Cloud Sync for Enterprise Documents",
    "version": "14.0.1.0.2",
    "category": "Document Management",
    "author": "faOtools",
    "website": "https://faotools.com/apps/14.0/cloud-sync-for-enterprise-documents-517",
    "license": "Other proprietary",
    "application": True,
    "installable": True,
    "auto_install": False,
    "depends": [
        "cloud_base",
        "documents"
    ],
    "data": [
        "data/data.xml",
        "security/ir.model.access.csv",
        "views/views.xml",
        "views/documents_document.xml",
        "views/templates.xml"
    ],
    "qweb": [
        
    ],
    "js": [
        
    ],
    "demo": [
        
    ],
    "external_dependencies": {},
    "summary": "The technical extension to sync Odoo Enterprise Documents with cloud clients",
    "description": """
For the full details look at static/description/index.html

* Features * 




#odootools_proprietary

    """,
    "images": [
        "static/description/main.png"
    ],
    "price": "44.0",
    "currency": "EUR",
    "live_test_url": "https://faotools.com/my/tickets/newticket?&url_app_id=81&ticket_version=14.0&ticket_license=enterpise&url_type_id=3",
}