# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name" : "Project Portfolio",
    "author" : "Softhealer Technologies",
    "website": "https://www.softhealer.com",
    "support" : "support@softhealer.com",
    "category": "website",
    "summary": "show website project portfolio, manage project portfolio app, website project portfolio odoo, project portfolio module, attractive project portfolio",
    "description": """ Portfolio is a fully responsive module that display projects portfolio on website.
        Awesome Filterable projects allows you to create, manage and publish a very modern and outstanding filterable portfolio that can be filtered using smooth animations and cool image hover effects. """,
    "version":"14.0.2",
    "depends" : ["base", "website", "web", "project"],
    "application" : True,
    "data" : [ "security/ir.model.access.csv",
               "data/sh_website_portfolio_data.xml",
               "views/project_view.xml",
               "views/category_view.xml",
               "views/portfolio_template.xml",
            ],
    "images": ["static/description/background.png", ],
    "live_test_url": "https://youtu.be/K5oHpaSKsKg",
    "auto_install":False,
    "installable" : True,
    "price": 35,
    "currency": "EUR"   
}

