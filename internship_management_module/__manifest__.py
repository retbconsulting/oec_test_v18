# -*- coding: utf-8 -*-
{
    'name': 'Internship Management Module',
    "version": "18.0.0.0.0",
    'license': 'LGPL-3',
    "summary": "Internship Management Module",
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
        'documents',
        'website',
        'website_crm_partner_assign',
        'product',
        'website_slides',
        'website_membership',
        'web',
        'contacts_enterprise',
        'theme_default',
        'operating_unit',
        'hr',
        'mail_group',
        'mail_mobile',
        'mail_plugin',
        'web_studio',
        'website_profile',
        'auth_signup',
        'auth_oauth',
        'payment'
    ],
    'data': [
        # Data
        'data/auth_signup_data.xml',
        'data/mail_notification_templates.xml',
        'data/res_partner_security.xml',
        'data/res_partner_data.xml',
        'data/website_data.xml',
        #'data/custom_login_template.xml',

        # Wizards

        # Views
        'views/portal/portal_base_templates.xml',
        #'views/base/res_partner_views.xml',
        'views/base/res_school_year_views.xml',
        'views/portal/portal_templates.xml',
        'views/base/res_partner_type_views.xml',
        'views/base/res_partner_level_views.xml',
        'views/base/profil_change_views.xml',
        'views/portal/portal_submit_templates.xml',
        'views/survey/survey_survey_views.xml',
        'views/document/documents_document_view.xml',
        'views/document/documents_document_report_view.xml',
        'views/portal/portal_submit_report_templates.xml',
        'views/portal/portal_registration_templates.xml',
        'views/portal/portal_cotisation_templates.xml',
        'views/portal/portal_member_templates.xml',
        'views/oec/oec_committee_views.xml',
        'views/portal/portal_re_registration_templates.xml',
        'views/portal/portal_base_templates.xml',


        # Menu

        # Report
        'report/res_partner_report_view.xml',
        'report/res_partner_menu.xml',

        # Security
        'security/ir.model.access.csv',
    ],
    'images': ['static/description/icon.png'],
    'demo': [],
    'assets': {
        'web.assets_frontend': [
            'internship_management_module/static/src/css/header.css',
            'internship_management_module/static/src/css/footer.css',
            'pos_alpha55/static/src/css/login.css',
        ],
    },
    'installable': True,
    'application': True,
    'qweb': [],
}
