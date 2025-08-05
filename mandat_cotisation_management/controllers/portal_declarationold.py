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


class PortalDeclaration(CustomerPortal):
    
    
    @route(['/declarations'], type='http', auth='user', website=True)
    def declarations(self, redirect=None, **post):
        values = {}
        partner = request.env.user.partner_id
        declarations = request.env['oec.mandat.declaration'].sudo().search([('partner_id', '=', partner.id)])
        values.update({'declarations': declarations})
        return request.render("mandat_cotisation_management.declarations", values)
    
    @route(['/declaration/<model("oec.mandat.declaration"):declaration>',
            '/declaration'], type='http', auth='user', website=True)
    def new_declaration(self, redirect=None, declaration=None, **post):
        if post and request.httprequest.method == 'POST':
            declaration = request.env['oec.mandat.declaration'].sudo().search([('id', '=', post.get('id'))])
            declaration.sudo().write({'poids_ca' : post.get('poids_ca'),
                                      'nombre_bureaux' : post.get('nombre_bureaux'),
                                      'reseau_appartenance' : post.get('reseau_appartenance'),
                                      'number_pages' : post.get('number_pages'),
                                      'effectif_audit' : post.get('effectif_audit'),
                                      'directeurs_mission' : post.get('directeurs_mission'),
                                      'responsables_mission' : post.get('responsables_mission'),
                                      'auditeurs' : post.get('auditeurs'),
                                      'responsables_mission' : post.get('responsables_mission'),
                                      'autres_cas' : post.get('autres_cas'),
                                      'sous_traitance' : post.get('sous_traitance'),
                                      'number_associes' : post.get('number_associes'),
                                      'number_associes_ec' : post.get('number_associes_ec'),
                                      'number_salaries_ec' : post.get('number_salaries_ec'),
                                      'list_associes_signature' : post.get('list_associes_signature')})
            
            if post.get('mandats_canevas'):
                file = post.get('mandats_canevas')
                file_content = base64.b64encode(file.read())
                file_content_binary = base64.decodestring(file_content)
                file_content_binary = file_content_binary.decode("ISO-8859-1")
                if file_content_binary:
                    file_content_reader = file_content_binary.split('\n')
                    data = {}
                    i = 0
                    for row in file_content_reader:
                        i += 1
                        if i == 1:
                            continue
                        line = row.split(';')
                        if len(line) == 1:
                            continue
                        empty_row = True
                        for l in line:
                            if l.strip():
                                empty_row = False
                                break
                        if empty_row:
                            continue
                    
                        request.env['oec.mandat'].sudo().create({
                                                             'secteur_activite': line[0],
                                                             'forme_juridique': line[1],
                                                             'mandat_declaration_id': declaration.id})
            return werkzeug.utils.redirect("/declaration/%s" % slug(declaration))
            
        declaration._get_mandats_number()
        values = {'state' : declaration.state, 
                  'name': declaration.partner_id.name,
                  'prenom': declaration.partner_id.second_name, 
                  'partner':declaration.partner_id,
                  'declaration':declaration,
                  'mandats': declaration.oec_mandat_ids}
        return request.render("mandat_cotisation_management.new_declaration", values)
    
    
    @route(['/declaration/<model("oec.mandat.declaration"):declaration>/duplicate'], type='http', auth='user', website=True)
    def duplicate_declaration(self, redirect=None, declaration=None, **post):
        partner = request.env.user.partner_id
        previous_declaration = request.env['oec.mandat.declaration'].search([('partner_id', '=', partner.id), ('id', '!=', declaration.id)], limit=1, order="id desc")
        if previous_declaration:
            for mandat in previous_declaration.oec_mandat_ids:
                mandat.copy({'mandat_declaration_id': declaration.id})
        return werkzeug.utils.redirect("/declarations")
    
    @route(['/declaration/<model("oec.mandat.declaration"):declaration>/load'], type='http', auth='user', website=True)
    def load_mandats(self, redirect=None, declaration=None, **post):
        partner = request.env.user.partner_id
        print ('Hello')
        return werkzeug.utils.redirect("/declaration/%s" % slug(declaration))
        
    @route(['/declaration/<model("oec.mandat.declaration"):declaration>/submit'], type='http', auth='public', website=True)
    def declaration_submit(self, redirect=None, declaration=None, **post):
        #mandat = request.env['oec.mandat'].sudo().browse(int(id))
        declaration.button_in_progress()
        return request.render("mandat_cotisation_management.portal_declaration_submit_success")
