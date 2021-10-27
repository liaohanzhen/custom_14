# -*- coding: utf-8 -*-

{
    'name' : 'CRM Extension for 5B Industries.',
    'version' : '0.1',
    "author": "Nikunj",
    "category" : "CRM",
    "description": """
- Force send Email stopped and its set in queue, so it is send when Email cron job executed.
- Added Checkbox in Crm Stage to auto create project if Lead/opportunity reach at that stage
    """,
    'depends' : ['crm','stock', 'project'],
    "data" : [
              "data/customer.segment.csv",
              "data/ir_sequence_data.xml",
              'security/ir.model.access.csv',
              "views/res_partner_view.xml",
              'views/crm_lead_view.xml',
              'views/product_template_view.xml',
              'views/templates.xml',
              'views/crm_stage_view.xml',
              'views/project_view.xml',
            ],
    'qweb': [
        "static/src/xml/kanban.xml",
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'post_init_hook': '_auto_create_category_if_not_exist',
}
