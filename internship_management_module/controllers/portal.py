# -*- coding: utf-8 -*-

import base64
import functools
import json
import logging
import math
import re
from collections import defaultdict

from werkzeug import urls
from markupsafe import Markup
#from odoo.addons.http_routing.models.ir_http import slug

from odoo import fields as odoo_fields, http, tools, _, SUPERUSER_ID
from odoo.exceptions import ValidationError, AccessError, MissingError, UserError, AccessDenied
from odoo.http import content_disposition, Controller, request, route
from odoo.tools import consteq
from odoo import http

from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
import werkzeug.exceptions
import werkzeug.urls
import werkzeug.wrappers
import logging
import traceback
from werkzeug.exceptions import NotFound


_logger = logging.getLogger(__name__)





REGISTRATION_MODE_MAP_F2B = {
    'a': ('pp2', 'pm', 'moraleyes_physiqueno'),
    'b': ('pp3', 'pp', 'physique_salarie'),
    'c': ('pm', 'pm', 'moraleyes_physiqueyes'),
    'd': ('pp4', 'pp', 'physique_associe'),
    'e': ('pp1', 'pp', 'physique_individuel'),   
}

REGISTRATION_MODE_MAP_B2F = {
    'pm': 'c',
    'pp1': 'e',
    'pp2': 'a',
    'pp3': 'b',
    'pp4': 'd',
}

class CustomerPortalCustom(CustomerPortal):
    
    MANDATORY_BILLING_FIELDS = ["name", "phone", "email", "street", "city", "country_id","second_name","place_of_birth","birthday"]
    OPTIONAL_BILLING_FIELDS = ["zipcode", "state_id", "vat", "company_name","iscae_certificate","work_certificate","anthropometric_profile","internship_supervisor_id","internship_controler_id" ,'start_date','contract_date','depot_date',"inscription_manuscrite", "attestation_cnss", "attestation_prise_en_charge_maitre", "attestation_prise_en_charge_commissaire_compte", "pv", "cin", "photo"]
    DOCUMENT_FIELDS = ['lettre_demande_inscription', 'declaration_sur_honneur', 'actes_modificatifs', 'copie_bo_jal', 'actes_cession', 'statuts', 'copie_conforme_contrat', 'modele_7', 'attestation_radiation', 'attestation_assurance', 'attestation_inscription', 'bulletin_notification', 'copie_cheque', 'contrat_travail', 'copie_cin', 'engagement', 'attestation_inscription_membre', 'extrait_casier_judiciaire', 'extrait_acte_naissance', 'photographies_recentes', 'photocopie_diplome', 'attestation_equivalence', 'fiches_annuelles', 'attestation_fin_stage', 'fiche_generale_synthese', 'fiche_annuelle', 'copie_convention', 'certificat_residence', 'demande_inscription_societe', 'demande_inscription_salarie', 'avenant_contrat_travail', 'copie_contrat_bail', 'declaration_sur_honneur_societe', 'lettre_demande_inscription_societe']
    REGISTRATION_FIELDS = ['hours', 'mode_registration', 'name', 'second_name', 'sexe', 'cin_number', 'phone', 'fax', 'gsm', 'email', 'diplome', 'already_registred', 'raison_sociale', 'forme_juridique', 'siege_social', 'capital_social', 'effectif', 'identifiant_fiscal', 'taxe_professionnelle', 'conseil_regional'] + DOCUMENT_FIELDS
    REPARTITION_CAPITAL_SOCIAL_FIELDS = ['name', 'percentage']
    DOCUMENT_REQUIREMENTS = {
        # Documents communs à tous les modes
        'common': [
            'copie_cin',
            'declaration_sur_honneur',
            'photocopie_diplome'
        ],

        # Documents spécifiques par mode
        'pp1': [
            'extrait_casier_judiciaire',
            'photographies_recentes',
            'extrait_acte_naissance',
            'demande_inscription_salarie',
            'questionnaire'
        ],

        'pp2': [
            'copie_cnie',
            'extrait_casier_judiciaire',
            'photographies_recentes',
            'extrait_acte_naissance',
            'engagement_prise_en_charge',
            'attestation_inscription',
            'bulletin_notification',
            'attestation_assurance',
            'actes_modificatifs',
            'copie_bo_jal',
            'modele_7',
            'questionnaire'
        ],

        'pp3': [
            'extrait_casier_judiciaire',
            'photographies_recentes',
            'extrait_acte_naissance',
            'demande_inscription_salarie',
            'engagement',
            'lettre_demande_inscription',
            'attestation_inscription',
            'bulletin_notification',
            'attestation_assurance',
            'avenant_contrat_travail',
            'modele_7',
            'questionnaire'
        ],

        'pp4': [
            'extrait_casier_judiciaire',
            'photographies_recentes',
            'extrait_acte_naissance',
            'engagement',
            'attestation_inscription',
            'bulletin_notification',
            'attestation_assurance',
            'modele_7',
            'questionnaire'
        ],

        'pm': [
            'attestation_inscription',
            'bulletin_notification',
            'attestation_assurance',
            'actes_modificatifs',
            'copie_bo_jal',
            'modele_7',
            'contrat_travail',
            'copie_conforme_contrat',
            'attestation_inscription_membre',
            'lettre_demande_inscription',
            'statuts_mis_a_jour',
            'questionnaire'
        ]
    }
    
    
    
    @route(['/declarations'], type='http', auth='public', website=True)
    def request_cotisation(self, redirect=None, **post):
        return request.render("internship_management_module.portal_declaration")

    @http.route(['/demande-inscription'], type='http', auth='public', website=True)
    def request_registration(self, **post):
        _logger.error('0')
        partners = request.env['res.partner'].sudo().search([
            ('mode_registration', '!=', 'pm'),
            ('status_register', '=', 'registred')
        ])

        _logger.error('1')
        _logger.error('2 %s', post)
        companies = request.env['res.partner'].sudo().search([('is_company', '=', True)])
        
        vals = {
            'register_types': [
                ["pp", "Personne physique"],
                ["pm", "Personne morale"]
            ],
            'companies': companies,
            'partners': partners,
            'error': {},
            'error_message': None
        }

        
        if post and request.httprequest.method == 'POST':
            error_messages = []

            _logger.warning('2')
            required_fields = {
                'mode_registration': "Mode d'inscription est requis",
                'type_selection': "Type d'inscription est requis",
                'name': "Nom est requis",
                'prenom': "Prénom est requis",
                'email': "Email est requis",
                'copie_cin': "Copie CIN est requise",
                'diplome_document': "Diplôme est requis"
            }

            for field, message in required_fields.items():
                if not post.get(field):
                    error_messages.append(message)

            if not post.get('declaration_honneur'):
                error_messages.append("Vous devez accepter la déclaration sur l'honneur")


            if post.get('type_selection') in ['b', 'd'] and not post.get('cabinet_rattache'):
                error_messages.append("Cabinet rattaché est requis pour ce type d'inscription")
            _logger.warning('%s', error_messages)
            if error_messages:
                vals['error_message'] = error_messages
                return request.render("internship_management_module.portal_request_registration", vals)
            _logger.warning('3')
            try:

                partner_vals = {
                    'name': post.get('name'),
                    'second_name': post.get('prenom'),
                    'email': post.get('email'),
                    'contact_registration_mode': post.get('mode_registration', False),
                    'contact_registration_type': REGISTRATION_MODE_MAP_F2B.get(
                        post.get('type_selection', False), False)[2],
                    'mode_registration': REGISTRATION_MODE_MAP_F2B.get(
                        post.get('type_selection', False), False)[0],
                    'status_register': 'draft',
                    'parent_id': int(post.get('cabinet_rattache')) if post.get('cabinet_rattache') and post.get('cabinet_rattache').isdigit() else False,
                    'contact_type_id': 4,
                    'is_company': post.get('mode_registration', False) == 'pm',
                }

                _logger.error('3')
                if 'copie_cin' in request.httprequest.files:
                    cin_file = request.httprequest.files['copie_cin']
                    partner_vals['copie_cin'] = base64.b64encode(cin_file.read())
                    partner_vals['copie_cin_filename'] = cin_file.filename

                if 'diplome_document' in request.httprequest.files:
                    diplome_file = request.httprequest.files['diplome_document']
                    partner_vals['diplome_document'] = base64.b64encode(diplome_file.read())
                    partner_vals['diplome_document_filename'] = diplome_file.filename


                if post.get('mode_registration') == 'pm':
                    partner_vals.update({
                        'denomination': post.get('denomination'),
                        'rc': post.get('rc'),
                        'ice': post.get('ice'),
                        'siege_social': post.get('siege_social')
                    })

                    if 'statuts' in request.httprequest.files:
                        statuts_file = request.httprequest.files['statuts']
                        partner_vals['statuts'] = base64.b64encode(statuts_file.read())
                        partner_vals['statuts_filename'] = statuts_file.filename

                _logger.error('4')
                try:
                    _logger.error('sss %s',partner_vals)
                    partner = request.env['res.partner'].sudo().create(partner_vals)
                except Exception as e:
                    vals['error_message'] = ["Une erreur est survenue lors de la création: %s" % str(e)]
                _logger.error('5 %s',partner)
                #partner._send_registration_notification()
                _logger.error('6')
                return request.render("internship_management_module.portal_confirm_request_registration")
                #return request.redirect('/demande-inscription/confirmation/%s' % partner.id)
                #return request.redirect('/demande-inscription/confirmation')

            except Exception as e:
                _logger.error('7')
                vals['error_message'] = ["Une erreur est survenue lors de la création: %s" % str(e)]
                _logger.error('sss %s',vals['error_message'])
                return request.render("internship_management_module.portal_request_registration", vals)

        return request.render("internship_management_module.portal_request_registration", vals)

    @route(['/demande-inscription/confirmation/<int:partner_id>'], type='http', auth='public', website=True)
    def registration_confirmation(self, partner_id, **post):
        registration_data = request.session.get('registration_data', {})
        _logger.error('ART')
        if not partner_id:
            return request.redirect('/demande-inscription')

        if post.get('confirm'):
            return request.redirect('/registration')


        values = {
            'name': registration_data.get('name', ''),
            'prenom': registration_data.get('prenom', ''),
            'email': registration_data.get('email', ''),
            'mode': self._get_mode_label(registration_data.get('mode_registration')),
            'type_selection': registration_data.get('type_selection', ''),
            'has_copie_cin': registration_data.get('has_copie_cin', False),
            'has_diplome': registration_data.get('has_diplome', False),
            'show_pp_rattache': registration_data.get('mode_registration') == 'pm',
            'pp_rattache': self._get_partner_name(registration_data.get('pp_rattache')),
        }
        values = {}
        return request.render("internship_management_module.portal_inscription_submit", values)

    def _get_mode_label(self, mode):
        modes = {
            "pm": "Personne morale",
            "pp1": "Personne physique à titre individuel",
            "pp2": "Personne physique exerçant en société",
            "pp3": "Personne physique en tant que salarié",
            "pp4": "Personne physique exerçant en tant qu'associé"
        }
        return modes.get(mode, "")

    def _get_partner_name(self, partner_id):
        if not partner_id:
            return ""
        partner = request.env['res.partner'].sudo().browse(int(partner_id))
        return partner.name if partner.exists() else ""

    @route(['/download/document'], type='http', auth='public')
    def download_document(self, doc_type=None, **kwargs):
        registration_data = request.session.get('registration_data', {})

        if doc_type == 'cin':
            content = registration_data.get('copie_cin_content')
            filename = registration_data.get('copie_cin_filename', 'cin.pdf')
        elif doc_type == 'diplome':
            content = registration_data.get('diplome_content')
            filename = registration_data.get('diplome_filename', 'diplome.pdf')
        else:
            raise NotFound()

        if not content:
            raise NotFound()

        return request.make_response(
            base64.b64decode(content),
            headers=[
                ('Content-Type', 'application/pdf'),
                ('Content-Disposition', f'attachment; filename="{filename}"')
            ]
        )

    @route(['/registration'], type='http', auth='user', website=True)
    def registration(self, redirect=None, **post):
        values = {}
        partner = request.env.user.partner_id
        current_mode = partner.mode_registration or post.get('mode_registration')

        if post and request.httprequest.method == 'POST':
            error_messages = []
            partner_vals = {}
            files = request.httprequest.files

            try:
                # 1. Traitement des champs de base
                for field in self.REGISTRATION_FIELDS:
                    if field in post:
                        partner_vals[field] = post[field]

                # 2. Déterminer les documents requis pour ce mode
                required_docs = self.DOCUMENT_REQUIREMENTS.get('common', []) + \
                                self.DOCUMENT_REQUIREMENTS.get(current_mode, [])

                # 3. Validation des documents requis
                for doc_field in required_docs:
                    # Vérifie si le fichier est fourni ou déjà existant
                    file = files.get(doc_field)
                    if (not file or not file.filename) and not getattr(partner, doc_field, False):
                        field_label = doc_field.replace('_', ' ').capitalize()
                        error_messages.append(f"Le document {field_label} est obligatoire")

                # 4. Validation des champs obligatoires communs
                common_required = ['name', 'second_name', 'email', 'phone', 'cin_number']
                for field in common_required:
                    if not post.get(field):
                        error_messages.append(f"Le champ {field.replace('_', ' ')} est obligatoire")

                # 5. Validation spécifique pour les personnes morales
                if current_mode == 'pm':
                    # Validation de la répartition du capital
                    total_percent = 0
                    repartition_lines = []

                    for i in range(1, 6):
                        name = post.get(f'name{i}')
                        percent = float(post.get(f'percentage{i}', 0))

                        if name:  # Ligne remplie
                            repartition_lines.append((0, 0, {
                                'name': name,
                                'percentage': percent,
                                'status': post.get(f'status{i}')
                            }))
                            total_percent += percent

                    if abs(total_percent - 100) > 0.01 and repartition_lines:
                        error_messages.append("La somme des pourcentages doit faire exactement 100%")

                    partner_vals['repartition_ids'] = [(5, 0, 0)] + repartition_lines

                if error_messages:
                    values['error_message'] = error_messages
                    raise ValidationError("\n".join(error_messages))

                # 6. Traitement des fichiers
                for doc_field in self.DOCUMENT_FIELDS:
                    if doc_field in files:
                        file = files[doc_field]
                        if file and file.filename:
                            partner_vals[doc_field] = base64.b64encode(file.read())
                            partner_vals[f'{doc_field}_filename'] = file.filename

                # 7. Gestion de la photo de profil
                if 'photographies_recentes' in files:
                    file = files['photographies_recentes']
                    if file and file.filename:
                        partner_vals['image_1920'] = base64.b64encode(file.read())

                # 8. Traitement des fichiers supplémentaires
                if 'autres_fichiers' in files:
                    for fichier in files.getlist('autres_fichiers'):
                        if fichier and fichier.filename:
                            try:
                                request.env['res.partner.file'].sudo().create({
                                    'name': fichier.filename,
                                    'datas': base64.b64encode(fichier.read()),
                                    'partner_id': partner.id
                                })
                            except Exception as e:
                                _logger.warning("Failed to process additional file: %s", str(e))

                # 9. Mise à jour du partenaire
                partner.write(partner_vals)

                # 10. Gestion de la soumission
                if 'submit' in post:
                    # Vérification supplémentaire avant soumission
                    missing_docs = [
                        doc for doc in required_docs
                        if not getattr(partner, doc, False)
                    ]

                    if missing_docs:
                        error_messages = [f"Documents manquants pour soumission: {', '.join(missing_docs)}"]
                        values['error_message'] = error_messages
                        raise ValidationError("\n".join(error_messages))

                    # Validation de la checkbox
                    if not post.get('declaration_honneur'):
                        error_messages.append("Vous devez accepter la déclaration sur l'honneur")
                        values['error_message'] = error_messages
                        raise ValidationError("\n".join(error_messages))

                    partner.button_in_progress()
                    return request.redirect('/registration?submitted=1')

                return request.redirect('/registration?saved=1')

            except ValidationError as e:
                values['error_message'] = str(e).split('\n')
            except Exception as e:
                values['error_message'] = ["Une erreur technique est survenue"]
                _logger.error("Registration error: %s", str(e), exc_info=True)

        # Préparation des valeurs pour le template
        values.update({
            'partner': partner,
            'register_types': partner._fields['contact_registration_mode'].selection,
            'type_selection': partner._fields['contact_registration_type'].selection,
            'error': values.get('error', {})
        })

        return request.render("internship_management_module.portal_registration", values)

        
    @route(['/registration/submit'], type='http', auth='public', website=True)
    def submit_registration(self, redirect=None, **post):
        partner = request.env.user.partner_id
        if request.httprequest.method == 'POST':
            if redirect:
                return request.redirect(redirect)
            partner.sudo().button_in_progress()
            return request.redirect('/registration')
        response = request.render("internship_management_module.portal_registration_submit")
        #response.headers['X-Frame-Options'] = 'DENY'
        return response

    @http.route('/update_status', type='http', auth='user', methods=['POST'], csrf=True)
    def update_status(self, **post):
        partner_id = int(post.get('partner_id'))
        action = post.get('action')  # accept ou reject

        partner = request.env['res.partner'].sudo().browse(partner_id)

        if partner.status_register == 'in_progress':
            if action == 'accept':
                partner.status_register = 'registred'
            elif action == 'reject':
                partner.status_register = 'rejected'

        return request.redirect('/registration')
    
    @route(['/my/account'], type='http', auth='user', website=True)
    def account(self, redirect=None, **post):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        values.update({
            'error': {},
            'error_message': [],
        })

        if post and request.httprequest.method == 'POST':
            error, error_message = self.details_form_validate(post)
            values.update({'error': error, 'error_message': error_message})
            
            ''' Documents '''
            iscae_certificate_filename = work_certificate_filename = anthropometric_profile_filename = inscription_manuscrite_filename = attestation_cnss_filename = attestation_prise_en_charge_maitre_filename = attestation_prise_en_charge_commissaire_compte_filename = pv_filename = cin_filename = photo_filename = None
            if post.get('iscae_certificate'):
                iscae_certificate_file = post.get('iscae_certificate')
                iscae_certificate_filename = post.get('iscae_certificate').filename
                iscae_certificate_file = iscae_certificate_file.read()
                post.update({'iscae_certificate': Markup(base64.b64encode(iscae_certificate_file).decode('utf-8'))})
            else:
                del post['iscae_certificate']
                
            if post.get('work_certificate'):
                work_certificate_file = post.get('work_certificate')
                work_certificate_filename = post.get('work_certificate').filename
                work_certificate_file = work_certificate_file.read()
                post.update({'work_certificate': Markup(base64.b64encode(work_certificate_file).decode('utf-8'))})
            else:
                post.pop("work_certificate", None)
                
            if post.get('anthropometric_profile'):
                anthropometric_profile_file = post.get('anthropometric_profile')
                anthropometric_profile_filename = post.get('anthropometric_profile').filename
                anthropometric_profile_file = anthropometric_profile_file.read()
                post.update(
                    {'anthropometric_profile': Markup(base64.b64encode(anthropometric_profile_file).decode('utf-8'))})
            else:
                del post['anthropometric_profile']
                
            if post.get('inscription_manuscrite'):
                inscription_manuscrite_file = post.get('inscription_manuscrite')
                inscription_manuscrite_filename = post.get('inscription_manuscrite').filename
                inscription_manuscrite_file = inscription_manuscrite_file.read()
                post.update(
                    {'inscription_manuscrite': Markup(base64.b64encode(inscription_manuscrite_file).decode('utf-8'))})
            else:
                del post['inscription_manuscrite']
                
            if post.get('attestation_cnss'):
                attestation_cnss_file = post.get('attestation_cnss')
                attestation_cnss_filename = post.get('attestation_cnss').filename
                attestation_cnss_file = attestation_cnss_file.read()
                post.update({'attestation_cnss': Markup(base64.b64encode(attestation_cnss_file).decode('utf-8'))})
            else:
                del post['attestation_cnss']
            
            if post.get('attestation_prise_en_charge_maitre'):
                attestation_prise_en_charge_maitre_file = post.get('attestation_prise_en_charge_maitre')
                attestation_prise_en_charge_maitre_filename = post.get('attestation_prise_en_charge_maitre').filename
                attestation_prise_en_charge_maitre_file = attestation_prise_en_charge_maitre_file.read()
                post.update({'attestation_prise_en_charge_maitre': Markup(
                    base64.b64encode(attestation_prise_en_charge_maitre_file).decode('utf-8'))})
            else:
                del post['attestation_prise_en_charge_maitre']
                
            if post.get('attestation_prise_en_charge_commissaire_compte'):
                attestation_prise_en_charge_commissaire_compte_file = post.get('attestation_prise_en_charge_commissaire_compte')
                attestation_prise_en_charge_commissaire_compte_filename = post.get('attestation_prise_en_charge_commissaire_compte').filename
                attestation_prise_en_charge_commissaire_compte_file = attestation_prise_en_charge_commissaire_compte_file.read()
                post.update({'attestation_prise_en_charge_commissaire_compte': Markup(
                    base64.b64encode(attestation_prise_en_charge_commissaire_compte_file).decode('utf-8'))})
            else:
                del post['attestation_prise_en_charge_commissaire_compte']

            if post.get('pv'):
                pv_file = post.get('pv')
                pv_filename = post.get('pv').filename
                pv_file = pv_file.read()
                post.update({'pv': Markup(base64.b64encode(pv_file).decode('utf-8'))})
            else:
                del post['pv']
                
            if post.get('cin'):
                cin_file = post.get('cin')
                cin_filename = post.get('cin').filename
                cin_file = cin_file.read()
                post.update({'cin': Markup(base64.b64encode(cin_file).decode('utf-8'))})
            else:
                del post['cin']
                
            if post.get('photo'):
                photo_file = post.get('photo')
                photo_filename = post.get('photo').filename
                photo_file = photo_file.read()
                post.update({'photo': Markup(base64.b64encode(photo_file).decode('utf-8'))})
            else:
                del post['photo']

            values.update(post)
            if not error:
                values = {key: post[key] for key in self.MANDATORY_BILLING_FIELDS}
                values.update({key: post[key] for key in self.OPTIONAL_BILLING_FIELDS if key in post})
                for field in set(['country_id', 'state_id','internship_controler_id','internship_supervisor_id']) & set(values.keys()):
                    try:
                        values[field] = int(values[field])
                    except:
                        values[field] = False
                values.update({'zip': values.pop('zipcode', ''), 'iscae_certificate_filename' : iscae_certificate_filename, \
                               'work_certificate_filename' : work_certificate_filename, \
                               'anthropometric_profile_filename' : anthropometric_profile_filename, \
                               'inscription_manuscrite_filename': inscription_manuscrite_filename, \
                               'attestation_cnss_filename': attestation_cnss_filename, \
                               'attestation_prise_en_charge_maitre_filename': attestation_prise_en_charge_maitre_filename, \
                               'attestation_prise_en_charge_commissaire_compte_filename': attestation_prise_en_charge_commissaire_compte_filename, \
                               'pv_filename': pv_filename,
                               'cin_filename': cin_filename,
                               'photo_filename': photo_filename,
                               'saved_flag': True
                               })
                if post.get('internship_supervisor_id'):
                    values.update({
                        'cregionalp_id': request.env['res.partner'].sudo().search(
                            [('id', '=', post.get('internship_supervisor_id'))]).mapped('cregionalcourant_id').id if
                        request.env['res.partner'].sudo().search(
                            [('id', '=', post.get('internship_supervisor_id'))]) else False,
                        'cregionalcourant_id': request.env['res.partner'].sudo().search(
                            [('id', '=', post.get('internship_supervisor_id'))]).mapped('cregionalcourant_id').id if
                        request.env['res.partner'].sudo().search(
                            [('id', '=', post.get('internship_supervisor_id'))]) else False
                    })
                partner.sudo().write(values)
                if redirect:
                    return request.redirect(redirect)
                return request.redirect('/my/account')

        countries = request.env['res.country'].sudo().search([])
        states = request.env['res.country.state'].sudo().search([])
        supervisors = request.env['res.partner'].sudo().search([('contact_type_id.code', '=', 'EC')])
        controlors = request.env['res.partner'].sudo().search([('contact_type_id.code', '=', 'CS')])

        values.update({
            'partner': partner,
            'countries': countries,
            'states': states,
            'supervisors':supervisors,
            'controlors':controlors,
            'has_check_vat': hasattr(request.env['res.partner'], 'check_vat'),
            'redirect': redirect,
            'page_name': 'my_details',
        })
        
        response = request.render("portal.portal_my_details", values)
        #response.headers['X-Frame-Options'] = 'DENY'
        return response

    @route(['/my/account/cvtheque'], type='http', auth='user', website=True)
    def account_cvtheque(self, redirect=None, **post):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        formation_list = []
        experience_list = []
        values.update({
            'error': {},
            'error_message': [],
        })
        formation = request.env['x_cvstagaire']
        if post and request.httprequest.method == 'POST':
            if post.get('description1'):
                vals = {
                    'x_studio_du_au_1':post.get('date_start1'),
                    'x_studio_option':post.get('date_end1'),
                    'x_studio_description_2':post.get('description1')
                }
                formation_list.append((0,0,vals))
            if post.get('description2'):
                vals = {
                    'x_studio_du_au_1':post.get('date_start2'),
                    'x_studio_option':post.get('date_end2'),
                    'x_studio_description_2':post.get('description2')
                }
                formation_list.append((0,0,vals))
            if post.get('description3'):
                vals = {
                    'x_studio_du_au_1':post.get('date_start3'),
                    'x_studio_option':post.get('date_end3'),
                    'x_studio_description_2':post.get('description3')
                }
                formation_list.append((0,0,vals))
            if post.get('description4'):
                vals = {
                    'x_studio_du_au_1':post.get('date_start4'),
                    'x_studio_option':post.get('date_end4'),
                    'x_studio_description_2':post.get('description4')
                }
                formation_list.append((0,0,vals))
            if post.get('description5'):
                vals = {
                    'x_studio_du_au_1':post.get('date_start5'),
                    'x_studio_option':post.get('date_end5'),
                    'x_studio_description_2':post.get('description5')
                }
                formation_list.append((0,0,vals))
            partner.x_studio_formation_3 = formation_list
            if post.get('ex_date_start1'):
                vals = {
                    'x_studio_du_anne_1':post.get('ex_date_start1'),
                    'x_studio_au_anne':post.get('ex_date_end1'),
                    'x_studio_description_2':post.get('ex_description1'),
                    'x_studio_poste':post.get('ex_poste1')
                }
                experience_list.append((0,0,vals))
            if post.get('ex_date_start2'):
                vals = {
                    'x_studio_du_anne_1':post.get('ex_date_start2'),
                    'x_studio_au_anne':post.get('ex_date_end2'),
                    'x_studio_description_2':post.get('ex_description2'),
                    'x_studio_poste':post.get('ex_poste2')
                }
                experience_list.append((0,0,vals))
            if post.get('ex_date_start3'):
                vals = {
                    'x_studio_du_anne_1':post.get('ex_date_start3'),
                    'x_studio_au_anne':post.get('ex_date_end3'),
                    'x_studio_description_2':post.get('ex_description3'),
                    'x_studio_poste':post.get('ex_poste3')
                }
                experience_list.append((0,0,vals))
            if post.get('ex_date_start4'):
                vals = {
                    'x_studio_du_anne_1':post.get('ex_date_start4'),
                    'x_studio_au_anne':post.get('ex_date_end4'),
                    'x_studio_description_2':post.get('ex_description4'),
                    'x_studio_poste':post.get('ex_poste4')
                }
                experience_list.append((0,0,vals))
            if post.get('ex_date_start5'):
                vals = {
                    'x_studio_du_anne_1':post.get('ex_date_start5'),
                    'x_studio_au_anne':post.get('ex_date_end5'),
                    'x_studio_description_2':post.get('ex_description5'),
                    'x_studio_poste':post.get('ex_poste5')
                }
                experience_list.append((0,0,vals))
            partner.x_studio_experience_1 = experience_list
            print('partner',partner)
            if redirect:
                return request.redirect(redirect)
            return request.redirect('/report/success')

        values.update({
            'partner': partner,
            'redirect': redirect,
            'page_name': 'cvtheque',
        })
        
        response = request.render("internship_management_module.portal_my_cv", values)
        #response.headers['X-Frame-Options'] = 'DENY'
        return response


    @route(['/my/account/submit'], type='http', auth='user', website=True)
    def submit(self, redirect=None, **post):
        partner = request.env.user.partner_id
        partner.sudo().button_submit()
        if request.httprequest.method == 'POST':
            if redirect:
                return request.redirect(redirect)
            return request.redirect('/my/account')
        response = request.render("internship_management_module.portal_submit")
        #response.headers['X-Frame-Options'] = 'DENY'
        return response

    @route(['/my/report',
            '/my/report/<model("documents.document"):report>'], type='http', auth='public', website=True)
    def report(self, report=None,redirect=None, **post):
        slug = request.env['ir.http']._slug
        values = {}
        list_vals = []
        filename = None
        partner = request.env.user.partner_id
        related_record = post.get('id') if post.get('id') else report.id
        related_document = request.env['documents.document'].browse(int(related_record))
        line_1 = related_document.sudo().mapped('realised_works_ids').filtered(lambda r:r.name == "Audit Comptable et financier")
        line_2 = related_document.sudo().mapped('realised_works_ids').filtered(lambda r:r.name == "Evaluation du dispositif de contrôle interne")
        line_3 = related_document.sudo().mapped('realised_works_ids').filtered(lambda r:r.name == "Expertise comptable et revision des comptes")
        line_4 = related_document.sudo().mapped('realised_works_ids').filtered(lambda r:r.name == "Assistance à l'élaboration des liasses fiscales")
        line_5 = related_document.sudo().mapped('realised_works_ids').filtered(lambda r:r.name == "Préparation des etats de synthèse (ETIC)")
        line_6 = related_document.sudo().mapped('realised_works_ids').filtered(lambda r:r.name == "Reporting IFRS")
        
        if request.httprequest.method == 'POST':
            if partner.id == related_document.internship_supervisor_id.id:
                values.update({'signature' : request.env['res.users'].sudo().search([('partner_id', '=', related_document.internship_supervisor_id.id)]).sign_signature,
                               'apprciation_ms': post.get('apprciation_ms'),
                               'validation_date': odoo_fields.Date.today()})
                related_document.sudo().write(values)
                share_vals = {
                'type': 'ids',
                'document_ids': [(4, related_document.id)],
                'folder_id': related_document.folder_id.id
                }
                share = request.env['documents.share'].sudo().create(share_vals)
                base_url = request.env["ir.config_parameter"].sudo().get_param("web.base.url")
                url = "%s/document/download/%s/%s/%s" % (base_url, share.id, share.access_token, related_document.id)
                signature_url = "%s/web/image?model=documents.document&id=%s&field=signature" % (base_url, related_document.id)
                values.update({
                               'report': related_document,
                               'url': url,
                               'partner': partner,
                               'signature_url': signature_url
                               })
                email = request.env.ref('base.user_admin').email
                email_to = related_document.internship_controler_id.email
                name = related_document.internship_controler_id.name
                second_name = related_document.internship_controler_id.second_name
                stagiaire_name = related_document.internship_id.name
                stagiaire_prenom = related_document.internship_id.second_name
                email_template_report_examined = request.env.ref('internship_management_module.email_template_report_examined')
                email_template_report_examined.sudo().with_context(email_from=email, email_to=email_to, name=name, second_name=second_name, stagiaire_name=stagiaire_name, stagiaire_prenom=stagiaire_prenom).send_mail(related_document.id,force_send=True)
                return werkzeug.utils.redirect("/my/report/%s" % slug(related_document))
                return request.redirect('/my/internships')
                return request.render("internship_management_module.portal_report_submit", values)
            
            if partner.id == related_document.internship_controler_id.id:
                #values.update({'signature' : request.env['res.users'].sudo().search([('partner_id', '=', related_document.internship_supervisor_id.id)]).sign_signature})
                values.update({'signature_cs' : request.env['res.users'].sudo().search([('partner_id', '=', related_document.internship_controler_id.id)]).sign_signature,
                                'report_content': post.get('report_content'),
                               'internship_progress':post.get('internship_progress'),
                               'respect_internship_condition':post.get('respect_internship_condition'),
                               'cs_decision':post.get('cs_decision'),
                               'apprciation_cs': post.get('apprciation_cs'),
                               'controle_date': odoo_fields.Date.today()})
                related_document.sudo().write(values)
                share_vals = {
                'type': 'ids',
                'document_ids': [(4, related_document.id)],
                'folder_id': related_document.folder_id.id
                }
                share = request.env['documents.share'].sudo().create(share_vals)
                base_url = request.env["ir.config_parameter"].sudo().get_param("web.base.url")
                url = "%s/document/download/%s/%s/%s" % (base_url, share.id, share.access_token, related_document.id)
                signature_url = "%s/web/image?model=documents.document&id=%s&field=signature" % (base_url, related_document.id)
                signature_cs_url = "%s/web/image?model=documents.document&id=%s&field=signature_cs" % (base_url, related_document.id)
                values.update({
                               'report': related_document,
                               'url': url,
                               'partner': partner,
                               'signature_url': signature_url,
                                'signature_cs_url':signature_cs_url
                               })
                email = request.env.ref('base.user_admin').email
                email_to = related_document.internship_id.email
                name = related_document.internship_id.name
                second_name = related_document.internship_id.second_name
                stagiaire_name = related_document.internship_id.name
                stagiaire_prenom = related_document.internship_id.second_name
                email_template_report_response = request.env.ref('internship_management_module.email_template_report_response')
                email_template_report_response.sudo().with_context(email_from=email, email_to=email_to, name=name, second_name=second_name, stagiaire_name=stagiaire_name, stagiaire_prenom=stagiaire_prenom).send_mail(related_document.id,force_send=True)
                return werkzeug.utils.redirect("/my/report/%s" % slug(related_document))
                return request.redirect('/my/internships')
                return request.render("internship_management_module.portal_report_submit", values)
                
            if report:
                report_file = report.read()
                post.update({'report': base64.b64encode(report_file)})
                values.update({
                    'datas':base64.b64encode(report_file)})
            values.update({
                'start_stage_date':post.get('start_stage_date'),
                'had_difficulties_finding_ms':post.get('had_difficulties_finding_ms'),
                'had_change_maitre_stage':post.get('had_difficulties_courses'),
                'had_difficulties_courses':post.get('had_difficulties_courses'),
                'remarks_difficulties_courses':post.get('remarks_difficulties_courses'),
                'had_difficulties_works':post.get('had_difficulties_works'),
                'remarks_difficulties_works':post.get('remarks_difficulties_works'),
                'remarks_deroulement_stage':post.get('remarks_deroulement_stage'),
                'name':post.get('name'),
            })
            
            if line_1:
                line_1.write({'charge_horaire': post.get('charge_horaire_1')})
            else:
                request.env['realised.work.line'].create({'name' : "Audit Comptable et financier", 'charge_horaire': post.get('charge_horaire_1'), 'document_id': related_document.id})

            if line_2:
                line_2.write({'charge_horaire': post.get('charge_horaire_2')})
            else:
                request.env['realised.work.line'].create({'name' : "Evaluation du dispositif de contrôle interne", 'charge_horaire': post.get('charge_horaire_2'), 'document_id': related_document.id})

            if line_3:
                line_3.write({'charge_horaire': post.get('charge_horaire_3')})
            else:
                request.env['realised.work.line'].create({'name' : "Expertise comptable et revision des comptes", 'charge_horaire': post.get('charge_horaire_3'), 'document_id': related_document.id})

            if line_4:
                line_4.write({'charge_horaire': post.get('charge_horaire_4')})
            else:
                request.env['realised.work.line'].create({'name' : "Assistance à l'élaboration des liasses fiscales", 'charge_horaire': post.get('charge_horaire_4'), 'document_id': related_document.id})

            if line_5:
                line_5.write({'charge_horaire': post.get('charge_horaire_5')})
            else:
                request.env['realised.work.line'].create({'name' : "Préparation des etats de synthèse (ETIC)", 'charge_horaire': post.get('charge_horaire_5'), 'document_id': related_document.id})

            if line_6:
                line_6.write({'charge_horaire': post.get('charge_horaire_6')})
            else:
                request.env['realised.work.line'].create({'name' : "Reporting IFRS", 'charge_horaire': post.get('charge_horaire_6'), 'document_id': related_document.id})
            
            related_document.sudo().write(values)
            if redirect:
                return request.redirect(redirect)
            share_vals = {
                'type': 'ids',
                'document_ids': [(4, related_document.id)],
                'folder_id': related_document.folder_id.id
            }
            share = request.env['documents.share'].sudo().create(share_vals)
            base_url = request.env["ir.config_parameter"].sudo().get_param("web.base.url")
            url = "%s/document/download/%s/%s/%s" % (base_url, share.id, share.access_token, related_document.id)
            signature_url = "%s/web/image?model=documents.document&amp;id=%s&amp;field=signature" % (base_url, related_document.id)
            signature_cs_url = "%s/web/image?model=documents.document&amp;id=%s&amp;field=signature_cs" % (base_url, related_document.id)
            values.update({
                           'report': related_document,
                           'url': url,
                           'partner': partner,
                           'signature_url': signature_url,
                            'signature_cs_url': signature_cs_url
                           })
            
            email = request.env.ref('base.user_admin').email
            email_to = related_document.internship_supervisor_id.email
            name = related_document.internship_supervisor_id.name
            second_name = related_document.internship_supervisor_id.second_name
            stagiaire_name = related_document.internship_id.name
            stagiaire_prenom = related_document.internship_id.second_name
            email_template_report_deposed = request.env.ref('internship_management_module.email_template_report_deposed')
            email_template_report_deposed.with_context(email_from=email, email_to=email_to, name=name, second_name=second_name, stagiaire_name=stagiaire_name, stagiaire_prenom=stagiaire_prenom).send_mail(related_document.id,force_send=True)

            values.update({
                'charge_horaire_1': line_1.charge_horaire if line_1 else 0,
                'charge_horaire_2': line_2.charge_horaire if line_2 else 0,
                'charge_horaire_3': line_3.charge_horaire if line_3 else 0,
                'charge_horaire_4': line_4.charge_horaire if line_4 else 0,
                'charge_horaire_5': line_5.charge_horaire if line_5 else 0,
                'charge_horaire_6': line_6.charge_horaire if line_6 else 0,

            })

            print ('I m here')
            return request.render("internship_management_module.portal_report_submit", values)
        
        values.update({
            'report': report,
            'charge_horaire_1': int(line_1.charge_horaire) if line_1 else 0,
            'charge_horaire_2': int(line_2.charge_horaire) if line_2 else 0,
            'charge_horaire_3': int(line_3.charge_horaire) if line_3 else 0,
            'charge_horaire_4': int(line_4.charge_horaire) if line_4 else 0,
            'charge_horaire_5': int(line_5.charge_horaire) if line_5 else 0,
            'charge_horaire_6': int(line_6.charge_horaire) if line_6 else 0,
            
        })
        share_vals = {
                'type': 'ids',
                'document_ids': [(4, related_document.id)],
                'folder_id': related_document.folder_id.id
        }
        share = request.env['documents.share'].sudo().create(share_vals)
        base_url = request.env["ir.config_parameter"].sudo().get_param("web.base.url")
        url = "%s/document/download/%s/%s/%s" % (base_url, share.id, share.access_token, related_document.id)
        signature_url = "%s/web/image?model=documents.document&id=%s&field=signature" % (base_url, related_document.id)
        signature_cs_url = "%s/web/image?model=documents.document&id=%s&field=signature_cs" % (base_url, related_document.id)
        values.update({
                           'report': related_document,
                           'url': url,
                           'partner': partner,
                           'signature_url': signature_url,
                            'signature_cs_url':signature_cs_url
        })
        
        response = request.render("internship_management_module.portal_report_submit", values)
        #response.headers['X-Frame-Options'] = 'DENY'
        return response

    @route(['/report/success/<string:id>'], type='http', auth='user', website=True)
    def report_success(self, id=None,redirect=None, **post):
        partner = request.env.user.partner_id
        report = request.env['documents.document'].sudo().browse(int(id))
        report.sudo().write({'depot_date': odoo_fields.Date.today()})
        if request.httprequest.method == 'POST':
            if redirect:
                return request.redirect(redirect)
            return request.redirect('/')
        
        response = request.render("internship_management_module.portal_report_success")
        #response.headers['X-Frame-Options'] = 'DENY'
        return response

# maite de stage route

    @http.route(['/my/internships/ms'], type='http', auth="user", website=True)
    def portal_my_internships_ms(self, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        Documents = request.env['documents.document']

        domain = [
            '|', ('internship_id', '=', partner.id),
            ('internship_supervisor_id', '=', partner.id),
            ('folder_id.name', '=', 'Rapports de stage'),
        ]

        searchbar_sortings = {
            'date': {'label': _('Créé le'), 'order': 'create_date desc'},
            'name': {'label': _('Nom'), 'order': 'name'},
        }

        # default sortby Document
        if not sortby:
            sortby = 'date'
        sort_order = searchbar_sortings[sortby]['order']

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]


        # count for pager
        document_count = Documents.search_count(domain)
        # make pager
        pager = portal_pager(
            url="/my/internships",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=document_count,
            step=self._items_per_page
        )
        reports = Documents.search(domain, order=sort_order, limit=self._items_per_page, offset=pager['offset'])

        # Grouper les rapports par stagiaire
        grouped_reports = defaultdict(list)
        for report in reports:
            grouped_reports[report.internship_id].append(report)

        values.update({
            'date': date_begin,
            'grouped_reports': grouped_reports,
            'page_name': 'report',
            'pager': pager,
            'default_url': '/my/internships',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'partner': partner
        })

        return request.render("internship_management_module.portal_my_internships", values)

    # Controleur de stage route
    @http.route(['/my/internships/cs'], type='http', auth="user", website=True)
    def portal_my_internships_cs(self, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        Documents = request.env['documents.document']

        domain = [
            '|', ('internship_id', '=', partner.id),
            ('internship_controler_id', '=', partner.id),
            ('folder_id.name', '=', 'Rapports de stage'),
        ]

        searchbar_sortings = {
            'date': {'label': _('Créé le'), 'order': 'create_date desc'},
            'name': {'label': _('Nom'), 'order': 'name'},
        }

        # default sortby Document
        if not sortby:
            sortby = 'date'
        sort_order = searchbar_sortings[sortby]['order']

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # count for pager
        document_count = Documents.search_count(domain)
        # make pager
        pager = portal_pager(
            url="/my/internships",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=document_count,
            step=self._items_per_page
        )
        reports = Documents.search(domain, order=sort_order, limit=self._items_per_page, offset=pager['offset'])

        # Grouper les rapports par stagiaire
        grouped_reports = defaultdict(list)
        for report in reports:
            grouped_reports[report.internship_id.id].append(report)

        values.update({
            'date': date_begin,
            'grouped_reports': grouped_reports,
            'page_name': 'report',
            'pager': pager,
            'default_url': '/my/internships',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'partner': partner
        })

        return request.render("internship_management_module.portal_my_internships", values)
    
    @http.route(['/my/internships'], type='http', auth="user", website=True)
    def portal_my_internships(self, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        Documents = request.env['documents.document']

        domain = [
            '|', '|', ('internship_id', '=', partner.id),
            ('internship_supervisor_id', '=', partner.id),
            ('internship_controler_id', '=', partner.id),
            ('folder_id.name', '=', 'Rapports de stage'),
        ]

        searchbar_sortings = {
            'date': {'label': _('Créé le'), 'order': 'create_date desc'},
            'name': {'label': _('Nom'), 'order': 'name'},
        }

        # default sortby Document
        if not sortby:
            sortby = 'date'
        sort_order = searchbar_sortings[sortby]['order']

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # count for pager
        document_count = Documents.search_count(domain)
        # make pager
        pager = portal_pager(
            url="/my/internships",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=document_count,
            step=self._items_per_page
        )
        # search the count to display, according to the pager data
        reports = Documents.search(domain, order=sort_order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_reports_history'] = reports.ids[:100]
        partner = request.env.user.partner_id
        values.update({
            'date': date_begin,
            'reports': reports.sudo(),
            'page_name': 'report',
            'pager': pager,
            'default_url': '/my/internships',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'partner': partner
        })
        return request.render("internship_management_module.portal_my_internships", values)

    @route('/Hoome', type='http', auth="user", website=True)
    def my_home(self, **kw):
        # Préparer les données à afficher dans la vue
        values = self._prepare_portal_layout_values()
        values.update({
            'custom_message': 'Bienvenue sur votre page personnalisée!',
            # Vous pouvez ajouter plus de données ici
        })
        return request.render("internship_management_module.portal_my_home_cust", values)
    
    @route(['/re_registration'], type='http', auth='user', website=True)
    def re_registration(self, redirect=None, **post):
        values = {}
        partner_vals = {}
        centers = request.env['operating.unit'].sudo().search([])
        pays = request.env['res.country'].sudo().search([])
        partner = request.env.user.partner_id
        if post and request.httprequest.method == 'POST':
        
            document_dict = {key: post[key] for key in self.DOCUMENT_FIELDS if key in post}
            for key in document_dict.keys():
                if post.get(key):
                    file = post.get(key)
                    filename = post.get(key).filename
                    post.update({key: base64.b64encode(file.read())})
                    filename_field = key + '_filename'
                    partner_vals.update({filename_field : filename})
                else:
                    del post[key]
            
            if partner.mode_registration == 'pm':
                repartition_dict = {key: post[key] for key in self.REPARTITION_CAPITAL_SOCIAL_FIELDS if key in post}  
                values_table = []
                for i in range(1,6):
                    name = 'name' + str(i)
                    percentage = 'percentage' + str(i)
                    status = 'status' + str(i)
                    values_table.append((0,0, {'name': post.get(name) if post.get(name) else '',
                                                 'percentage': post.get(percentage) if post.get(percentage) else 0,
                                                 'status': post[status] if post[status] else None}))
                
                partner_vals.update({'repartition_ids': values_table})
                partner.write({'repartition_ids': None})
            
            partner_vals.update({key: post[key] for key in self.REGISTRATION_FIELDS if key in post})
            for field in set(['conseil_regional']) & set(partner_vals.keys()):
                    try:
                        partner_vals[field] = int(partner_vals[field])
                    except:
                        partner_vals[field] = False
            if 'photographies_recentes' in post:           
                partner_vals.update({'image_1920': post['photographies_recentes']})
                
            partner.write(partner_vals)
        values.update({
            'error': {},
            'error_message': [],
            'register_types': [["pm","Personne morale"],["pp1","Personne physique à titre individuel"], ["pp2","Personne physique exerçant en société"], ["pp3","Personne physique en tant que salarié"], ["pp4","Personne physique exerçant en tant qu\'associé d\'un cabinet inscrit"]],
            'centers': centers,
            'payss':pays,
            'partner': partner
        })
        
        if partner.mode_registration == 'pm':
            etat_repartition = {}
            count = 0
            for repartition in partner.repartition_ids:
                count += 1
                name = 'name' + str(count)
                percentage = 'percentage' + str(count)
                status = 'status' + str(count)
                etat_repartition.update({
                    name : repartition.name,
                    percentage : repartition.percentage,
                    status : repartition.status
                })
            values.update(etat_repartition)
        response = request.render("internship_management_module.portal_re_registration", values)
        #response.headers['X-Frame-Options'] = 'DENY'
        return response
    
    @http.route(['/list-stagiaires-ms'], type='http', auth="user", website=True)
    def stagiaires(self, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        print(partner)
        Stagiaires = request.env['res.partner']

        domain = [
            ('internship_supervisor_id', '=', partner.id),
        ]

        searchbar_sortings = {
            'date': {'label': _('Créé le'), 'order': 'create_date desc'},
            'name': {'label': _('Nom'), 'order': 'name'},
        }

        # default sortby Document
        if not sortby:
            sortby = 'date'
        sort_order = searchbar_sortings[sortby]['order']

        '''if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]'''
        print (domain)
        # count for pager
        stagiaire_count = Stagiaires.search_count(domain)
        # make pager
        pager = portal_pager(
            url="/my/internships",
            url_args={'sortby': sortby},
            total=stagiaire_count,
            step=self._items_per_page
        )
        # search the count to display, according to the pager data
        stagiaires = Stagiaires.search(domain, order=sort_order, limit=self._items_per_page, offset=pager['offset'])
        #request.session['my_reports_history'] = reports.ids[:100]
        print (stagiaires)
        values.update({
            'stagiaires': stagiaires.sudo(),
            'page_name': 'stagiaire',
            'pager': pager,
            'default_url': '/my/internships',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("internship_management_module.portal_stagiaires", values)
    
    @http.route(['/list-stagiaires-cs'], type='http', auth="user", website=True)
    def stagiaires_cs(self, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        print('hhhhhhhhhhhhh')
        Stagiaires = request.env['res.partner']

        domain = [
            ('internship_controler_id', '=', partner.id),
        ]

        searchbar_sortings = {
            'date': {'label': _('Créé le'), 'order': 'create_date desc'},
            'name': {'label': _('Nom'), 'order': 'name'},
        }

        # default sortby Document
        if not sortby:
            sortby = 'date'
        sort_order = searchbar_sortings[sortby]['order']

        '''if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]'''
        print (domain)
        # count for pager
        stagiaire_count = Stagiaires.search_count(domain)
        # make pager
        pager = portal_pager(
            url="/my/internships",
            url_args={'sortby': sortby},
            total=stagiaire_count,
            step=self._items_per_page
        )
        # search the count to display, according to the pager data
        stagiaires = Stagiaires.search(domain, order=sort_order, limit=self._items_per_page, offset=pager['offset'])
        #request.session['my_reports_history'] = reports.ids[:100]
        print (stagiaires)
        values.update({
            'stagiaires': stagiaires.sudo(),
            'page_name': 'stagiaire',
            'pager': pager,
            'default_url': '/my/internships',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("internship_management_module.portal_stagiaires", values)
    
    
    @http.route(['/list-members'], type='http', auth="public", website=True)
    def stagiaires_members(self, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        print(partner)
        Members = request.env['res.partner']

        domain = [
            ('contact_type_id.code', '=', 'EC'),
        ]

        searchbar_sortings = {
            'date': {'label': _('Créé le'), 'order': 'create_date desc'},
            'name': {'label': _('Nom'), 'order': 'name'},
        }

        # default sortby Document
        if not sortby:
            sortby = 'date'
        sort_order = searchbar_sortings[sortby]['order']

        '''if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]'''
        # count for pager
        member_count = Members.sudo().search_count(domain)
        # make pager
        pager = portal_pager(
            url="/my/internships",
            url_args={'sortby': sortby},
            total=member_count,
            step=self._items_per_page
        )
        # search the count to display, according to the pager data
        members = Members.sudo().search(domain, order=sort_order, limit=self._items_per_page, offset=pager['offset'])
        #request.session['my_reports_history'] = reports.ids[:100]
        values.update({
            'members': members.sudo(),
            'page_name': 'members',
            'pager': pager,
            'default_url': '/my/internships',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("internship_management_module.portal_members", values)

from odoo import http
from odoo.http import request
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from werkzeug.utils import redirect


class SignupRedirectController(AuthSignupHome):

    @http.route('/web/signup', type='http', auth='public', website=True, sitemap=False)
    def web_auth_signup(self, *args, **kw):
        # Call the parent signup method first
        response = super(SignupRedirectController, self).web_auth_signup(*args, **kw)
        
        # Check if signup was successful (user is now logged in)
        if request.session.uid:
            # Define your target URL here
            target_url = '/demande-inscription'  # Change this to your desired URL
            
            # You can also make it dynamic based on user properties
            # user = request.env.user
            # if user.has_group('base.group_portal'):
            #     target_url = '/portal'
            # elif user.has_group('base.group_user'):
            #     target_url = '/web'
            
            return redirect(target_url)
        
        # If signup wasn't successful, return the original response
        return response


#class CustomLoginController(http.Controller):

    #@http.route('/web/login', type='http', auth="none", website=True)
    #def custom_login(self, **kwargs):
     #   response = request.render('internship_management_module.custom_login_template', {})
      #  response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
       # response.headers['Pragma'] = 'no-cache'
        #return response