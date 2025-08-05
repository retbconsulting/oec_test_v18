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


class PortalCotisation(CustomerPortal):

    @route(['/cotisation/new/',
            '/cotisation/new/<model("oec.cotisation"):cotisation>'], type='http', auth='user', website=True)
    def new_cotisation(self, cotisation=None, redirect=None, **post):
        slug = request.env['ir.http']._slug
        values = {}
        partner = request.env.user.partner_id
        suggested_years = [(str(num), str(num)) for num in range(2018, (datetime.now().year) + 1)]
        if cotisation and not post:
            values = {'year': cotisation.year, 'number_members': cotisation.number_members,
                      'amount_member': cotisation.amount_member,
                      'amount_member_c': cotisation.amount_member_c,
                      'number_members_2': cotisation.number_members_2,
                      'amount_member_2': cotisation.amount_member_2,
                      'total_f': cotisation.total_f,
                      'total_g': cotisation.total_g,
                      'total_g_2': cotisation.total_g_2,
                      'mandat_number': cotisation.mandat_number,
                      'ca': cotisation.ca,
                      'total_h': cotisation.total_h,
                      'total_i': cotisation.total_i,
                      'total_j': cotisation.total_j,
                      'total': cotisation.total,
                      'id': cotisation.id,
                      'state': cotisation.state,
                      'name': partner.name,
                      'prenom': partner.second_name,
                      'cotisation': cotisation.id,
                      'mode_registration': partner.mode_registration,
                      'suggested_years': suggested_years}
            return request.render("mandat_cotisation_management.oec_portal_new_cotisation", values)

        if not cotisation and post and request.httprequest.method == 'POST':
            cotisation = request.env['oec.cotisation'].sudo().create({
                'year': post.get('year'),
                'number_members': post.get('number_members'),
                'amount_member': post.get('amount_member'),
                'amount_member_c': post.get('amount_member_c'),
                'number_members_2': post.get('number_members_2'),
                'mandat_number': post.get('mandat_number'),
                'amount_member_2': post.get('amount_member_2'),
                'total_f': post.get('total_f'),
                'total_g': post.get('total_g'),
                'total_g_2': post.get('total_g_2'),
                'ca': post.get('ca'),
                'total_h': post.get('total_h'),
                'total_i': post.get('total_i'),
                'total_j': post.get('total_j'),
                'total': post.get('total'),
                'partner_id': partner.id,
                'mode_registration': partner.mode_registration,
                'suggested_years': suggested_years
            })

            return werkzeug.utils.redirect("/cotisation/new/%s" % slug(cotisation))

        if cotisation and post and request.httprequest.method == 'POST':
            cotisation = request.env['oec.cotisation'].sudo().browse(int(cotisation))

            cotisation.sudo().write({'year': post.get('year'),
                                     'number_members': post.get('number_members'),
                                     'amount_member': post.get('amount_member'),
                                     'amount_member_c': post.get('amount_member_c'),
                                     'number_members_2': post.get('number_members_2'),
                                     'amount_member_2': post.get('number_members_2'),
                                     'mandat_number': post.get('mandat_number'),
                                     'total_f': post.get('total_f'),
                                     'total_g': post.get('total_g'),
                                     'total_g_2': post.get('total_g_2'),
                                     'ca': post.get('ca'),
                                     'total_h': post.get('total_h'),
                                     'total_i': post.get('total_i'),
                                     'total_j': post.get('total_j'),
                                     'total': post.get('total'),
                                     'partner_id': partner.id,
                                     'mode_registration': partner.mode_registration,
                                     'suggested_years': suggested_years})

            print(post.get('justif'))
            if post.get('justif'):
                justif_file = post.get('justif')
                justif_filename = post.get('justif').filename
                post.update({'justif': base64.b64encode(justif_file.read())})
                cotisation.sudo().write({'justif_file': post.get('justif'), 'justif_filename': justif_filename})

            return werkzeug.utils.redirect("/cotisation/new/%s" % slug(cotisation))

        values = {'state': 'draft', 'name': partner.name,
                  'prenom': partner.second_name}
        return request.render("mandat_cotisation_management.oec_portal_new_cotisation", values)

    @route(['/cotisations'], type='http', auth='user', website=True)
    def cotisations_list(self, redirect=None, **post):
        values = {}
        partner = request.env.user.partner_id
        cotisations = request.env['oec.cotisation'].sudo().search([('partner_id', '=', partner.id)])
        values.update({'cotisations': cotisations,
                       'partner': partner})
        return request.render("mandat_cotisation_management.portal_cotisations", values)

    @route(['/cotisation/<string:id>/submit'], type='http', auth='public', website=True)
    def cotisation_submit(self, redirect=None, id=None, **post):
        cotisation = request.env['oec.cotisation'].sudo().browse(int(id))
        cotisation.button_in_progress()
        return request.render("mandat_cotisation_management.portal_cotisation_submit_success")

    @route(['/cotisation/<string:id>/justif/submit'], type='http', auth='public', website=True)
    def cotisation_submit_justif(self, redirect=None, id=None, **post):
        cotisation = request.env['oec.cotisation'].sudo().browse(int(id))
        cotisation.button_waiting_payment_validation()
        return request.render("mandat_cotisation_management.portal_cotisation_submit_success")


    #### Other new cotisation controller
    @route(['/oec/cotisation/new/',
            '/oec/cotisation/new/<model("oec.cotisation"):cotisation>'], type='http', auth='user', website=True)
    def oec_new_cotisation(self, cotisation=None, redirect=None, **post):
        slug = request.env['ir.http']._slug
        values = {}
        partner = request.env.user.partner_id
        suggested_years = [(str(num), str(num)) for num in range(2018, (datetime.now().year) + 1)]
        if cotisation and not post:
            values = {'year': cotisation.year, 'number_members': cotisation.number_members,
                      'amount_member': cotisation.amount_member,
                      'amount_member_c': cotisation.amount_member_c,
                      'number_members_2': cotisation.number_members_2,
                      'amount_member_2': cotisation.amount_member_2,
                      'total_f': cotisation.total_f,
                      'total_g': cotisation.total_g,
                      'total_g_2': cotisation.total_g_2,
                      'mandat_number': cotisation.mandat_number,
                      'ca': cotisation.ca,
                      'total_h': cotisation.total_h,
                      'total_i': cotisation.total_i,
                      'total_j': cotisation.total_j,
                      'total': cotisation.total,
                      'id': cotisation.id,
                      'state': cotisation.state,
                      'name': partner.name,
                      'prenom': partner.second_name,
                      'cotisation': cotisation.id,
                      'mode_registration': partner.mode_registration,
                      'suggested_years': suggested_years}
            return request.render("mandat_cotisation_management.oec_portal_new_cotisation", values)

        if not cotisation and post and request.httprequest.method == 'POST':
            cotisation = request.env['oec.cotisation'].sudo().create({
                'year': post.get('year'),
                'number_members': post.get('number_members'),
                'amount_member': post.get('amount_member'),
                'amount_member_c': post.get('amount_member_c'),
                'number_members_2': post.get('number_members_2'),
                'mandat_number': post.get('mandat_number'),
                'amount_member_2': post.get('amount_member_2'),
                'total_f': post.get('total_f'),
                'total_g': post.get('total_g'),
                'total_g_2': post.get('total_g_2'),
                'ca': post.get('ca'),
                'total_h': post.get('total_h'),
                'total_i': post.get('total_i'),
                'total_j': post.get('total_j'),
                'total': post.get('total'),
                'partner_id': partner.id,
                'mode_registration': partner.mode_registration,
                'suggested_years': suggested_years
            })

            return werkzeug.utils.redirect("/oec/cotisation/new/%s" % slug(cotisation))

        if cotisation and post and request.httprequest.method == 'POST':
            cotisation = request.env['oec.cotisation'].sudo().browse(int(cotisation))

            cotisation.sudo().write({'year': post.get('year'),
                                     'number_members': post.get('number_members'),
                                     'amount_member': post.get('amount_member'),
                                     'amount_member_c': post.get('amount_member_c'),
                                     'number_members_2': post.get('number_members_2'),
                                     'amount_member_2': post.get('number_members_2'),
                                     'mandat_number': post.get('mandat_number'),
                                     'total_f': post.get('total_f'),
                                     'total_g': post.get('total_g'),
                                     'total_g_2': post.get('total_g_2'),
                                     'ca': post.get('ca'),
                                     'total_h': post.get('total_h'),
                                     'total_i': post.get('total_i'),
                                     'total_j': post.get('total_j'),
                                     'total': post.get('total'),
                                     'partner_id': partner.id,
                                     'mode_registration': partner.mode_registration,
                                     'suggested_years': suggested_years})

            print(post.get('justif'))
            if post.get('justif'):
                justif_file = post.get('justif')
                justif_filename = post.get('justif').filename
                post.update({'justif': base64.b64encode(justif_file.read())})
                cotisation.sudo().write({'justif_file': post.get('justif'), 'justif_filename': justif_filename})

            return werkzeug.utils.redirect("/oec/cotisation/new/%s" % slug(cotisation))

        values = {'state': 'draft', 'name': partner.name,
                  'prenom': partner.second_name}
        return request.render("mandat_cotisation_management.oec_portal_new_cotisation", values)
