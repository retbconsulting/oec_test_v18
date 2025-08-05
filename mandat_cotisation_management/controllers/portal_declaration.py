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
import xlrd
from io import BytesIO

_logger = logging.getLogger(__name__)

forme_juridique = [
            ('1', 'SA'),
            ('2','SARL'),
            ('3','SAS'),
            ('4','SARL AU'),
            ('5','SNC'),
            ('6','SCA'),
            ('7','SCS'),
            ('8','Association'),
            ('9','Coopérative'),
            ('10','Fond collectif'),
            ('11','OPVC'),
            ('12','OPCI'),
            ('13','Mutuelle'),
            ('14','Autres')
        ]
secteur_activite = [
            ('1','Agriculture / Agroalimentaire'),
            ('2','Bois/Papier/ Carton/Imprimerie'),
            ('3','Chimie/Parachimie'),
            ('5','Edition/Communication/Multimédia'),
            ('6','Etudes et Conseils'),
            ('7','Machine et équipements'),
            ('8','Plastique/Caoutchouc'),
            ('9','Textile/Habillement/Chaussure'),
            ('10','Banque/Assurance'),
            ('11','BTP/ Matériaux de construction'),
            ('12','Commerce/Négoce/Distribution'),
            ('13','Electronique/Electricité'),
            ('14','Industrie pharmaceutique'),
            ('15','Informatique/Télécoms'),
            ('16','Métallurgie/Travail du Metal'),
            ('17','Services aux entreprises'),
            ('18','Transport et Logistique'),
            ('19','Autres')]

nature_mission = [
            ('1', 'Audit légal'),
            ('2','Audil contractuel'),
            ('3','Autres missions légales'),
            ('4','Autres missions liées')
        ] 

yes_no = [
            ('1', 'Oui'),
            ('2','Non')
        ] 

class PortalDeclaration(CustomerPortal):
    
    
    @route(['/declarations'], type='http', auth='user', website=True)
    def declarations(self, redirect=None, **post):
        values = {}
        partner = request.env.user.partner_id
        parent_declarations = []
        if partner.parent_id:
            parent_declarations = request.env['oec.mandat.declaration'].sudo().search([('partner_id', '=', partner.parent_id.id)])
        declarations = request.env['oec.mandat.declaration'].sudo().search([('partner_id', '=', partner.id)])
        values.update(
            {
                'declarations': declarations, 
                'parent_declarations': parent_declarations
            }
        )
        return request.render("mandat_cotisation_management.declarations", values)
    
    @route(['/declaration/<model("oec.mandat.declaration"):declaration>',
            '/declaration'], type='http', auth='user', website=True)
    def new_declaration(self, redirect=None, declaration=None, **post):
        slug = request.env['ir.http']._slug
        _logger.error(f"post={post} ; request.httprequest.method={request.httprequest.method} ; declaration={declaration}")
        if declaration:
            print("------->>>>>>>>>>///\\\\\\ : ", declaration.list_associes_signature)
        if declaration and declaration.list_associes_signature and not post.get('list_associes_signature', None):
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            post.update({
                'list_associes_signature': declaration.list_associes_signature,
            })
        if post and request.httprequest.method == 'POST':
            print(post)
            declaration = request.env['oec.mandat.declaration'].sudo().search([('id', '=', post.get('id'))])
            # associes_signataires_ids = request.env['res.partner'].sudo().search([('id', 'in', list(map(int, post.get('list_associes_signature').split(', '))))])
            # print(associes_signataires_ids)
            associes_signataires_ids = list(filter(bool, map(lambda a: int(a) if a else None, post.get('list_associes_signature').split(', '))))
            print("sssssssssssssssssssssssssaaaaaaaaaaaaaaa : ", associes_signataires_ids)
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
                                      'list_associes_signature' : [(6, 0, associes_signataires_ids)]})
            
            if post.get('mandats_canevas'):
                file = post.get('mandats_canevas')
                book = xlrd.open_workbook(file_contents=file.read())
                sheet = book.sheets()[0]
                index = 0
                for rowx, row in enumerate(map(sheet.row, range(sheet.nrows)), 1):
                    index += 1
                    if index >= 3:
                        values = []
                        for colx, cell in enumerate(row, 1):
                            print(str(cell.value))
                            values.append(cell.value)
                        secteur_act = [v[0] for i, v in enumerate(secteur_activite) if v[1] == values[0]]
                        forme_juri = [v[0] for i, v in enumerate(forme_juridique) if v[1] == values[1]]
                        nature_mis = [v[0] for i, v in enumerate(nature_mission) if v[1] == values[12]]
                        entite_ape = [v[0] for i, v in enumerate(yes_no) if v[1] == values[2]]
                        in_group = [v[0] for i, v in enumerate(yes_no) if v[1] == values[3]]
                        nombre_autres_entite_groupe = [v[0] for i, v in enumerate(yes_no) if v[1] == values[4]]
                        #print(datetime(*xlrd.xldate.xldate_as_tuple(values[13], book.datemode)))
                        request.env['oec.mandat'].sudo().create({
                                                                 'secteur_activite': secteur_act[0],
                                                                 'forme_juridique': forme_juri[0],
                                                                 'entite_ape' : entite_ape[0],
                                                                 'in_group' : in_group[0],
                                                                 'nombre_autres_entite_groupe': nombre_autres_entite_groupe[0],
                                                                 'capitaux_propres' : values[5],
                                                                 'resultat_exercice': values[6],
                                                                 'total_actif' : values[7],
                                                                 'produit_exploitation' : values[8],
                                                                 'produit_financie' : values[9],
                                                                 'leasing_restant' : values[10],
                                                                 'honoraires_dernier_exercice_clos' : values[11],
                                                                 'nature_mission' : nature_mis[0],
                                                                 'date_designation' : datetime(*xlrd.xldate.xldate_as_tuple(values[13], book.datemode)),
                                                                 'mode_designation' : values[14],
                                                                 'exercces_couverts_par_le_mandat' : [(6, 0, [values[15]])],
                                                                 'coCac' : values[16],
                                                                 'dernier_exercice_control' : values[17],
                                                                 'nombre_reserves_pour_limitation' : values[19],
                                                                 'nombre_reserves_pour_incertitudes' : values[20],
                                                                 'nombre_reserves_pour_desacord' : values[21],
                                                                 'nombre_observation' : values[22],
                                                                 'associe_signataire' : values[23],                              
                                                                 'budget_temps_selon_norme' : values[24],
                                                                 'budget_retenu_effort' : values[25],
                                                                 'budget_temps_realises' : values[26],
                                                                 'temps_passe_associe' : values[27],
                                                                 'autres_missions_realises' : values[28],
                                                                 'honoraires_autres_mission' : values[29],
                                                                 'rapport_opinion' : values[31],
                                                                 'rapport_controle_interne' : values[32],
                                                                 'rapport_detaille_comptes' : values[33],
                                                                 'rapport_special' : values[34],
                                                                 'autres_rapports' : values[35],
                                                                 'partner_id': declaration.partner_id.id,
                                                                 'mandat_declaration_id': declaration.id})
            return werkzeug.utils.redirect("/declaration/%s" % slug(declaration))
        
        print ([associe.id for associe in declaration.list_associes_signature])
        partners = request.env['res.partner'].search([])
        declaration._get_mandats_number()
        values = {'state' : declaration.state, 
                  'name': declaration.partner_id.name,
                  'prenom': declaration.partner_id.second_name, 
                  'partner':declaration.partner_id,
                  'mode_exercice': dict(declaration.partner_id._get_registration_mode()).get(declaration.partner_id.mode_registration, ''),
                  'forme_juridique': dict(declaration.partner_id._get_formes_juridiques()).get(declaration.partner_id.legal_form, ''),
                  'declaration':declaration,
                  'mandats': declaration.oec_mandat_ids,
                  'partners':partners,
                  'associes': [associe.id for associe in declaration.list_associes_signature],
                  'list_associes_signature': ', '.join(list(map(lambda a: str(a.id), declaration.list_associes_signature)))}
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
        slug = request.env['ir.http']._slug
        partner = request.env.user.partner_id
        print ('Hello')
        return werkzeug.utils.redirect("/declaration/%s" % slug(declaration))
        
    @route(['/declaration/<model("oec.mandat.declaration"):declaration>/submit'], type='http', auth='public', website=True)
    def declaration_submit(self, redirect=None, declaration=None, **post):
        #mandat = request.env['oec.mandat'].sudo().browse(int(id))
        declaration.button_in_progress()
        return request.render("mandat_cotisation_management.portal_declaration_submit_success")
