# -*- coding: utf-8 -*-
{
    "name": "Google Drive Odoo Integration",
    "version": "14.0.1.0.2",
    "category": "Document Management",
    "author": "faOtools",
    "website": "https://faotools.com/apps/14.0/google-drive-odoo-integration-512",
    "license": "Other proprietary",
    "application": True,
    "installable": True,
    "auto_install": False,
    "depends": [
        "cloud_base"
    ],
    "data": [
        "data/data.xml",
        "security/ir.model.access.csv",
        "views/res_config_settings.xml"
    ],
    "qweb": [
        
    ],
    "js": [
        
    ],
    "demo": [
        
    ],
    "external_dependencies": {
        "python": []
},
    "summary": "The tool to automatically synchronize Odoo attachments with Google Drive files in both ways",
    "description": """
For the full details look at static/description/index.html

* Features * 

- Sync any documents you like
- How synchronization works
- &lt;i class='fa fa-folder-open'&gt;&lt;/i&gt; Odoo Enterprise Documents



#odootools_proprietary

    """,
    "images": [
        "static/description/main.png"
    ],
    "price": "264.0",
    "currency": "EUR",
    "live_test_url": "https://faotools.com/my/tickets/newticket?&url_app_id=80&ticket_version=14.0&url_type_id=3",
}