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

class PortalFormation(CustomerPortal):
    
    FORMATION_FIELDS = ['subject', 'hours_number', 'date', 'animateur', 'organisme', 'city'] 
    FORMATION_TYPE = ['one', 'two', 'three', 'four', 'five']                   
    ITERATIONS = ['1', '2', '3', '4', '5']
    
    @route(['/formation/new/',
            '/formation/new/<model("oec.formation"):formation>'], type='http', auth='user', website=True)
    def new_formation(self, formation=None,redirect=None, **post):
        slug = request.env['ir.http']._slug
        values = {}
        partner = request.env.user.partner_id
        values.update({'partner': partner, 'state': 'draft'})
        if formation and not post:
            row = 1
            for formation_item in formation.sudo().oec_formation_one_ids:
                values.update({'subject_one_'+str(row) : formation_item.subject,
                                   'hours_number_one_'+str(row) : formation_item.hours_number,
                                   'date_one_'+str(row) : formation_item.date,
                                   'animateur_one_'+str(row) : formation_item.animateur,
                                   'organisme_one_'+str(row) : formation_item.organisme,
                                   'city_one_'+str(row) : formation_item.city})
                row += 1
            row = 1
            for formation_item in formation.sudo().oec_formation_two_ids:
                values.update({'subject_two_'+str(row) : formation_item.subject,
                                   'hours_number_two_'+str(row) : formation_item.hours_number,
                                   'date_two_'+str(row) : formation_item.date,
                                   'animateur_two_'+str(row) : formation_item.animateur,
                                   'organisme_two_'+str(row) : formation_item.organisme,
                                   'city_two_'+str(row) : formation_item.city})
                row += 1
            row = 1
            for formation_item in formation.sudo().oec_formation_three_ids:
                values.update({'subject_three_'+str(row) : formation_item.subject,
                                   'hours_number_three_'+str(row) : formation_item.hours_number,
                                   'date_three_'+str(row) : formation_item.date,
                                   'animateur_three_'+str(row) : formation_item.animateur,
                                   'organisme_three_'+str(row) : formation_item.organisme,
                                   'city_three_'+str(row) : formation_item.city})
                row += 1
            row = 1
            for formation_item in formation.sudo().oec_formation_four_ids:
                values.update({'subject_four_'+str(row) : formation_item.subject,
                                   'hours_number_four_'+str(row) : formation_item.hours_number,
                                   'date_four_'+str(row) : formation_item.date,
                                   'animateur_four_'+str(row) : formation_item.animateur,
                                   'organisme_four_'+str(row) : formation_item.organisme,
                                   'city_four_'+str(row) : formation_item.city})
                row += 1
            for formation_item in formation.sudo().oec_formation_five_ids:
                values.update({'subject_five_'+str(row) : formation_item.subject,
                                   'hours_number_five_'+str(row) : formation_item.hours_number,
                                   'date_five_'+str(row) : formation_item.date,
                                   'animateur_five_'+str(row) : formation_item.animateur,
                                   'organisme_five_'+str(row) : formation_item.organisme,
                                   'city_five_'+str(row) : formation_item.city})
                row += 1
            values.update({'formation': formation.sudo().id,
                           'id': formation.sudo().id,
                           'state': formation.sudo().state})
            return request.render("mandat_cotisation_management.new_formation", values)
        
        if not formation and post and request.httprequest.method == 'POST':
            FormationModel = request.env['oec.formation']
            formation = FormationModel.sudo().create({'partner_id': partner.id,
                                          'year': post.get('year')})
            for type in self.FORMATION_TYPE:
                model = 'oec.formation.' + type
                Model = request.env[model]
                for iteration in self.ITERATIONS:
                    if not post.get(self.FORMATION_FIELDS[0]+'_'+type+'_'+iteration) \
                        and not post.get(self.FORMATION_FIELDS[1]+'_'+type+'_'+iteration) \
                        and not post.get(self.FORMATION_FIELDS[2]+'_'+type+'_'+iteration) \
                        and not post.get(self.FORMATION_FIELDS[3]+'_'+type+'_'+iteration) \
                        and not post.get(self.FORMATION_FIELDS[4]+'_'+type+'_'+iteration) \
                        and not post.get(self.FORMATION_FIELDS[5]+'_'+type+'_'+iteration):
                        break;
                    Model.sudo().create({ self.FORMATION_FIELDS[0] : post.get(self.FORMATION_FIELDS[0]+'_'+type+'_'+iteration),
                                        self.FORMATION_FIELDS[1] : post.get(self.FORMATION_FIELDS[1]+'_'+type+'_'+iteration),
                                        self.FORMATION_FIELDS[2] : post.get(self.FORMATION_FIELDS[2]+'_'+type+'_'+iteration) if post.get(self.FORMATION_FIELDS[2]+'_'+type+'_'+iteration) else None,
                                        self.FORMATION_FIELDS[3] : post.get(self.FORMATION_FIELDS[3]+'_'+type+'_'+iteration),                                                              
                                        self.FORMATION_FIELDS[4] : post.get(self.FORMATION_FIELDS[4]+'_'+type+'_'+iteration),
                                        self.FORMATION_FIELDS[5] : post.get(self.FORMATION_FIELDS[5]+'_'+type+'_'+iteration),
                                        'oec_formation_id': formation.id})
            
            return werkzeug.utils.redirect("/formation/new/%s" % slug(formation))
        
        if formation and post and request.httprequest.method == 'POST':
            formation = request.env['oec.formation'].sudo().browse(int(formation))
            formation.sudo().oec_formation_one_ids.unlink()
            formation.sudo().oec_formation_two_ids.unlink()
            formation.sudo().oec_formation_three_ids.unlink()
            formation.sudo().oec_formation_four_ids.unlink()
            formation.sudo().oec_formation_five_ids.unlink()
            for type in self.FORMATION_TYPE:
                model = 'oec.formation.' + type
                Model = request.env[model]
                for iteration in self.ITERATIONS:
                    if not post.get(self.FORMATION_FIELDS[0]+'_'+type+'_'+iteration) \
                        and not post.get(self.FORMATION_FIELDS[1]+'_'+type+'_'+iteration) \
                        and not post.get(self.FORMATION_FIELDS[2]+'_'+type+'_'+iteration) \
                        and not post.get(self.FORMATION_FIELDS[3]+'_'+type+'_'+iteration) \
                        and not post.get(self.FORMATION_FIELDS[4]+'_'+type+'_'+iteration) \
                        and not post.get(self.FORMATION_FIELDS[5]+'_'+type+'_'+iteration):
                        break;
                    Model.sudo().create({ self.FORMATION_FIELDS[0] : post.get(self.FORMATION_FIELDS[0]+'_'+type+'_'+iteration),
                                        self.FORMATION_FIELDS[1] : post.get(self.FORMATION_FIELDS[1]+'_'+type+'_'+iteration),
                                        self.FORMATION_FIELDS[2] : post.get(self.FORMATION_FIELDS[2]+'_'+type+'_'+iteration) if post.get(self.FORMATION_FIELDS[2]+'_'+type+'_'+iteration) else None,
                                        self.FORMATION_FIELDS[3] : post.get(self.FORMATION_FIELDS[3]+'_'+type+'_'+iteration),                                                              
                                        self.FORMATION_FIELDS[4] : post.get(self.FORMATION_FIELDS[4]+'_'+type+'_'+iteration),
                                        self.FORMATION_FIELDS[5] : post.get(self.FORMATION_FIELDS[5]+'_'+type+'_'+iteration),
                                        'oec_formation_id': formation.id})
                return werkzeug.utils.redirect("/formation/new/%s" % slug(formation))
        return request.render("mandat_cotisation_management.new_formation", values)
    
    
    @route(['/formations'], type='http', auth='user', website=True)
    def formations_list(self, redirect=None, **post):
        values = {}
        partner = request.env.user.partner_id
        formations = request.env['oec.formation'].sudo().search([('partner_id', '=', partner.id)])
        values.update({'formations': formations,
                       'partner': partner})
        return request.render("mandat_cotisation_management.portal_formations", values)
    
    
    @route(['/formation/<string:id>/submit'], type='http', auth='public', website=True)
    def formation_submit(self, redirect=None, id=None, **post):
        formation = request.env['oec.formation'].sudo().browse(int(id))
        formation.sudo().button_confirm()
        return request.render("mandat_cotisation_management.portal_formation_submit_success")
    
 
