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


SECTEURS_ACTIVITES = [['1', 'Agriculture / Agroalimentaire'],
            ['2','Bois/Papier/ Carton/Imprimerie'],
            ['3','Chimie/Parachimie'],
            ['5','Edition/Communication/Multimédia'],
            ['6','Etudes et Conseils'],
            ['7','Machine et équipements'],
            ['8','Plastique/Caoutchouc'],
            ['9','Textile/Habillement/Chaussure'],
            ['10','Banque/Assurance'],
            ['11','BTP/ Matériaux de construction'],
            ['12','Commerce/Négoce/Distribution'],
            ['13','Electronique/Electricité'],
            ['14','Industrie pharmaceutique'],
            ['15','Informatique/Télécoms'],
            ['16','Métallurgie/Travail du Metal'],
            ['17','Services aux entreprises'],
            ['18','Transport et Logistique'],
            ['19','Autres']]

NATURES_MISSION = [['1', 'Audit légal'],
            ['2','Audil contractuel'],
            ['3','Autres missions légales'],
            ['4','Autres missions liées']]

FORMES_JURIDIQUE = [['1', 'SA'],
            ['2','SARL'],
            ['3','SAS'],
            ['4','SARL AU'],
            ['5','SNC'],
            ['6','SCA'],
            ['7','SCS'],
            ['8','Association'],
            ['9','Coopérative'],
            ['10','Fond collectif'],
            ['11','OPVC'],
            ['12','OPCI'],
            ['13','Mutuelle'],
            ['14','Autres']]

MODES_DESIGNATIN = [["Appel d'offres", "Appel d'offres"],
            ['Désignation directe','Désignation directe']]


class PortalMandat(CustomerPortal):
    

    @route(['/declaration/<model("oec.mandat.declaration"):declaration>/mandat/<model("oec.mandat"):mandat>/delete'], type='http', auth='user', website=True)
    def delete_mandat(self, mandat=None,declaration=None, redirect=None, **post):
        slug = request.env['ir.http']._slug
        mandat.unlink()
        return werkzeug.utils.redirect("/declaration/%s" % slug(declaration))
        
    @route(['/mandat/new/',
             '/mandat/new/<model("oec.mandat"):mandat>',
             '/declaration/<model("oec.mandat.declaration"):declaration>/mandat/new',
             '/declaration/<model("oec.mandat.declaration"):declaration>/mandat/<model("oec.mandat"):mandat>'], type='http', auth='user', website=True)
    def new_mandat(self, mandat=None,redirect=None, declaration=None, **post):
        print(f"exercices={post.get('exercces_couverts_par_le_mandat')}")
        values = {}
        slug = request.env['ir.http']._slug
        partner = request.env.user.partner_id
        mode_registration = 1 if partner.mode_registration == 'pm' else 0
        print (declaration)
        if mandat and not post:
            _logger.error("the co_cac is : " + str(mandat.coCac))
            print("the co_cac is : " + str(mandat.coCac))
            values.update({'secteur_activite': mandat.secteur_activite,
                                                            'forme_juridique' : mandat.forme_juridique,
                                                             'entite_ape' : mandat.entite_ape,
                                                             'in_group' : mandat.in_group,
                                                             'nombre_autres_entite_groupe': mandat.nombre_autres_entite_groupe,
                                                             'capitaux_propres' : str(mandat.capitaux_propres).replace('.', ','),
                                                             'resultat_exercice': str(mandat.resultat_exercice).replace('.', ','),
                                                             'total_actif' : str(mandat.total_actif).replace('.', ','),
                                                             'produit_exploitation' : str(mandat.produit_exploitation).replace('.', ','),
                                                             'produit_financie' : str(mandat.produit_financie).replace('.', ','),
                                                             'leasing_restant' : str(mandat.leasing_restant).replace('.', ','),
                                                             'honoraires_dernier_exercice_clos' : str(mandat.honoraires_dernier_exercice_clos).replace('.', ','),
                                                             
                                                             'nature_mission' : mandat.nature_mission,
                                                             'date_designation' : mandat.date_designation,
                                                             'mode_designation' : mandat.mode_designation,
                                                             'exercces_couverts_par_le_mandat' : mandat.exercces_couverts_par_le_mandat,
                                                             'co_cac' : mandat.coCac,
                                                             'dernier_exercice_control' : mandat.dernier_exercice_control,
                                                             'nombre_reserves_pour_limitation' : mandat.nombre_reserves_pour_limitation,
                                                             'nombre_reserves_pour_incertitudes' : mandat.nombre_reserves_pour_incertitudes,
                                                             'nombre_reserves_pour_desacord' : mandat.nombre_reserves_pour_desacord,
                                                             'nombre_observation' : mandat.nombre_observation,
                                                             'associe_signataire' : mandat.associeSignataire,
                                                             
                                                             'budget_temps_selon_norme' : mandat.budget_temps_selon_norme,
                                                             'budget_retenu_effort' : mandat.budget_retenu_effort,
                                                             'budget_temps_realises' : mandat.budget_temps_realises,
                                                             'temps_passe_associe' : mandat.temps_passe_associe,
                                                             'autres_missions_realises' : mandat.autres_missions_realises,
                                                             'honoraires_autres_mission' : str(mandat.honoraires_autres_mission).replace('.', ','),
                                                             'rapport_opinion' : mandat.rapport_opinion,
                                                             'rapport_controle_interne' : mandat.rapport_controle_interne,
                                                             'rapport_detaille_comptes' : mandat.rapport_detaille_comptes,
                                                             'rapport_special' : mandat.rapport_special,
                                                             'autres_rapports' : mandat.autres_rapports,
                                                             'partner': partner,
                                                             'declaration': declaration,
                                                             'mandat': mandat,
                                                             'id': mandat.id,
                                                             'declaration_id': declaration.id,
                                                             'name': partner.name,
                                                             'prenom': partner.second_name,
                                                             'state':declaration.state,
                                                             'secteurs': SECTEURS_ACTIVITES,
                                                            'natures': NATURES_MISSION,
                                                            'formes': FORMES_JURIDIQUE,
                                                            'modes': MODES_DESIGNATIN})
            return request.render("mandat_cotisation_management.new_mandat", values)
         
        if not mandat and post and request.httprequest.method == 'POST':
            mandat = request.env['oec.mandat'].sudo().create({
                                                             'secteur_activite': post.get('secteur_activite'),
                                                             'forme_juridique' : post.get('forme_juridique'),
                                                             'entite_ape' : post.get('entite_ape'),
                                                             'in_group' : post.get('in_group'),
                                                             'nombre_autres_entite_groupe': post.get('nombre_autres_entite_groupe'),
                                                             'capitaux_propres' : post.get('capitaux_propres').replace(' ', '').replace(',', '.'),
                                                             'resultat_exercice': post.get('resultat_exercice').replace(' ', '').replace(',', '.'),
                                                             'total_actif' : post.get('total_actif').replace(' ', '').replace(',', '.'),
                                                             'produit_exploitation' : post.get('produit_exploitation').replace(' ', '').replace(',', '.'),
                                                             'produit_financie' : post.get('produit_financie').replace(' ', '').replace(',', '.'),
                                                             'leasing_restant' : post.get('leasing_restant').replace(' ', '').replace(',', '.'),
                                                             'honoraires_dernier_exercice_clos' : post.get('honoraires_dernier_exercice_clos').replace(' ', '').replace(',', '.'),
                                                             'nature_mission' : post.get('nature_mission'),
                                                             'date_designation' : post.get('date_designation') if post.get('date_designation') else None,
                                                             'mode_designation' : post.get('mode_designation'),
                                                             'exercces_couverts_par_le_mandat' : post.get('exercces_couverts_par_le_mandat'),
                                                             'coCac' : int(post.get('co_cac')) if post.get('co_cac') else False,
                                                             'dernier_exercice_control' : post.get('dernier_exercice_control'),
                                                             'nombre_reserves_pour_limitation' : post.get('nombre_reserves_pour_limitation'),
                                                             'nombre_reserves_pour_incertitudes' : post.get('nombre_reserves_pour_incertitudes'),
                                                             'nombre_reserves_pour_desacord' : post.get('nombre_reserves_pour_desacord'),
                                                             'nombre_observation' : post.get('nombre_observation'),
                                                             'associeSignataire' : int(post.get('associe_signataire')) if post.get('associe_signataire') else False,                              
                                                             'budget_temps_selon_norme' : post.get('budget_temps_selon_norme'),
                                                             'budget_retenu_effort' : post.get('budget_retenu_effort'),
                                                             'budget_temps_realises' : post.get('budget_temps_realises'),
                                                             'temps_passe_associe' : post.get('temps_passe_associe'),
                                                             'autres_missions_realises' : post.get('autres_missions_realises'),
                                                             'honoraires_autres_mission' : post.get('honoraires_autres_mission').replace(' ', '').replace(',', '.'),
                                                             'rapport_opinion' : post.get('rapport_opinion'),
                                                             'rapport_controle_interne' : post.get('rapport_controle_interne'),
                                                             'rapport_detaille_comptes' : post.get('rapport_detaille_comptes'),
                                                             'rapport_special' : post.get('rapport_special'),
                                                             'autres_rapports' : post.get('autres_rapports'),
                                                             'partner_id': partner.id,
                                                             'mandat_declaration_id': declaration})
            
            declaration = request.env['oec.mandat.declaration'].sudo().search([('id', '=', declaration)])
            return werkzeug.utils.redirect("/declaration/%s" % slug(declaration))
        
        if mandat and post and request.httprequest.method == 'POST':
            print("got this co_cac :", post.get('co_cac'), "from post")
            _logger.error(f"mandat={mandat} ; id={post.get('id')} ; id_type={type(post.get('id'))} ; exercices={post.get('exercces_couverts_par_le_mandat')}")
            mandat = request.env['oec.mandat'].sudo().search([('id', '=', post.get('id'))])
            _logger.info("Mandat found successfully. Updating it ...")
            mandat.sudo().write({
                                                             'secteur_activite': post.get('secteur_activite'),
                                                             'forme_juridique' : post.get('forme_juridique'),
                                                             'entite_ape' : post.get('entite_ape'),
                                                             'in_group' : post.get('in_group'),
                                                             'nombre_autres_entite_groupe': post.get('nombre_autres_entite_groupe'),
                                                             'capitaux_propres' : post.get('capitaux_propres').replace(' ', '').replace(',', '.'),
                                                             'resultat_exercice': post.get('resultat_exercice').replace(' ', '').replace(',', '.'),
                                                             'total_actif' : post.get('total_actif').replace(' ', '').replace(',', '.'),
                                                             'produit_exploitation' : post.get('produit_exploitation').replace(' ', '').replace(',', '.'),
                                                             'produit_financie' : post.get('produit_financie').replace(' ', '').replace(',', '.'),
                                                             'leasing_restant' : post.get('leasing_restant').replace(' ', '').replace(',', '.'),
                                                             'honoraires_dernier_exercice_clos' : post.get('honoraires_dernier_exercice_clos').replace(' ', '').replace(',', '.'),
                                                             'nature_mission' : post.get('nature_mission'),
                                                             'date_designation' : post.get('date_designation') if post.get('date_designation') else None,
                                                             'mode_designation' : post.get('mode_designation'),
                                                             'exercces_couverts_par_le_mandat' : post.get('exercces_couverts_par_le_mandat'),
                                                             'coCac' : int(post.get('co_cac')) if post.get('co_cac') else False,
                                                             'dernier_exercice_control' : post.get('dernier_exercice_control'),
                                                             'nombre_reserves_pour_limitation' : post.get('nombre_reserves_pour_limitation'),
                                                             'nombre_reserves_pour_incertitudes' : post.get('nombre_reserves_pour_incertitudes'),
                                                             'nombre_reserves_pour_desacord' : post.get('nombre_reserves_pour_desacord'),
                                                             'nombre_observation' : post.get('nombre_observation'),
                                                             'associeSignataire' : int(post.get('associe_signataire')) if post.get('associe_signataire') else False,                              
                                                             'budget_temps_selon_norme' : post.get('budget_temps_selon_norme'),
                                                             'budget_retenu_effort' : post.get('budget_retenu_effort'),
                                                             'budget_temps_realises' : post.get('budget_temps_realises'),
                                                             'temps_passe_associe' : post.get('temps_passe_associe'),
                                                             'autres_missions_realises' : post.get('autres_missions_realises'),
                                                             'honoraires_autres_mission' : post.get('honoraires_autres_mission').replace(' ', '').replace(',', '.'),
                                                             'rapport_opinion' : post.get('rapport_opinion'),
                                                             'rapport_controle_interne' : post.get('rapport_controle_interne'),
                                                             'rapport_detaille_comptes' : post.get('rapport_detaille_comptes'),
                                                             'rapport_special' : post.get('rapport_special'),
                                                             'autres_rapports' : post.get('autres_rapports')})
            
            #print (post.get('declaration_id'))
            declaration = request.env['oec.mandat.declaration'].sudo().search([('id', '=', post.get('declaration_id'))])
            return werkzeug.utils.redirect("/declaration/%s" % slug(declaration))
            
        values.update({'state' : 'draft',
                   'name': partner.name,
                   'prenom': partner.second_name, 
                   'partner':partner,
                   'declaration': declaration.id,
                   'state':declaration.state,
                   'secteurs': SECTEURS_ACTIVITES,
                   'natures': NATURES_MISSION,
                   'formes': FORMES_JURIDIQUE,
                   'modes': MODES_DESIGNATIN})
        return request.render("mandat_cotisation_management.new_mandat", values)
    
    
    @route(['/mandats'], type='http', auth='user', website=True)
    def mandats_list(self, redirect=None, **post):
        values = {}
        partner = request.env.user.partner_id
        formations = request.env['oec.mandat'].sudo().search([('partner_id', '=', partner.id)])
        values.update({'mandats': formations})
        return request.render("mandat_cotisation_management.portal_mandats", values)
    
    @route(['/mandat/<string:id>/submit'], type='http', auth='public', website=True)
    def mandat_submit(self, redirect=None, id=None, **post):
        mandat = request.env['oec.mandat'].sudo().browse(int(id))
        mandat.button_in_progress()
        return request.render("mandat_cotisation_management.portal_mandat_submit_success")
    
    
