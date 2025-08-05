# -*- coding: utf-8 -*-

{
    'name': 'OEC - Cotisations and Mandats',
    "version": "18.0.0.0.0",
    'license': 'LGPL-3',  

    "summary": "OEC - Cotisations and Mandats",
    "author": "R&B Consulting",
    "website": "https://www.r-bconsulting.com",
    "category": "Generic",
    'depends': [
        'base',
        'contacts',
        'portal',
        'account',
        'crm',
        'sale',
        'purchase',
        'survey',
        'mail',
        'internship_management_module',
        'operating_unit',
        'documents',
        'product',
        'web',
        'website_studio',


    ],

    'data': [
        # Views
        'views/oec_cotisation_views.xml',
        'views/oec_formation_views.xml',
        'views/oec_mandat_views.xml',
        'views/portal_cotisation_templates.xml',
        'views/portal_formation_templates.xml',
        'views/portal_mandat_templates.xml',
        'views/portal_declaration_templates.xml',
        'views/oec_mass_mailing_views.xml',
        #'views/base/res_partner_views.xml',
        # Security
        'security/ir.model.access.csv',
        # Report
        'report/cotisation_report.xml',
        'report/declaration_report.xml',  
        'report/paiement_receipt.xml',  

        # Data
        'data/mail_notification_templates.xml',
        'data/cotisation_data.xml',
        'data/mandat_data.xml',
        'data/ir_cron_run_report.xml',
    ],
    'demo': [
    ],
    'images': ['static/src/img/red-layer.png',
               'static/src/img/avatar.png',
               'static/src/img/background.png',
               'static/src/img/background-2.png',
               'static/src/img/background-3.png',
               'static/src/img/background-4.png',
               'static/src/img/location-drop.png',
               'static/src/img/logo-oec.png',
               'static/src/img/mes-controles-qualiti.png',
               'static/src/img/mes-cotisations.png',
               'static/src/img/mes-declarations.png',
               'static/src/img/mes-stagiaires.png',
               'static/src/img/mes-stagiaires-con.png',
               'static/src/img/mon-profil.png',
               'static/src/img/phone.png',
               'static/src/img/photo.png',
               'static/src/img/site-footer.png',
               'static/src/img/top-layer.png',
               'static/src/img/website.png',
               'static/src/img/white-layer.png'],

    'assets': {
        'web.assets_frontend': [


        ],

    },

    'installable': True,
    'application': True,
    'qweb': [],
}
