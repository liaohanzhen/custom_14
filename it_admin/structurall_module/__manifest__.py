# -*- coding: utf-8 -*-
{
    'name': 'structurall module',
    'version': '14.11',
    'summary': '',
    'category': 'General',
    'author': 'IT Admin',
    "website": "",
    'data': [
        
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/res_config_settings_views.xml',
        'views/resource_rental.xml',
        'views/contract_view.xml',
        'wizard/agregar_producto_view.xml',
        #'reports/contrato_report.xml',
        'reports/presupuesto_report.xml',
        'data/mail_template.xml',

        #New reports
        #Contrato de arrendamiento antiguo el nuevo es el de persona moral
        #'reports/contrato_arrendamiento_report.xml',
        'reports/adendum_report.xml',
        'reports/recibo_deposito.xml',
        'reports/contrato_financiamiento.xml',
        'reports/pagare_new_report.xml',
        #Nuevo contrato de arrendamiento
        'reports/contrato_persona_moral.xml',
        'reports/sale_report.xml',

        #New changes in views
        'views/so_rental_view.xml',
        'views/adendum_view.xml',
        'data/sequence_data.xml',
        'views/product_view.xml',
        'reports/requerimientos_contratos.xml',
        'reports/sale_order_template_ext.xml',
        'views/sales_team.xml',
        'views/product_pricelist.xml',
        'views/res_partner_view.xml',
        'wizard/crear_adendum_view.xml',
        'views/sale_view_action.xml',

        #FIX TO DIAS DE GRACIA ADD FIELD TO RES_COMPANY
        'views/res_company_view.xml',
        'views/payment_view.xml',


        ],
    'depends': ['resource_rental_mgt','contract','sale','stock'
    ],
    'qweb': [
            ], 

    'support': 'soporte@itadmin.com.mx',

}

