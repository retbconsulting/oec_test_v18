# -*- coding: utf-8 -*-

import base64
import functools
import json
import logging
import math
import re

from werkzeug import urls
import base64

from odoo import fields as odoo_fields, http, tools, _, SUPERUSER_ID
from odoo.exceptions import ValidationError, AccessError, MissingError, UserError, AccessDenied
from odoo.http import content_disposition, Controller, request, route
from odoo.tools import consteq
from odoo import http
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
import werkzeug.exceptions
import werkzeug.urls
import werkzeug.wrappers
#from odoo.addons.http_routing.models.ir_http import slug
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)

class PortalCotisation(CustomerPortal):

    @route(['/my-profil'], type='http', auth='user', website=True)
    def my_profil(self, cotisation=None, redirect=None, **post):
        values = {}
        partner = request.env.user.partner_id
        values = {'partner': partner,
                  'register_types': [["pm", "Personne morale"], ["pp1", "Personne physique à titre individuel"],
                                     ["pp2", "Personne physique exerçant en société"],
                                     ["pp3", "Personne physique en tant que salarié"],
                                     ["pp4", "Personne physique exerçant en tant qu'associé d'un cabinet inscrit"]]}
        return request.render("mandat_cotisation_management.my_profil", values)

    @route(['/cotisation/new/',
            '/cotisation/new/<model("oec.cotisation"):cotisation>',
            '/cotisation/<model("oec.cotisation"):cotisation>/justif/submit'], type='http', auth='user', website=True)
    def new_cotisation(self, cotisation=None, redirect=None, **post):
        _logger.error("Invoking new_cotisation !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        slug = request.env['ir.http']._slug
        values = {}
        partner = request.env.user.partner_id
        mode_registration = 1 if partner.mode_registration == 'pm' else 0
        previous_declaration = request.env['oec.cotisation'].sudo().search(
            [('partner_id', '=', partner.id), ('state', '=', 'comptabilise')])
        previous_declaration_years = [declaration.year for declaration in previous_declaration]

        configuration = request.env['oec.configuration'].sudo().search([], limit=1)
        suggested_years = [(str(num), str(num)) for num in range(2019, (datetime.now().year) + 1) if
                           str(num) not in previous_declaration_years]
        suggested_discount = [
            ('0%', _("0%")),
            ('50%', _("50%")),
            ('100%', _("100%")),
        ]

        date_open = datetime(year=int(suggested_years[0][0]), month=1, day=1)
        date_inscription = partner.date_inscription
        diff = 0
        if date_open and date_inscription:
            diff = (date_open.year - date_inscription.year) * 12 + date_open.month - date_inscription.month

        
        _logger.error("trying new_cotisation with :")
        if cotisation and not post:
            _logger.error(f"Missing field cotisation and not post : {post.get('total_i2')} vs {cotisation.total_i2}")
            values = {'year': str(cotisation.year),
                      'number_members': cotisation.number_members,
                      'amount_member': cotisation.amount_member,
                      'amount_member_c': cotisation.amount_member_c,
                      'number_members_2': cotisation.number_members_2,
                      'number_members_50': cotisation.number_members_50,
                      'number_members_exo': cotisation.number_members_exo,
                      'amount_member_2': cotisation.amount_member_2,
                      'total_f': cotisation.total_f,
                      'total_g': cotisation.total_g,
                      'total_g_2': cotisation.total_g_2,
                      'mandat_number': cotisation.mandat_number,
                      's_office_number': cotisation.s_office_number,
                      'ca': '{:,}'.format(cotisation.ca).replace(',', ' '),
                      'total_h': cotisation.total_h,
                      'total_i': cotisation.total_i,
                      'total_i2': cotisation.total_i2,
                      'total_j': cotisation.total_j,
                      'total': cotisation.total,
                      'id': cotisation.id,
                      'state': cotisation.state,
                      'name': partner.name,
                      'prenom': partner.second_name,
                      'cotisation': cotisation.id,
                      'mode_registration': mode_registration,
                      'suggested_years': suggested_years,
                      'partner': partner,
                      'amount_member': int(configuration.amount_member),
                      'amount_member_2': int(configuration.amount_member),
                      'amount_member_c': int(configuration.cotisation_morale),
                      'justif_ca': cotisation.justif_ca_filename, ###########################################
                      'justif_ca_file': base64.b64decode(cotisation.justif_ca_file) if cotisation.justif_ca_file else None,
                      'diff': diff,
                      'modalite_payment': cotisation.modalite_payment,
                      'numero_cheque': cotisation.numero_cheque,
                      'amount_cheque': cotisation.amount_cheque,
                      'discount': str(cotisation.discount),
                      'suggested_discount': suggested_discount}
            return request.render("mandat_cotisation_management.oec_portal_new_cotisation", values)

        if not cotisation and post and request.httprequest.method == 'POST':
            _logger.error(f"Missing field not cotisation and post : {post.get('total_i2')}")

            cotisation = request.env['oec.cotisation'].sudo().create({
                'year': post.get('year'),
                'number_members': post.get('number_members'),
                'amount_member': post.get('amount_member'),
                'amount_member_c': configuration.cotisation_morale,
                'number_members_2': post.get('number_members_2'),
                'number_members_50': post.get('number_members_50'),
                'number_members_exo': post.get('number_members_exo'),
                'mandat_number': post.get('mandat_number'),
                's_office_number': post.get('s_office_number'),
                'amount_member_2': configuration.amount_member,
                'total_f': post.get('total_f'),
                'total_g': post.get('total_g'),
                'total_g_2': post.get('total_g_2'),
                'ca': post.get('ca').replace(" ", ""),
                'total_h': post.get('total_h'),
                'total_i': post.get('total_i'),
                'total_i2': post.get('total_i2'),
                'total_j': post.get('total_j'),
                'total': post.get('total'),
                'discount': post.get('discount'),  # Fix applied here
                'partner_id': partner.id})

            if post.get('justif_ca'):
                justif_file = post.get('justif_ca')
                # request.session['last_uploaded_file'] = justif_file.read()
                justif_filename = post.get('justif_ca').filename
                post.update({'justif_ca': base64.b64encode(justif_file.read())})
                cotisation.sudo().write(
                    {'justif_ca_file': post.get('justif_ca'), 'justif_ca_filename': justif_filename})

            return werkzeug.utils.redirect("/cotisation/new/%s" % slug(cotisation))

        if cotisation and post and request.httprequest.method == 'POST' and not post.get('modalite_payment'):
            cotisation = request.env['oec.cotisation'].sudo().browse(int(cotisation))
            _logger.error(f"Missing field cotisation and post : {post.get('total_i2')}")

            cotisation.sudo().write({'year': post.get('year'),
                                     'number_members': post.get('number_members'),
                                     'amount_member': post.get('amount_member'),
                                     'amount_member_c': int(configuration.cotisation_morale),
                                     'number_members_2': post.get('number_members_2'),
                                     'number_members_50': post.get('number_members_50'),
                                     'number_members_exo': post.get('number_members_exo'),
                                     'amount_member_2': int(configuration.amount_member),
                                     'mandat_number': post.get('mandat_number'),
                                     's_office_number': post.get('s_office_number'),
                                     'total_f': post.get('total_f'),
                                     'total_g': post.get('total_g'),
                                     'total_g_2': post.get('total_g_2'),
                                     'ca': post.get('ca').replace(" ", ""),
                                     'total_h': post.get('total_h'),
                                     'total_i': post.get('total_i'),
                                     'total_i2': post.get('total_i2'),
                                     'total_j': post.get('total_j'),
                                     'total': post.get('total'),
                                     'partner_id': partner.id,
                                     'modalite_payment': post.get('modalite_payment'),
                                     'numero_cheque': post.get('numero_cheque'),
                                     'amount_cheque': post.get('amount_cheque'),
                                     'discount': post.get('discount'),
                                     })
            cotisation.total_i2 = post.get('total_i2')

            '''if post.get('justif'):
                justif_file = post.get('justif')
                justif_filename = post.get('justif').filename
                post.update({'justif': base64.b64encode(justif_file.read())})
                cotisation.sudo().write({'justif_file': post.get('justif'), 'justif_filename': justif_filename})'''

            if post.get('justif_ca'):
                justif_file = post.get('justif_ca')
                # request.session['last_uploaded_file'] = justif_file.read()
                justif_filename = post.get('justif_ca').filename
                post.update({'justif_ca': base64.b64encode(justif_file.read())})
                cotisation.sudo().write(
                    {'justif_ca_file': post.get('justif_ca'), 'justif_ca_filename': justif_filename})

            return werkzeug.utils.redirect("/cotisation/new/%s" % slug(cotisation))

        if cotisation and post and request.httprequest.method == 'POST' and post.get('modalite_payment'):
            _logger.error("here in 4")
            cotisation = request.env['oec.cotisation'].sudo().browse(int(cotisation))
            cotisation.sudo().write({'modalite_payment': post.get('modalite_payment'),
                                     'numero_cheque': post.get('numero_cheque'),
                                     'amount_cheque': post.get('amount_cheque')})
            if post.get('justificatif'):
                justif_file = post.get('justificatif')
                justif_filename = post.get('justificatif').filename
                post.update({'justificatif': base64.b64encode(justif_file.read())})
                cotisation.sudo().write(
                    {'justificatif': post.get('justificatif'), 'justificatif_filename': justif_filename})
            cotisation.button_waiting_payment_validation()

            return request.render("mandat_cotisation_management.portal_cotisation_submit_success")

        _logger.error('outside!!!')

        values = {'state': 'draft',
                  'name': partner.name,
                  'prenom': partner.second_name,
                  'partner': partner,
                  'amount_member': int(configuration.amount_member),
                  'amount_member_2': int(configuration.amount_member),
                  'amount_member_c': int(configuration.cotisation_morale),
                  'suggested_years': suggested_years,
                  'suggested_discount': suggested_discount,
                  'diff': diff}
        return request.render("mandat_cotisation_management.oec_portal_new_cotisation", values)

    @route(['/cotisations'], type='http', auth='user', website=True)
    def cotisations_list(self, redirect=None, **post):
        values = {}
        partner = request.env.user.partner_id
        parent_cotisations = []
        if partner.parent_id:
            parent = partner.parent_id
            parent_cotisations = request.env['oec.cotisation'].sudo().search([('partner_id', '=', parent.id)])
        cotisations = request.env['oec.cotisation'].sudo().search([('partner_id', '=', partner.id)])
        values.update(
            {
                'cotisations': cotisations,
                'parent_cotisations': parent_cotisations,
                'partner': partner
            }
        )
        return request.render("mandat_cotisation_management.portal_cotisations", values)

    @route(['/cotisation/<string:id>/submit'], type='http', auth='public', website=True)
    def cotisation_submit(self, redirect=None, id=None, **post):
        cotisation = request.env['oec.cotisation'].sudo().browse(int(id))
        cotisation.button_in_progress()
        cotisation.declaration_date = datetime.now()
        return request.render("mandat_cotisation_management.portal_cotisation_submit_success")

    @route(['/cotisation/<string:id>/justif/submit'], type='http', auth='public', website=True)
    def cotisation_submit_justif(self, redirect=None, id=None, **post):
        cotisation = request.env['oec.cotisation'].sudo().browse(int(id))
        '''numero_cheque = fields.Char(string='Numéro de chèque')
        amount_cheque = fields.Float(string="Montant du chèque")
        modalite_payment =  fields.Selection(string="Type de rejet", selection='_get_modalites_payment', default='cheque')
        justificatif = fields.Binary(string="Justificatif du paiement")'''
        # cotisation.button_waiting_payment_validation()
        return request.render("mandat_cotisation_management.portal_cotisation_submit_success")
