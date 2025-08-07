# -*- coding: utf-8 -*-
import random
import string
from odoo import api, fields, models, _
from datetime import datetime, timedelta,date
from odoo.exceptions import ValidationError, UserError
from odoo.http import request
import logging
import werkzeug
from lxml import etree
from markupsafe import escape, Markup
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)


class ProfilChange(models.Model):
    _name = 'profil.change'

    user_id = fields.Many2one(comodel_name='res.users', string='Utilisateur')
    date = fields.Date(string="Date d'attribution")
    profil = fields.Selection(string="Profile", selection='_get_profils')

    @api.model
    def _get_profils(self):
        return [
            ('gs', _("Gestionnaire OEC")),
            ('me', _("Membre élu")),
            ('sg', _('Secrétaire général')),
            ('pc', _('Président du CROEC')),
            ('cn', _('Conseil national'))
        ]

class RepartitionCapitalSociaLine(models.Model):

    _name = 'repartition.capital.social.line'

    name = fields.Char(string="Associé")
    percentage = fields.Integer(string="Pourcentage")
    status = fields.Selection(string="Qualité de l'associé", selection='_get_status', default='associe_expert_comptable')
    partner_id = fields.Many2one(comodel_name='res.partner', string="EC")

    @api.model
    def _get_status(self):
        return [
            ('associe_expert_comptable', _("Associé Expert comptable inscrit")),
            ('associe_salarie', _("Associé Salarié")),
            ('associe_non_salarie', _('Associé Non Salarié'))
        ]

class ResPartnerRejectLine(models.TransientModel):
    _name = 'res.partner.reject.line'

    reject_id = fields.Many2one(comodel_name='res.partner.reject')
    document = fields.Selection(string='Document', selection='_get_document_list')
    reserve = fields.Char(string='Réserve')

    @api.model
    def _get_document_list(self):
        return [
            ('lettre_demande_inscription', _("Lettre de demande d’inscription à l'ordre")),
            ('declaration_sur_honneur', _("Déclaration sur l’honneur")),
            ('actes_modificatifs', _('Actes modificatifs')),
            ('copie_bo_jal', _('Copie du BO et du JAL')),
            ('actes_cession', _('Actes de cession de parts sociales ou de transferts d’actions')),
            ('statuts', _('Statuts mis à jour')),
            ('copie_conforme_contrat', _('Copie certifiée conforme du contrat de bail')),
            ('modele_7', _('Certificat modèle 7 du Registre du Commerce')),
            ('attestation_radiation', _('Attestation de radiation')),
            ('attestation_assurance', _('Attestation d’assurance Responsabilité Civile')),
            ('attestation_inscription', _("Attestation d'inscription à la Taxe Professionnelle")),
            ('bulletin_notification', _('Bulletin de notification de l’Identifiant Fiscal')),
            ('contrat_travail', _('Contrat de travail')),
            ('copie_cin', _('CIN')),
            ('copie_cnie', _('CNIE')),
            ('diplome_document', _('Diplôme')),
            ('engagement', _('Engagement')),
            ('attestation_inscription_membre', _('Attestation d’inscription')),
            ('extrait_casier_judiciaire', _('Un extrait du casier judiciaire ou une fiche anthropométrique datant de moins de trois mois')),
            ('extrait_acte_naissance', _('Un extrait d’acte de naissance datant de moins de trois mois')),
            ('photographies_recentes', _('Trois photographies récentes du candidat')),
            ('photocopie_diplome', _('Une photocopie du diplôme national d’Expert-Comptable ou d’un diplôme reconnu équivalent, signé et cacheté (certifiée conforme à l’original)')),
            ('attestation_equivalence', _('Une attestation d’équivalence au diplôme national d’expertise comptable, délivrée par le ministère d’enseignement supérieur, pour tous les diplômes étrangers')),
            ('fiches_annuelles', _('Trois Fiches annuelles de stage, pour le diplôme français')),
            ('attestation_fin_stage', _("L'attestation de fin de stage, pour le diplôme français")),
            ('fiche_generale_synthese', _("La fiche générale de synthèse, pour le diplôme français")),
            ('fiche_annuelle', _("La fiche annuelle de 200 heures d’audit pour les diplômes étrangers")),
            ('copie_convention', _("Une copie de la convention de réciprocité prévue à l’article 20 de la loi 15/89 pour les étrangers")),
            ('certificat_residence', _("Un certificat de résidence et éventuellement les justificatifs de paiement d’impôts au Maroc, pour les candidats étrangers")),
            ('demande_inscription_societe', _("Lettre de demande d’inscription à l’Ordre, cachetée et signée par la société")),
            ('demande_inscription_salarie', _("Lettre de demande d’inscription à l’Ordre, daté et signée par le salarié")),
            ('avenant_contrat_travail', _("Avenant au contrat de travail visé par le Président du Conseil National")),
            ('copie_contrat_bail', _("Copie du Contrat de bail du cabinet (certifié conforme à l’original)"))
        ]

class ResPartnerRejectLine(models.Model):
    _name = 'reject.line'

    partner_id = fields.Many2one(comodel_name='res.partner')
    document = fields.Selection(string='Document', selection='_get_document_list')
    reserve = fields.Char(string='Réserve')

    @api.model
    def _get_document_list(self):
        return [
            ('lettre_demande_inscription', _("Lettre de demande d’inscription à l'ordre")),
            ('declaration_sur_honneur', _("Déclaration sur l’honneur")),
            ('actes_modificatifs', _('Actes modificatifs')),
            ('copie_bo_jal', _('Copie du BO et du JAL')),
            ('actes_cession', _('Actes de cession de parts sociales ou de transferts d’actions')),
            ('statuts', _('Statuts mis à jour')),
            ('copie_conforme_contrat', _('Copie certifiée conforme du contrat de bail')),
            ('modele_7', _('Certificat modèle 7 du Registre du Commerce')),
            ('attestation_radiation', _('Attestation de radiation')),
            ('attestation_assurance', _('Attestation d’assurance Responsabilité Civile')),
            ('attestation_inscription', _("Attestation d'inscription à la Taxe Professionnelle")),
            ('bulletin_notification', _('Bulletin de notification de l’Identifiant Fiscal')),
            ('contrat_travail', _('Contrat de travail')),
            ('copie_cin', _('CIN')),
            ('copie_cnie', _('CNIE')),
            ('diplome_document', _('Diplôme')),
            ('engagement', _('Engagement')),
            ('attestation_inscription_membre', _('Attestation d’inscription')),
            ('extrait_casier_judiciaire', _('Un extrait du casier judiciaire ou une fiche anthropométrique datant de moins de trois mois')),
            ('extrait_acte_naissance', _('Un extrait d’acte de naissance datant de moins de trois mois')),
            ('photographies_recentes', _('Trois photographies récentes du candidat')),
            ('photocopie_diplome', _('Une photocopie du diplôme national d’Expert-Comptable ou d’un diplôme reconnu équivalent, signé et cacheté (certifiée conforme à l’original)')),
            ('attestation_equivalence', _('Une attestation d’équivalence au diplôme national d’expertise comptable, délivrée par le ministère d’enseignement supérieur, pour tous les diplômes étrangers')),
            ('fiches_annuelles', _('Trois Fiches annuelles de stage, pour le diplôme français')),
            ('attestation_fin_stage', _("L'attestation de fin de stage, pour le diplôme français")),
            ('fiche_generale_synthese', _("La fiche générale de synthèse, pour le diplôme français")),
            ('fiche_annuelle', _("La fiche annuelle de 200 heures d’audit pour les diplômes étrangers")),
            ('copie_convention', _("Une copie de la convention de réciprocité prévue à l’article 20 de la loi 15/89 pour les étrangers")),
            ('certificat_residence', _("Un certificat de résidence et éventuellement les justificatifs de paiement d’impôts au Maroc, pour les candidats étrangers")),
            ('demande_inscription_societe', _("Lettre de demande d’inscription à l’Ordre, cachetée et signée par la société")),
            ('demande_inscription_salarie', _("Lettre de demande d’inscription à l’Ordre, daté et signée par le salarié")),
            ('avenant_contrat_travail', _("Avenant au contrat de travail visé par le Président du Conseil National")),
            ('copie_contrat_bail', _("Copie du Contrat de bail du cabinet (certifié conforme à l’original)"))
        ]

class ResPartnerReject(models.TransientModel):

    _name = 'res.partner.reject'

    type =  fields.Selection(string="Type de rejet", selection='_get_types', default='definitif')
    partner_id = fields.Many2one(comodel_name='res.partner')
    reject_line_ids = fields.One2many(comodel_name='res.partner.reject.line', inverse_name='reject_id')

    @api.model
    def _get_types(self):
        return [
            ('definitif', _("Rejet défintif")),
            ('reserve', _("Rejet avec réserve"))
        ]

    def confirm(self):
        Reject = self.env['reject.line']
        partner = self.partner_id
        if self.type == 'definitif':
            partner.write({
                    'status_register':'rejected',
                    'date_final_conseil_national': fields.Date.today()
                })
            template = self.env.ref('internship_management_module.email_template_reject_registration')
            email = self.env.ref('base.user_admin').email
            template.with_context(email_from=email).send_mail(self.id,force_send=True)
        else:
            for reject_line in self.reject_line_ids:
                Reject.create({
                               'document': reject_line.document,
                               'reserve': reject_line.reserve,
                               'partner_id': partner.id})
            partner.write({
                           'is_first_rejected': True,
                           'status_register': 'account_created'})
        return True

class ResPartnerRegistrationReserve(models.TransientModel):

    _name = 'res.partner.registration.reserve'

    motif = fields.Text(string="Réserve", required=True)
    partner_id = fields.Many2one(comodel_name='res.partner')

    def confirm(self):
        if self.partner_id.status_register == 'in_progress':
            self.partner_id.write({'reserve_croec' : self.motif,
                                    'date_initial_croec': fields.Date.today()})
            self.partner_id._send_email_reserve()
            self.partner_id.status_register = 'account_created'

        elif self.partner_id.status_register == 'in_progress_member_elu':
            self.partner_id.write({'reserve_member_elu' : self.motif,
                                    'status_register':'in_progress_to_depose',
                                    'date_final_member_elu': fields.Date.today(),
                                    'date_initial_secretaire_general': fields.Date.today()})
            # Send an email to CROEC


        elif self.partner_id.status_register == 'in_progress_secretaire_general':
            self.partner_id.write({'reserve_secretaire_general' : self.motif,
                                    'status_register':'in_progress_president_conseil',
                                    'date_final_secretaire_general': fields.Date.today(),
                                    'date_initial_president_conseil': fields.Date.today()})

        else:
            self.partner_id.write({'reserve_president_conseil' : self.motif,
                                    'status_register':'in_progress_conseil_national',
                                    'date_final_president_conseil': fields.Date.today(),
                                    'date_initial_conseil_national': fields.Date.today()})

class ResPartnerRegistrationUnfavorable(models.TransientModel):

    _name = 'res.partner.registration.unfavorable'

    motif = fields.Text(string="Motif")
    partner_id = fields.Many2one(comodel_name='res.partner')

    def confirm(self):
        if self.partner_id.status_register == 'in_progress_member_elu':
            self.partner_id.write({'reserve_member_elu' : 'Avis défavorable' + '\n' + self.motif,
                                    'status_register':'account_created',
                                    'date_final_member_elu': fields.Date.today(),
                                    'date_initial_secretaire_general': fields.Date.today()})

        elif self.partner_id.status_register == 'in_progress_secretaire_general':
            self.partner_id.write({'reserve_secretaire_general' : 'Avis défavorable' + '\n' + self.motif,
                                    'status_register':'account_created',
                                    'date_final_secretaire_general': fields.Date.today(),
                                    'date_initial_president_conseil': fields.Date.today()})

        else:
            self.partner_id.write({'reserve_president_conseil' : 'Avis défavorable' + '\n' + self.motif,
                                    'status_register':'account_created',
                                    'date_final_president_conseil': fields.Date.today(),
                                    'date_initial_conseil_national': fields.Date.today()})

    # def confirm(self):
    #     if self.partner_id.status_register == 'in_progress_member_elu':
    #         self.partner_id.write({'reserve_member_elu' : 'Avis défavorable' + '\n' + self.motif,
    #                                 'status_register':'in_progress_secretaire_general',
    #                                 'date_final_member_elu': fields.Date.today(),
    #                                 'date_initial_secretaire_general': fields.Date.today()})

    #     elif self.partner_id.status_register == 'in_progress_secretaire_general':
    #         self.partner_id.write({'reserve_secretaire_general' : 'Avis défavorable' + '\n' + self.motif,
    #                                 'status_register':'in_progress_president_conseil',
    #                                 'date_final_secretaire_general': fields.Date.today(),
    #                                 'date_initial_president_conseil': fields.Date.today()})

    #     else:
    #         self.partner_id.write({'reserve_president_conseil' : 'Avis défavorable' + '\n' + self.motif,
    #                                 'status_register':'in_progress_conseil_national',
    #                                 'date_final_president_conseil': fields.Date.today(),
    #                                 'date_initial_conseil_national': fields.Date.today()})

class ResPartner(models.Model):

    _inherit = 'res.partner'
    _rec_name = 'display_name'

    # --------------------------------------------------------------------
    # FIELDS
    # --------------------------------------------------------------------

    mandat_number = fields.Integer(string="Nombre de mandats")
    date_inscription = fields.Date(string="Date d'inscription")
    is_first_rejected = fields.Boolean(string='Premier rejet?', readonly=True)
    reject_line_ids = fields.One2many(comodel_name='reject.line', inverse_name='partner_id', string='Détail du rejet CN', readonly=True)
    display_name = fields.Char(string='Display Name', compute='_compute_display_name', store=True)
    repartition_ids = fields.One2many('repartition.capital.social.line', 'partner_id', string='Etat de répartition du capital social')
    related_pp_id = fields.Many2one(comodel_name='res.partner', string="Personne physique")
    contact_type = fields.Char(related="contact_type_id.code", string='Prénom', store=True)
    status_register = fields.Selection(string='Register status', selection='_get_status_register', default='draft', tracking=True)
    status_register_a = fields.Selection(related='status_register')
    status_register_b = fields.Selection(related='status_register')
    status_register_c = fields.Selection(related='status_register')
    status_register_d = fields.Selection(related='status_register')
    status_register_e = fields.Selection(related='status_register')
    status_register_f = fields.Selection(related='status_register')
    status_register_g = fields.Selection(related='status_register')
    status_register_j = fields.Selection(related='status_register')
    status_register_l = fields.Selection(related='status_register')
    status_register_m = fields.Selection(related='status_register')
    mode_registration = fields.Selection(string="Mode d'inscription", selection='_get_registration_mode', default='pm')
    sexe = fields.Selection(string="Sexe", selection=[('male', _('Homme')),('female', _('Femme'))], default='male')
    cin_number = fields.Char(string="CIN")
    diplome = fields.Selection(string="Diplome", selection=[('marocain', _('Marocain')),('francais', _('Français')),('autre', _('Autre'))], default='marocain')
    #already_registred = fields.Selection(string="Mode d’exercice de la profession d’Expert-Comptable", selection=[('yes', _('Oui')),('no', _('Non'))], default='yes')
    raison_sociale = fields.Char(string="Raison sociale")
    forme_juridique = fields.Char(string="Forme juridique")  # Legacy Field !!!!
    legal_form = fields.Selection(string="Forme juridique", selection='_get_formes_juridiques')
    siege_social = fields.Char(string="Siège social")
    capital_social = fields.Char(string="Etat de répartition du capital social")
    effectif = fields.Integer(string="Effectif employé par le cabinet")
    identifiant_fiscal = fields.Char(string="Identifiant fiscal")
    taxe_professionnelle = fields.Char(string="Taxe professionnelle")
    conseil_regional = fields.Many2one(comodel_name='operating.unit', string='Conseil Régional')
    gsm = fields.Char(string='GSM')
    fax = fields.Char(string='Fax')

    lettre_demande_inscription = fields.Binary(string="Lettre de demande d’inscription à l'ordre", attachment=True)
    lettre_demande_inscription_filename = fields.Char(string='Lettre de demande d’inscription filename')
    valid_lettre_demande_inscription = fields.Selection(string='',selection='_get_validation')
    motif_lettre_demande_inscription = fields.Char(string='',tracking=True)

    #lettre_demande_inscription_societe = fields.Binary(string="Lettre de demande d’inscription précisant la liste des associés, le pourcentage de participation de chacun et l’identité des dirigeants", attachment=True)
    #lettre_demande_inscription_societe_filename = fields.Char(string='Lettre de demande d’inscription filename')

    declaration_sur_honneur = fields.Binary(string="Déclaration sur l’honneur", attachment=True)
    declaration_sur_honneur_filename = fields.Char(string='Déclaration sur l’honneur filename')
    valid_declaration_sur_honneur = fields.Selection(string='',selection='_get_validation')
    motif_declaration_sur_honneur = fields.Char(string='',tracking=True)

    #declaration_sur_honneur_societe = fields.Binary(string="Déclaration sur l’honneur (Société)", attachment=True)
    #declaration_sur_honneur_societe_filename = fields.Char(string='Déclaration sur l’honneur filename')

    actes_modificatifs = fields.Binary(string="Actes modificatifs", attachment=True)
    actes_modificatifs_filename = fields.Char(string='Actes modificatifs filename')
    valid_actes_modificatifs = fields.Selection(string='',selection='_get_validation')
    motif_actes_modificatifs = fields.Char(string='',tracking=True)

    copie_bo_jal = fields.Binary(string="Copie du BO et du JAL", attachment=True)
    copie_bo_jal_filename = fields.Char(string='Copie du BO et du JAL filename')
    valid_copie_bo_jal = fields.Selection(string='',selection='_get_validation')
    motif_copie_bo_jal = fields.Char(string='',tracking=True)

    actes_cession = fields.Binary(string="Actes de cession de parts sociales ou de transferts d’actions", attachment=True)
    actes_cession_filename = fields.Char(string='Actes de cession de parts sociales ou de transferts d’actions filename')
    valid_actes_cession = fields.Selection(string='',selection='_get_validation')
    motif_actes_cession = fields.Char(string='',tracking=True)

    statuts = fields.Binary(string="Statuts mis à jour ", attachment=True)
    statuts_filename = fields.Char(string='Statuts mis à jour filename')
    valid_statuts = fields.Selection(string='',selection='_get_validation')
    motif_statuts = fields.Char(string='',tracking=True)

    copie_conforme_contrat = fields.Binary(string="Copie certifiée conforme du contrat de bail ", attachment=True)
    copie_conforme_contrat_filename = fields.Char(string='Copie certifiée conforme du contrat de bail  filename')
    valid_copie_conforme_contrat = fields.Selection(string='',selection='_get_validation')
    motif_copie_conforme_contrat = fields.Char(string='',tracking=True)

    modele_7 = fields.Binary(string="Certificat modèle 7 du Registre du Commerce ", attachment=True)
    modele_7_filename = fields.Char(string='Certificat modèle 7 du Registre du Commerce  filename')
    valid_modele_7 = fields.Selection(string='',selection='_get_validation')
    motif_modele_7 = fields.Char(string='',tracking=True)

    attestation_radiation = fields.Binary(string="Attestation de radiation", attachment=True)
    attestation_radiation_filename = fields.Char(string='Attestation de radiation filename')
    valid_attestation_radiation = fields.Selection(string='',selection='_get_validation')
    motif_attestation_radiation = fields.Char(string='',tracking=True)

    attestation_assurance = fields.Binary(string="Attestation d’assurance Responsabilité Civile ", attachment=True)
    attestation_assurance_filename = fields.Char(string='Attestation d’assurance Responsabilité Civile  filename')
    valid_attestation_assurance = fields.Selection(string='',selection='_get_validation')
    motif_attestation_assurance = fields.Char(string='',tracking=True)

    attestation_inscription = fields.Binary(string="Attestation d'inscription à la Taxe Professionnelle  ", attachment=True)
    attestation_inscription_filename = fields.Char(string="Attestation d'inscription à la Taxe Professionnelle filename")
    valid_attestation_inscription = fields.Selection(string='',selection='_get_validation')
    motif_attestation_inscription = fields.Char(string='',tracking=True)

    bulletin_notification = fields.Binary(string="Bulletin de notification de l’Identifiant Fiscal ", attachment=True)
    bulletin_notification_filename = fields.Char(string="Bulletin de notification de l’Identifiant Fiscal  filename")
    valid_bulletin_notification = fields.Selection(string='',selection='_get_validation')
    motif_bulletin_notification = fields.Char(string='',tracking=True)

    '''copie_cheque = fields.Binary(string="Copie Chèque ", attachment=True)
    copie_cheque_filename = fields.Char(string="Copie Chèque  filename")
    valid_copie_cheque = fields.Selection(string='',selection='_get_validation')
    motif_copie_cheque = fields.Char(string='',tracking=True)'''

    contrat_travail = fields.Binary(string="Contrat de travail ", attachment=True)
    contrat_travail_filename = fields.Char(string="Contrat de travail  filename")
    valid_contrat_travail = fields.Selection(string='',selection='_get_validation')
    motif_contrat_travail = fields.Char(string='',tracking=True)

    copie_cin = fields.Binary(string="CIN ", attachment=True)
    copie_cin_filename = fields.Char(string="Copie de la CIN  filename")
    valid_copie_cin = fields.Selection(string='',selection='_get_validation')
    motif_copie_cin = fields.Char(string='',tracking=True)

    copie_cnie = fields.Binary(string="CNIE ", attachment=True)
    copie_cnie_filename = fields.Char(string="Copie de la CNIE  filename")
    valid_copie_cnie = fields.Selection(string='', selection='_get_validation')
    motif_copie_cnie = fields.Char(string='', tracking=True)

    diplome_document = fields.Binary(string="Diplôme ", attachment=True)
    diplome_document_filename = fields.Char(string="Diplôme filename")
    valid_diplome_document = fields.Selection(string='',selection='_get_validation')
    motif_diplome_document = fields.Char(string='',tracking=True)

    engagement = fields.Binary(string="Engagement", attachment=True)
    engagement_filename = fields.Char(string="Engagement filename")
    valid_engagement = fields.Selection(string='',selection='_get_validation')
    motif_engagement = fields.Char(string='',tracking=True)

    attestation_inscription_membre = fields.Binary(string="Attestation d’inscription ", attachment=True)
    attestation_inscription_membre_filename = fields.Char(string="Attestation d’inscription  filename")
    valid_attestation_inscription_membre = fields.Selection(string='',selection='_get_validation')
    motif_attestation_inscription_membre = fields.Char(string='',tracking=True)

    """PP"""
    extrait_casier_judiciaire = fields.Binary(string=" Un extrait du casier judiciaire ou une fiche anthropométrique datant de moins de trois mois ", attachment=True)
    extrait_casier_judiciaire_filename = fields.Char(string=" Un extrait du casier judiciaire ou une fiche anthropométrique datant de moins de trois mois  filename")
    valid_extrait_casier_judiciaire = fields.Selection(string='',selection='_get_validation')
    motif_extrait_casier_judiciaire = fields.Char(string='',tracking=True)

    extrait_acte_naissance = fields.Binary(string="Un extrait d’acte de naissance datant de moins de trois mois", attachment=True)
    extrait_acte_naissance_filename = fields.Char(string="Un extrait d’acte de naissance datant de moins de trois mois  filename")
    valid_extrait_acte_naissance = fields.Selection(string='',selection='_get_validation')
    motif_extrait_acte_naissance = fields.Char(string='',tracking=True)

    photographies_recentes = fields.Binary(string="Trois photographies récentes du candidat", attachment=True)
    photographies_recentes_filename = fields.Char(string="Trois photographies récentes du candidat  filename")
    valid_photographies_recentes = fields.Selection(string='',selection='_get_validation')
    motif_photographies_recentes = fields.Char(string='',tracking=True)

    photocopie_diplome = fields.Binary(string="Une photocopie du diplôme national d’Expert-Comptable ou d’un diplôme reconnu équivalent, signé et cacheté (certifiée conforme à l’original)", attachment=True)
    photocopie_diplome_filename = fields.Char(string="Une photocopie du diplôme national d’Expert-Comptable ou d’un diplôme reconnu équivalent, signé et cacheté (certifiée conforme à l’original) filename")
    valid_photocopie_diplome = fields.Selection(string='',selection='_get_validation')
    motif_photocopie_diplome = fields.Char(string='',tracking=True)

    attestation_equivalence = fields.Binary(string="Une attestation d’équivalence au diplôme national d’expertise comptable, délivrée par le ministère d’enseignement supérieur, pour tous les diplômes étrangers", attachment=True)
    attestation_equivalence_filename = fields.Char(string="Une attestation d’équivalence au diplôme national d’expertise comptable, délivrée par le ministère d’enseignement supérieur, pour tous les diplômes étrangers  filename")
    valid_attestation_equivalence = fields.Selection(string='',selection='_get_validation')
    motif_attestation_equivalence = fields.Char(string='',tracking=True)

    fiches_annuelles = fields.Binary(string="Trois Fiches annuelles de stage, pour le diplôme français", attachment=True)
    fiches_annuelles_filename = fields.Char(string="Trois Fiches annuelles de stage, pour le diplôme français filename")
    valid_fiches_annuelles = fields.Selection(string='',selection='_get_validation')
    motif_fiches_annuelles = fields.Char(string='',tracking=True)

    attestation_fin_stage = fields.Binary(string="L'attestation de fin de stage, pour le diplôme français", attachment=True)
    attestation_fin_stage_filename = fields.Char(string="L'attestation de fin de stage, pour le diplôme français filename")
    valid_attestation_fin_stage = fields.Selection(string='',selection='_get_validation')
    motif_attestation_fin_stage = fields.Char(string='',tracking=True)

    fiche_generale_synthese = fields.Binary(string="La fiche générale de synthèse, pour le diplôme français", attachment=True)
    fiche_generale_synthese_filename = fields.Char(string="La fiche générale de synthèse, pour le diplôme français filename")
    valid_fiche_generale_synthese = fields.Selection(string='',selection='_get_validation')
    motif_fiche_generale_synthese = fields.Char(string='',tracking=True)

    fiche_annuelle = fields.Binary(string="La fiche annuelle de 200 heures d’audit pour les diplômes étrangers", attachment=True)
    fiche_annuelle_filename = fields.Char(string="La fiche annuelle de 200 heures d’audit pour les diplômes étrangers filename")
    valid_fiche_annuelle = fields.Selection(string='',selection='_get_validation')
    motif_fiche_annuelle = fields.Char(string='',tracking=True)

    copie_convention = fields.Binary(string="Une copie de la convention de réciprocité prévue à l’article 20 de la loi 15/89 pour les étrangers", attachment=True)
    copie_convention_filename = fields.Char(string="Une copie de la convention de réciprocité prévue à l’article 20 de la loi 15/89 pour les étrangers filename")
    valid_copie_convention = fields.Selection(string='',selection='_get_validation')
    motif_copie_convention = fields.Char(string='',tracking=True)

    copie_bo_jal = fields.Binary(
        string="Une copie du BO et du JAL",
        attachment=True)
    copie_bo_jal_filename = fields.Char(
        string="Une copie du BO et du JAL")
    questionnaire = fields.Binary(string="Questionnaire dûment rempli, daté et signé")
    questionnaire_filename = fields.Char(string="Nom du fichier Questionnaire")
    engagement_prise_en_charge = fields.Binary(string="Engagement de prise en charge du membre salarié")
    engagement_prise_en_charge_filename = fields.Char(string="Nom du fichier Engagement")
    certificat_residence = fields.Binary(string="Un certificat de résidence et éventuellement les justificatifs de paiement d’impôts au Maroc, pour les candidats étrangers", attachment=True)
    certificat_residence_filename = fields.Char(string="Un certificat de résidence et éventuellement les justificatifs de paiement d’impôts au Maroc, pour les candidats étrangers filename")
    valid_certificat_residence = fields.Selection(string='',selection='_get_validation')
    motif_certificat_residence = fields.Char(string='',tracking=True)

    demande_inscription_societe = fields.Binary(string="Lettre de demande d’inscription à l’Ordre, cachetée et signée par la société", attachment=True)
    demande_inscription_societe_filename = fields.Char(string="Lettre de demande d’inscription à l’Ordre, cachetée et signée par la société filename")
    valid_demande_inscription_societe = fields.Selection(string='',selection='_get_validation')
    motif_demande_inscription_societe = fields.Char(string='',tracking=True)

    demande_inscription_salarie = fields.Binary(string="Lettre de demande d’inscription à l’Ordre, daté et signée par le salarié", attachment=True)
    demande_inscription_salarie_filename = fields.Char(string="Lettre de demande d’inscription à l’Ordre, daté et signée par le salarié filename")
    valid_demande_inscription_salarie = fields.Selection(string='',selection='_get_validation')
    motif_demande_inscription_salarie = fields.Char(string='',tracking=True)

    avenant_contrat_travail = fields.Binary(string="Avenant au contrat de travail visé par le Président du Conseil National", attachment=True)
    avenant_contrat_travail_filename = fields.Char(string="Avenant au contrat de travail visé par le Président du Conseil National filename")
    valid_avenant_contrat_travail = fields.Selection(string='',selection='_get_validation')
    motif_avenant_contrat_travail = fields.Char(string='',tracking=True)

    copie_contrat_bail = fields.Binary(string="Copie du Contrat de bail du cabinet (certifié conforme à l’original)", attachment=True)
    copie_contrat_bail_filename = fields.Char(string="Copie du Contrat de bail du cabinet (certifié conforme à l’original) filename")
    valid_copie_contrat_bail = fields.Selection(string='',selection='_get_validation')
    motif_copie_contrat_bail = fields.Char(string='',tracking=True)


    date_initial_croec = fields.Date(string="Date d’arrivée")
    date_final_croec = fields.Date(string="Date fin de traitement")
    reserve_croec = fields.Char(string="Réserve CROEC")

    date_initial_member_elu = fields.Date(string="Date de transmission")
    date_final_member_elu = fields.Date(string="Date fin de traitement")
    reserve_member_elu = fields.Char(string="Réserve de la commission réglementation et déontologie")

    date_initial_secretaire_general = fields.Date(string="Date de transmission")
    date_final_secretaire_general = fields.Date(string="Date fin de traitement")
    reserve_secretaire_general = fields.Char(string="Réserve secrétaire général")

    date_initial_president_conseil = fields.Date(string="Date de transmission")
    date_final_president_conseil = fields.Date(string="Date fin de traitement")
    reserve_president_conseil = fields.Char(string="Réserve président du CROEC")

    date_initial_conseil_national = fields.Date(string="Date de transmission")
    date_final_conseil_national = fields.Date(string="Date fin de traitement")
    reserve_conseil_national = fields.Char(string="Réserve conseil national")

    second_name = fields.Char(
        string='Prénom',
    )

    contact_type_id = fields.Many2one(
        comodel_name='res.partner.type',
        string='Contact Type',
    )

    contact_level_id = fields.Many2one(
        comodel_name='res.partner.level',
        string='Niveau',
    )

    birthday = fields.Date(
        string='Date de naissance'
    )

    place_of_birth = fields.Char(
        string='Lieu de naissance',
    )

    internship_supervisor_id = fields.Many2one(
        comodel_name='res.partner',
        string='Maître de stage',
        domain=[('is_company','=',False)],
        tracking=True
    )

    internship_controler_id = fields.Many2one(
        comodel_name='res.partner',
        string='Contrôleur de stage',
        domain=[('is_company','=',False)],
        tracking=True
    )

    iscae_certificate = fields.Binary(
        string='Attestation originale d\'inscription ISCAE',
        attachment=True
    )

    iscae_certificate_filename = fields.Char(
        string='Attestation ISCAE Filename',
    )

    work_certificate = fields.Binary(
        string='Attestation originale de travail',
        attachment=True
    )

    work_certificate_filename = fields.Char(
        string='Attestation De Travail Filename',
    )

    anthropometric_profile = fields.Binary(
        string='Casier judiciaire ou Fiche anthropométrique',
        attachment=True
    )

    anthropometric_profile_filename = fields.Char(
        string='Fiche Anthropométrique Filename',
    )

    inscription_manuscrite = fields.Binary(
        string='Demande d’inscription manuscrite ',
        attachment=True
    )

    inscription_manuscrite_filename = fields.Char(
        string='Demande d’inscription manuscrite  Filename',
    )

    valid_inscription_manuscrite = fields.Selection(
        string='',
        selection='_get_validation'
    )

    motif_inscription_manuscrite = fields.Char(
        string='',
        tracking=True
    )

    attestation_cnss = fields.Binary(
        string=u'Attestation de déclaration des salaires CNSS',
        attachment=True
    )

    attestation_cnss_filename = fields.Char(
        string=u'Attestation de déclaration des salaires CNSS Filename',
    )

    valid_attestation_cnss = fields.Selection(
        string='',
        selection='_get_validation'
    )

    motif_attestation_cnss = fields.Char(
        string='',
        tracking=True
    )

    attestation_prise_en_charge_maitre = fields.Binary(
        string=u'Attestation de prise en charge par un maître de stage',
        attachment=True
    )

    attestation_prise_en_charge_maitre_filename = fields.Char(
        string=u'Attestation de prise en charge par un maître de stage Filename',
    )


    valid_attestation_prise_en_charge_maitre = fields.Selection(
        string='',
        selection='_get_validation'
    )

    motif_attestation_prise_en_charge_maitre = fields.Char(
        string='',
        tracking=True
    )

    attestation_prise_en_charge_commissaire_compte = fields.Binary(
        string='Attestation de prise en charge par le commissaire aux comptes',
        attachment=True
    )

    attestation_prise_en_charge_commissaire_compte_filename = fields.Char(
        string='Attestation de prise en charge par le commissaire aux comptes Filename',
    )

    valid_attestation_prise_en_charge_commissaire_compte = fields.Selection(
        string='',
        selection='_get_validation'
    )

    motif_attestation_prise_en_charge_commissaire_compte = fields.Char(
        string='',
        tracking=True
    )

    pv = fields.Binary(
        string='PV de nomination de Commissaire Aux Comptes',
        attachment=True
    )

    pv_filename = fields.Char(
        string='PV de nomination de Commissaire Aux Comptes Filename',
    )

    valid_pv = fields.Selection(
        string='',
        selection='_get_validation'
    )

    motif_pv = fields.Char(
        string='',
        tracking=True
    )

    cin = fields.Binary(
        string='Photocopie légalisée de la CIN',
        attachment=True
    )

    cin_filename = fields.Char(
        string='Photocopie légalisée de la CIN Filename',
    )

    valid_cin = fields.Selection(
        string='',
        selection='_get_validation'
    )

    motif_cin = fields.Char(
        string='',
        tracking=True
    )

    photo = fields.Binary(
        string='Photo',
        attachment=True
    )

    photo_filename = fields.Char(
        string='Photo Filename',
    )

    valid_photo = fields.Selection(
        string='',
        selection='_get_validation'
    )

    motif_photo = fields.Char(
        string='',
        tracking=True
    )

    office_id = fields.Many2one(
        comodel_name='res.partner',
        string='Cabinet',
    )

    other_information = fields.Text(
        string='Other Informations',
    )
    autres_fichiers_ids = fields.One2many('res.partner.file', 'partner_id', string="Autres fichiers")
    status = fields.Selection(
        string='Contact Status',
        selection='_get_status',
        default='draft',
        tracking=True
    )

    valid_iscae_certificate = fields.Selection(
        string='',
        selection='_get_validation'
    )

    motif_iscae_certificate = fields.Char(
        string='',
        tracking=True
    )

    valid_work_certificate = fields.Selection(
        string='',
        selection='_get_validation'
    )

    motif_work_certificate = fields.Char(
        string='',
        tracking=True
    )

    valid_anthropometric_profile = fields.Selection(
        string='',
        selection='_get_validation'
    )

    motif_anthropometric_profile = fields.Char(
        string='',
        tracking=True
    )

    valid_other_document = fields.Selection(
        string='',
        selection='_get_validation'
    )

    motif_other_document = fields.Char(
        string='',
        tracking=True
    )

    has_no_internship = fields.Boolean(
        string='Je cherche un stage',
    )

    resume = fields.Binary(
        string='CV PDF',
    )
    lettre_demande_inscription = fields.Binary("Lettre de demande d'inscription")
    statuts_mis_a_jour = fields.Binary("Statuts mis à jour")
    session_link = fields.Char(
        string='Questionnaire',
        compute='_compute_session_link'
    )

    survey_input_id = fields.Many2one(
        comodel_name='survey.user_input',
        string='CV',
        readonly=True,
    )

    contract = fields.Binary(
        string='Contrat de stage',
    )

    contract_filename = fields.Char(
        string='Contrat Filename',
    )

    cregionalp_id = fields.Many2one(
        comodel_name='operating.unit',
        string='CRégionalP',
    )

    cregionalcourant_id = fields.Many2one(
        comodel_name='operating.unit',
        string='CRégionalcourant',
    )

    conseil_regional_id = fields.Many2one(
        comodel_name='operating.unit',
        string='Conseil régional',
    )

    code = fields.Char(
        string='Code',
        readonly=True,
        copy=False,
        default='New'
    )

    start_date = fields.Date(
        string='Date de début du stage',
        compute='_compute_get_start_date',
        store=True
    )

    derogation = fields.Boolean(
        string='Dérogation'
    )

    start_derogation_date = fields.Date(
        string='Date de début du stage dérogatoire'
    )

    decision_commission = fields.Binary(
        string='Décision commission',
        attachment=True
    )

    decision_commission_filename = fields.Char(
        string='Décision commission Filename',
    )

    contract_date = fields.Date(
        string='Date de contrat du stage'
    )

    depot_date = fields.Date(
        string='Date de dépôt du dossier'
    )

    date_integration = fields.Date(
        string="Date d'intégration au cycle"
    )

    res_school_year_id = fields.Many2one(
        comodel_name = 'res.school.year',
        string = "Année scolaire"
    )

    saved_flag = fields.Boolean(
        string='Already saved?',
        default=False
    )

    department_id = fields.Many2one(
        comodel_name='hr.department',
        string='Etablissement de formation'
    )

    motif_reject = fields.Char(string="Motif de rejet")
    country = fields.Many2one(comodel_name='res.country', string='Pays')
    #hours = fields.Selection(string="200 heures", selection='_get_options')

    contact_registration_mode = fields.Selection(
        string="Mode d'inscription",
        selection=[
            ('pm', 'Personne Morale'), 
            ('pp', 'Personne Physique'), 
        ]
    )
    contact_registration_type = fields.Selection(
        string="Type d'inscription",
        selection=[
            # Personne physique
            ('physique_individuel', 'Inscription d\'une personne physique à titre individuel'),
            ('physique_salarie', 'Inscription d\'une personne physique en tant que salarié d\'un cabinet inscrit'),
            ('physique_associe', 'Inscription d\'une personne physique en tant que associé d\'un cabinet inscrit'),
            # Personne morale
            ('moraleyes_physiqueyes', 'Inscription d\'une personne morale et d\'une personne physique'),
            ('moraleyes_physiqueno', 'Inscription d\'une personne morale nouvelle par une personne physique déjà inscrite'),
        ]
    )

    # ------------------------------------------------------------------------
    # METHODS
    # ------------------------------------------------------------------------
    pv_cn = fields.Binary(
        string="PV du Conseil National",
        help="Document obligatoire pour confirmer l'inscription au niveau du Conseil National"
    )
    pv_cn_filename = fields.Char(
        string="Nom du fichier PV CN"
    )
    valid_pv_cn = fields.Selection([
        ('yes', 'Oui'),
        ('no', 'Non')
    ], string="PV CN valide", default='yes')

    motif_pv_cn = fields.Text(
        string="Motif de refus PV CN",
        help="Préciser le motif de refus du PV du Conseil National"
    )
    cheque_droit_entree = fields.Binary("Chèque droit d'entrée")
    montant_droit_entree = fields.Selection([
        ('4000', '4000,00 DH (Casablanca)'),
        ('3000', '3000,00 DH (Hors Casablanca)')
    ], string="Montant droit d'entrée")
    
    # Champ pour le statut d'inscription (si ce n'est pas déjà défini)
   # status_register = fields.Selection([
    #    ('draft', 'Brouillon'),
     #   ('submitted', 'Soumis'),
      #  ('in_progress_conseil_national', 'En cours - Conseil National'),
       # ('validated', 'Validé'),
        #('refused', 'Refusé'),
    #], string="Statut d'inscription", default='draft')

    @api.depends('pv_cn')
    def _compute_pv_cn_status(self):
        """Calculer le statut du PV CN"""
        for record in self:
            if record.pv_cn:
                record.pv_cn_status = 'uploaded'
            else:
                record.pv_cn_status = 'missing'

    pv_cn_status = fields.Selection([
        ('missing', 'Manquant'),
        ('uploaded', 'Téléchargé'),
        ('validated', 'Validé'),
        ('refused', 'Refusé')
    ], string="Statut PV CN", compute='_compute_pv_cn_status', store=True)

    @api.constrains('status_register', 'pv_cn')
    def _check_pv_cn_required(self):
        """Vérifier que le PV CN est obligatoire pour l'étape Conseil National"""
        for record in self:
            if record.status_register == 'in_progress_conseil_national' and not record.pv_cn:
                raise models.ValidationError(
                    "Le PV du Conseil National est obligatoire pour confirmer l'inscription."
                )
    @api.model
    def _get_formes_juridiques(self):
        return [
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
    
    @api.model
    def _get_options(self):
        return [
            ('yes', _("Oui")),
            ('no', _("Non"))
        ]

    def _check_document(self, document=''):
        print (len(self.env['reject.line'].search([('partner_id', '=', self.id),('document', '=', document)])))
        return True if len(self.env['reject.line'].search([('partner_id', '=', self.id),('document', '=', document)])) >= 1 else False

    # @api.depends('name', 'second_name')
    #def _get_display_name(self):
        #  for record in self:
        #  record_name = str(record.name) if record.name else ''
        #  second_name = record.second_name if record.second_name else ''
    #   record.display_name = record_name + ' ' + second_name

    @api.depends('name', 'second_name')  # Add other dependencies if needed
    def _compute_display_name(self):
        for record in self:
            record.display_name = f"{record.name or ''} {record.second_name or ''}"

    @api.depends('status_register')
    def _get_status_register_value(self):
        for record in self:
            record.step = record.status_register

    @api.onchange('has_no_internship')
    def _onchange_has_no_internship(self):
        if self.has_no_internship == False:
            self.resume = False


    @api.onchange('internship_supervisor_id','internship_controler_id')
    def _onchange_internship_supervisor(self):
        if self.internship_supervisor_id or self.internship_controler_id:
            if self.internship_supervisor_id==self.internship_controler_id:
                raise ValidationError(_('CS ne peut pas être un MS en même temps'))


    @api.onchange('internship_supervisor_id')
    def _onchange_internship_supervisor_id(self):
        if self.internship_supervisor_id:
                self.cregionalp_id = self.internship_supervisor_id.cregionalcourant_id.id

    def print_transmission_letter(self):
        return self.env.ref('internship_management_module.internship_transmission_letter_report').report_action(self)

    def print_notification_felicitation(self):
        return self.env.ref('internship_management_module.internship_notification_felicitation_report').report_action(self)

    def print_receipt(self):
        return self.env.ref('internship_management_module.internship_receipt_report').report_action(self)

    def print_recu_depot_physique(self):
        return self.env.ref('internship_management_module.internship_recu_depot_physique_report').report_action(self)

    @api.model
    def _get_validation(self):
        return [
            ('yes', _('Validé')),
            ('no', _('Rejeté')),
        ]

    # ------------------------------------------------------------------------
    # METHODS
    # ------------------------------------------------------------------------

    def _send_mails_request_registration(self):
        email = self.env.ref('base.user_admin').email
        base_url = request.httprequest.url_root
        if base_url and base_url[-1:] != '/':
            base_url += '/'
        db = self._cr.dbname
        url = "{}web?db={}#id={}&view_type=form&model={}".format(base_url, db, self.id, 'res.partner')
        request_registration_ec_template = self.env.ref('internship_management_module.email_template_demande_registration_ec')
        request_registration_admin_template = self.env.ref('internship_management_module.email_template_demande_registration_admin')
        request_registration_ec_template.with_context(email_to=self.email,email_from=email).send_mail(self.id,force_send=True)
        request_registration_admin_template.with_context(url=url,email_from=email).send_mail(self.id,force_send=True)

    def button_create_portal_access(self):
        group_portal = self.env.ref('base.group_portal')
        letters = string.ascii_lowercase
        random_password = ''.join(random.choice(letters) for i in range(8))
        self.env['res.users'].with_context(no_reset_password=True).create({'name' : self.name,
                                      'login': self.email,
                                      'partner_id': self.id,
                                      'password' : random_password,
                                      'active': True,
                                      'groups_id': [(4, group_portal.id)]})
        register_template = self.env.ref('internship_management_module.email_template_notification_create_user_registration')
        base_url = request.httprequest.url_root
        if base_url and base_url[-1:] != '/':
            base_url += '/'
        db = self._cr.dbname
        url = "{}registration".format(base_url)
        email = self.env.ref('base.user_admin').email
        register_template.with_context(url=url,email_from=email,login=self.email,password=random_password).send_mail(self.id,force_send=True)
        _logger.error(f"URL : {url}")
        _logger.error(f"Login : {self.email}")
        _logger.error(f"Password : {random_password}")
        return self.write({'status_register' : 'account_created'})


    def button_in_progress(self):
        self.write({
                'status_register':'in_progress',
                'date_initial_croec': fields.Date.today()
            })
        base_url = request.httprequest.url_root
        if base_url and base_url[-1:] != '/':
            base_url += '/'
        db = self._cr.dbname
        url = "{}web?db={}#id={}&view_type=form&model={}".format(base_url, db, self.id, 'res.partner')

        template = self.env.ref('internship_management_module.email_template_registration_submit')
        email = self.env.ref('base.user_admin').email
        template.with_context(url=url,email_from=email).send_mail(self.id,force_send=True)

    def button_validate_croec(self):
        if self.valid_lettre_demande_inscription=='no' or\
            self.valid_declaration_sur_honneur=='no' or\
            self.valid_actes_modificatifs=='no' or\
            self.valid_copie_bo_jal=='no' or\
            self.valid_actes_cession=='no' or\
            self.valid_statuts=='no' or\
            self.valid_copie_conforme_contrat=='no' or\
            self.valid_modele_7=='no' or\
            self.valid_attestation_radiation=='no' or\
            self.valid_attestation_assurance=='no' or\
            self.valid_attestation_inscription=='no' or\
            self.valid_bulletin_notification=='no' or\
            self.valid_contrat_travail=='no' or\
            self.valid_engagement=='no' or\
            self.valid_attestation_inscription_membre=='no' or\
            self.valid_extrait_casier_judiciaire=='no' or\
            self.valid_extrait_acte_naissance=='no' or\
            self.valid_photographies_recentes=='no' or\
            self.valid_photocopie_diplome=='no' or\
            self.valid_attestation_equivalence=='no' or\
            self.valid_fiches_annuelles=='no' or\
            self.valid_attestation_fin_stage=='no' or\
            self.valid_fiche_generale_synthese=='no' or\
            self.valid_fiche_annuelle=='no' or\
            self.valid_copie_convention=='no' or\
            self.valid_certificat_residence=='no' or\
            self.valid_demande_inscription_societe=='no' or\
            self.valid_demande_inscription_salarie=='no' or\
            self.valid_avenant_contrat_travail=='no' or\
            self.valid_copie_contrat_bail=='no':
                raise ValidationError(_('Merci de valider tous les documents avant de procéder à la validation du dossier'))
        template = self.env.ref('internship_management_module.email_template_validation_dossier_registration')
        email = self.env.ref('base.user_admin').email
        template.with_context(email_from=email).send_mail(self.id,force_send=True)
        self.write({
                'status_register':'in_progress_to_depose'
        })

    def button_deposed_croec(self):
        users = self.env.ref('internship_management_module.group_member_elu').users
        if not users:
            raise ValidationError(_("Aucun utilisateur n'a le profil 'Membre élu'"))
        email_to = users[0].email
        email = self.env.ref('base.user_admin').email
        base_url = request.httprequest.url_root
        if base_url and base_url[-1:] != '/':
            base_url += '/'
        db = self._cr.dbname
        url = "{}web?db={}#id={}&view_type=form&model={}".format(base_url, db, self.id, 'res.partner')
        template = self.env.ref('internship_management_module.email_template_validation_croec')
        template.with_context(url=url,email_to=email_to,email_from=email).send_mail(self.id,force_send=True)
        self.write({
                'status_register':'in_progress_member_elu',
                'date_final_croec': fields.Date.today(),
                'date_initial_member_elu': fields.Date.today()
            })

    def button_reserve_registration(self):
        return {
            'name':_("Réserve"),
            'view_mode': 'form',
            'res_model': 'res.partner.registration.reserve',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {
                'default_partner_id': self.id
            }
        }

    def button_unfavorable_registration(self):
        ## Not called
        return {
            'name':_("Avis défavorable"),
            'view_mode': 'form',
            'res_model': 'res.partner.registration.unfavorable',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'domain': '[]',
            'context': {
                'default_partner_id': self.id
            }
        }

    def button_validate_member_elu(self):
        users = self.env.ref('internship_management_module.group_secretaire_general').users
        if not users:
            raise ValidationError(_("Aucun utilisateur n'a le profil 'Secrétaire général'"))
        email_to = users[0].email
        email = self.env.ref('base.user_admin').email
        base_url = request.httprequest.url_root
        if base_url and base_url[-1:] != '/':
            base_url += '/'
        db = self._cr.dbname
        url = "{}web?db={}#id={}&view_type=form&model={}".format(base_url, db, self.id, 'res.partner')
        template = self.env.ref('internship_management_module.email_template_validation_membre_elu')
        template.with_context(url=url,email_to=email_to,email_from=email).send_mail(self.id,force_send=True)
        self.write({
                'status_register':'in_progress_secretaire_general',
                'date_final_member_elu': fields.Date.today(),
                'date_initial_secretaire_general': fields.Date.today(),
                'reserve_member_elu' : 'Validé'
            })


    def button_validate_secretaire_general(self):
        users = self.env.ref('internship_management_module.group_president_croec').users
        if not users:
            raise ValidationError(_("Aucun utilisateur n'a le profil 'Président du CROEC'"))
        email_to = users[0].email
        email = self.env.ref('base.user_admin').email
        base_url = request.httprequest.url_root
        if base_url and base_url[-1:] != '/':
            base_url += '/'
        db = self._cr.dbname
        url = "{}web?db={}#id={}&view_type=form&model={}".format(base_url, db, self.id, 'res.partner')
        template = self.env.ref('internship_management_module.email_template_validation_secretaire_general')
        template.with_context(url=url,email_to=email_to,email_from=email).send_mail(self.id,force_send=True)
        self.write({
                'status_register':'in_progress_president_conseil',
                'date_final_secretaire_general': fields.Date.today(),
                'date_initial_president_conseil': fields.Date.today(),
                'reserve_secretaire_general' : 'Validé'
            })

    def button_validate_president_conseil(self):
        users = self.env.ref('internship_management_module.group_conseil_national').users
        if not users:
            raise ValidationError(_("Aucun utilisateur n'a le profil 'Conseil national'"))
        email_to = users[0].email
        email = self.env.ref('base.user_admin').email
        base_url = request.httprequest.url_root
        if base_url and base_url[-1:] != '/':
            base_url += '/'
        db = self._cr.dbname
        url = "{}web?db={}#id={}&view_type=form&model={}".format(base_url, db, self.id, 'res.partner')
        template = self.env.ref('internship_management_module.email_template_validation_president_conseil')
        template.with_context(url=url,email_to=email_to,email_from=email).send_mail(self.id,force_send=True)
        self.write({
                'status_register':'in_progress_conseil_national',
                'date_final_president_conseil': fields.Date.today(),
                'date_initial_conseil_national': fields.Date.today(),
                'reserve_president_conseil' : 'Validé'
            })

    def button_confirm(self):
        if self.code == 'New' and\
            self.contact_type_id.code=='TEC' and\
            self.conseil_regional:
            self.write({
                'code' : self.env['ir.sequence'].next_by_code('ec.sequence')+ '/' + self.conseil_regional.code or '/'
            })
        contact_type_id = request.env['res.partner.type'].sudo().search([('code', '=', 'EC')], limit=1)
        self.write({
                'status_register':'registred',
                'date_final_conseil_national': fields.Date.today(),
                'reserve_conseil_national' : 'Validé',
                'contact_type_id': contact_type_id.id if contact_type_id else False,
                'contact_type': contact_type_id.id if contact_type_id else False,
            })

    def button_reject(self):
        return {
            'name':_("Rejet"),
            'view_mode': 'form',
            'res_model': 'res.partner.reject',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {
                'default_partner_id': self.id
            }
        }

    @api.model
    def _get_registration_mode(self):
        return [
            ('pm', _('Personne morale')),
            ('pp1', _('Personne physique à titre individuel')),
            ('pp2', _("Personne physique exerçant en société")),
            ('pp3', _('Personne physique en tant que salarié')),
            ('pp4', _('Personne physique exerçant en tant qu\'associé d\'un cabinet inscrit'))
        ]

    @api.model
    def _get_status_register(self):
        return [
            ('draft', _("Demande d'inscription")),
            ('account_created', _("Compte créé")),
            ('in_progress', _('En cours de traitement CROEC (Dépôt électronique)')),
            ('in_progress_to_depose', _('En cours de traitement CROEC (Dépôt physique)')),
            ('in_progress_member_elu', _('Commission réglementation et déontologie')),
            ('in_progress_secretaire_general', _('Secrétaire général')),
            ('in_progress_president_conseil', _('Président du conseil')),
            ('in_progress_conseil_national', _('Conseil national')),
            ('registred', _('Inscrit')),
            ('rejected', _('Rejeté'))
        ]

    def write(self, vals):
        for rec in self:
            old_status = rec.status_register

        result = super().write(vals)

        for rec in self:
            new_status = rec.status_register
            if vals.get('status_register') == 'in_progress_to_depose' and old_status != new_status:
                template = self.env.ref('internship_management_module.email_template_notify_prepare_physical')
                if template and rec.email:
                    template.send_mail(rec.id, force_send=True)

        return result
    @api.model
    def _get_status(self):
        return [
            ('draft', _('Dossier en cours')),
            ('submitted', _('Soumis')),
            ('completed', _('Dossier complet')),
            ('incompleted', _('Dossier incomplet')),
            ('drop_off', _('Déposé')),
            ('signed_contract', _('Contrat signé'))
        ]

    def button_submit(self):
        error = False
        msg = 'Merci de compléter les documents suivants: \n'
        if not self.inscription_manuscrite:
            error = True
            msg += '* Demande d’inscription manuscrite \n'
        if not self.iscae_certificate:
            error = True
            msg += '* Attestation originale d\'inscription ISCAE \n'
        if not self.work_certificate and (not self.attestation_prise_en_charge_commissaire_compte and not self.pv) :
            error = True
            msg += '* Attestation originale de travail ou bien Attestation de prise en charge par le commissaire aux comptes et PV de nomination de Commissaire Aux Comptes \n'
        if not self.attestation_cnss:
            error = True
            msg += '* Attestation de déclaration des salaires CNSS \n'
        if not self.attestation_prise_en_charge_maitre:
            error = True
            msg += '* Attestation de prise en charge par un maître de stage \n'
        if not self.anthropometric_profile:
            error = True
            msg += '* Casier judiciaire ou Fiche anthropométrique \n'
        if not self.cin:
            error = True
            msg += '* Photocopie légalisée de la CIN \n'
        if not self.photo:
            error = True
            msg += '* Photo \n'

        if error:
            self.write({
                'saved_flag': False
            })
            raise ValidationError(msg)
        manager_template = self.env.ref('internship_management_module.email_template_notification_submit_manager')
        internship_template = self.env.ref('internship_management_module.email_template_notification_submit_internship')
        base_url = request.httprequest.url_root
        if base_url and base_url[-1:] != '/':
            base_url += '/'
        db = self._cr.dbname
        url = "{}web?db={}#id={}&view_type=form&model={}".format(base_url, db, self.id, 'res.partner')
        email = 'stage@oec-casablanca.ma'
        self.write({
                'status':'submitted'
            })
        #try:
        manager_template.with_context(url=url,email_to=email,email_from=email).send_mail(self.id,force_send=True)
        internship_template.with_context(url=url,email_from=email).send_mail(self.id,force_send=True)
        #except Exception as exp:
            #self.env.cr.rollback()
            #_logger.error('Failed to Send mail of Notification')
            #_logger.error(str(exp))

    def button_completed(self):
        internship_template = self.env.ref('internship_management_module.email_template_notification_completed_internship')
        base_url = request.httprequest.url_root
        if self.valid_inscription_manuscrite!='yes' or\
            self.valid_iscae_certificate!='yes' or\
            self.valid_work_certificate!='yes' or\
            self.valid_attestation_cnss!='yes' or\
            self.valid_attestation_prise_en_charge_maitre!='yes' or\
            self.valid_attestation_prise_en_charge_commissaire_compte!='yes' or\
            self.valid_pv!='yes' or\
            self.valid_anthropometric_profile!='yes' or\
            self.valid_cin!='yes' or\
            self.valid_photo!='yes':
            raise ValidationError(_('Merci de valider tous les documents avant de procéder à la validation du dossier'))
        if base_url and base_url[-1:] != '/':
            base_url += '/'
        db = self._cr.dbname
        url = "{}web?db={}#id={}&view_type=form&model={}".format(base_url, db, self.id, 'res.partner')
        email = 'stage@oec-casablanca.ma'
        if self.code == 'New' and\
            self.contact_type_id.code=='ST' and\
            self.cregionalp_id and\
            self.cregionalcourant_id:
            self.write({
                'code' : self.env['ir.sequence'].next_by_code('internship.sequence')+ '/' + self.cregionalp_id.code + '/'+  self.cregionalcourant_id.code or '/'
            })
        try:
            internship_template.with_context(url=url,email_from=email).send_mail(self.id,force_send=True)
            self.write({
                'status':'completed'
            })
        except Exception as exp:
            self.env.cr.rollback()
            _logger.error('Failed to Send mail of Notification')
            _logger.error(str(exp))


    def _send_email_reserve(self):
        internship_template = self.env.ref('internship_management_module.email_template_notification_incompleted_registration')
        email = self.env.ref('base.user_admin').email
        msg_lettre_demande_inscription = msg_declaration_sur_honneur = msg_actes_modificatifs = msg_copie_bo_jal = \
        msg_actes_cession = msg_statuts = msg_copie_conforme_contrat = msg_modele_7 = msg_attestation_radiation = \
        msg_attestation_assurance = msg_attestation_inscription = msg_bulletin_notification = msg_copie_cheque = \
        msg_contrat_travail = msg_engagement = msg_attestation_inscription_membre = msg_extrait_casier_judiciaire = \
        msg_extrait_acte_naissance = msg_photographies_recentes = msg_photocopie_diplome = msg_attestation_equivalence = \
        msg_fiches_annuelles = msg_attestation_fin_stage = msg_fiche_generale_synthese = msg_fiche_annuelle = \
        msg_copie_convention = msg_certificat_residence = msg_demande_inscription_societe = msg_demande_inscription_salarie = \
        msg_avenant_contrat_travail = msg_copie_contrat_bail = ''
        if self.valid_lettre_demande_inscription=='no':
            msg_lettre_demande_inscription = ('Lettre de demande d’inscription à lordre : %s')% (self.motif_lettre_demande_inscription)

        if self.valid_declaration_sur_honneur=='no':
            msg_declaration_sur_honneur = ('Déclaration sur l’honneur :  %s')% (self.motif_declaration_sur_honneur)

        if self.valid_actes_modificatifs=='no':
            msg_actes_modificatifs = ('Actes modificatifs : %s')% (self.motif_actes_modificatifs)

        if self.valid_copie_bo_jal=='no':
            msg_copie_bo_jal = ('Copie du BO et du JAL :  %s')% (self.motif_copie_bo_jal)

        if self.valid_actes_cession=='no':
            msg_actes_cession = ('Actes de cession de parts sociales ou de transferts d’actions :  %s')% (self.motif_actes_cession)

        if self.valid_statuts=='no':
            msg_statuts = ('Statuts mis à jour : %s')% (self.motif_statuts)

        if self.valid_copie_conforme_contrat=='no':
            msg_copie_conforme_contrat = ('Copie certifiée conforme du contrat de bail :  %s')% (self.motif_copie_conforme_contrat)

        if self.valid_modele_7=='no':
            msg_modele_7 = ('Certificat modèle 7 du Registre du Commerce : %s')% (self.motif_modele_7)

        if self.valid_attestation_radiation=='no':
            msg_attestation_radiation = ('Attestation de radiation : %s')% (self.motif_attestation_radiation)

        if self.valid_attestation_assurance=='no':
            msg_attestation_assurance = ('Attestation d’assurance Responsabilité Civile : %s')% (self.motif_attestation_assurance)

        if self.valid_attestation_inscription=='no':
            msg_attestation_inscription = ("Attestation d'inscription à la Taxe Professionnelle : %s")% (self.motif_attestation_inscription)

        if self.valid_bulletin_notification=='no':
            msg_bulletin_notification = ("Bulletin de notification de l’Identifiant Fiscal %s")% (self.motif_bulletin_notification)


        if self.valid_contrat_travail=='no':
            msg_contrat_travail = ('Contrat de travail : %s')% (self.motif_contrat_travail)

        if self.valid_engagement=='no':
            msg_engagement = ('Engagement : %s')% (self.motif_engagement)

        if self.valid_attestation_inscription_membre=='no':
            msg_attestation_inscription_membre = ("Attestation d’inscription : %s")% (self.motif_attestation_inscription_membre)

        if self.valid_extrait_casier_judiciaire=='no':
            msg_extrait_casier_judiciaire = ('Un extrait du casier judiciaire ou une fiche anthropométrique datant de moins de trois mois : %s')% (self.motif_extrait_casier_judiciaire)

        if self.valid_extrait_acte_naissance=='no':
            msg_extrait_acte_naissance = ('Un extrait d’acte de naissance datant de moins de trois mois :  %s')% (self.motif_extrait_acte_naissance)

        if self.valid_photographies_recentes=='no':
            msg_photographies_recentes = ('Trois photographies récentes du candidat :  %s')% (self.motif_photographies_recentes)

        if self.valid_photocopie_diplome=='no':
            msg_photocopie_diplome = ("Une photocopie du diplôme national d’Expert-Comptable ou d’un diplôme reconnu équivalent, signé et cacheté (certifiée conforme à l’original) : %s")% (self.motif_photocopie_diplome)

        if self.valid_attestation_equivalence=='no':
            msg_attestation_equivalence = ('Une attestation d’équivalence au diplôme national d’expertise comptable, délivrée par le ministère d’enseignement supérieur, pour tous les diplômes étrangers :  %s')% (self.motif_attestation_equivalence)

        if self.valid_fiches_annuelles=='no':
            msg_fiches_annuelles = ('Trois Fiches annuelles de stage, pour le diplôme français :  %s')% (self.motif_fiches_annuelles)

        if self.valid_attestation_fin_stage=='no':
            msg_attestation_fin_stage = ("L'attestation de fin de stage, pour le diplôme français : %s")% (self.motif_attestation_fin_stage)

        if self.valid_fiche_generale_synthese=='no':
            msg_fiche_generale_synthese = ('La fiche générale de synthèse, pour le diplôme français :  %s')% (self.motif_fiche_generale_synthese)

        if self.valid_fiche_annuelle=='no':
            msg_fiche_annuelle = ('La fiche annuelle de 200 heures d’audit pour les diplômes étrangers :  %s')% (self.motif_fiche_annuelle)

        if self.valid_copie_convention=='no':
            msg_copie_convention = ("Une copie de la convention de réciprocité prévue à l’article 20 de la loi 15/89 pour les étrangers :  %s")% (self.motif_copie_convention)

        if self.valid_certificat_residence=='no':
            msg_certificat_residence = ("Un certificat de résidence et éventuellement les justificatifs de paiement d’impôts au Maroc, pour les candidats étrangers :  %s")% (self.motif_certificat_residence)

        if self.valid_demande_inscription_societe=='no':
            msg_demande_inscription_societe = ("Lettre de demande d’inscription à l’Ordre, cachetée et signée par la société : %s")% (self.motif_demande_inscription_societe)

        if self.valid_demande_inscription_salarie=='no':
            msg_demande_inscription_salarie = ("Lettre de demande d’inscription à l’Ordre, daté et signée par le salarié : %s")% (self.motif_demande_inscription_salarie)

        if self.valid_avenant_contrat_travail=='no':
            msg_avenant_contrat_travail = ("Avenant au contrat de travail visé par le Président du Conseil National :  %s")% (self.motif_avenant_contrat_travail)

        if self.valid_copie_contrat_bail=='no':
            msg_copie_contrat_bail = ('Copie du Contrat de bail du cabinet (certifié conforme à l’original) :  %s')% (self.motif_copie_contrat_bail)


        try:
            internship_template.with_context(email_from=email,
                                             msg_lettre_demande_inscription=msg_lettre_demande_inscription,
                                             msg_declaration_sur_honneur=msg_declaration_sur_honneur,
                                             msg_actes_modificatifs=msg_actes_modificatifs,
                                             msg_copie_bo_jal=msg_copie_bo_jal,
                                             msg_actes_cession=msg_actes_cession,
                                             msg_statuts=msg_statuts,
                                             msg_copie_conforme_contrat=msg_copie_conforme_contrat,
                                             msg_modele_7=msg_modele_7,
                                             msg_attestation_radiation=msg_attestation_radiation,
                                             msg_attestation_assurance=msg_attestation_assurance,
                                             msg_attestation_inscription=msg_attestation_inscription,
                                             msg_bulletin_notification=msg_bulletin_notification,
                                             msg_copie_cheque=msg_copie_cheque,
                                             msg_contrat_travail=msg_contrat_travail,
                                             msg_engagement=msg_engagement,
                                             msg_attestation_inscription_membre=msg_attestation_inscription_membre,
                                             msg_extrait_casier_judiciaire=msg_extrait_casier_judiciaire,
                                             msg_extrait_acte_naissance=msg_extrait_acte_naissance,
                                             msg_photographies_recentes=msg_photographies_recentes,
                                             msg_photocopie_diplome=msg_photocopie_diplome,
                                             msg_attestation_equivalence=msg_attestation_equivalence,
                                             msg_fiches_annuelles=msg_fiches_annuelles,
                                             msg_attestation_fin_stage=msg_attestation_fin_stage,
                                             msg_fiche_generale_synthese=msg_fiche_generale_synthese,
                                             msg_fiche_annuelle=msg_fiche_annuelle,
                                             msg_copie_convention=msg_copie_convention,
                                             msg_certificat_residence=msg_certificat_residence,
                                             msg_demande_inscription_societe=msg_demande_inscription_societe,
                                             msg_demande_inscription_salarie=msg_demande_inscription_salarie,
                                             msg_avenant_contrat_travail=msg_avenant_contrat_travail,
                                             msg_copie_contrat_bail=msg_copie_contrat_bail).send_mail(self.id,force_send=True)

        except Exception as exp:
            self.env.cr.rollback()
            _logger.error('Failed to Send mail of Notification')
            _logger.error(str(exp))

    def button_reserve(self):
        internship_template = self.env.ref('internship_management_module.email_template_notification_incompleted_internship')
        base_url = request.httprequest.url_root
        if base_url and base_url[-1:] != '/':
            base_url += '/'
        db = self._cr.dbname
        url = "{}web?db={}#id={}&view_type=form&model={}".format(base_url, db, self.id, 'res.partner')
        email = self.env.ref('base.user_admin').email
        msg_inscription = ''
        msg_iscae  = ''
        msg_work  = ''
        msg_attestation_cnss = ''
        msg_attestation_prise_en_charge_maitre = ''
        msg_attestation_prise_en_charge_commissaire_compte = ''
        msg_pv = ''
        msg_anthropometric_profile = ''
        msg_cin = ''
        msg_photo = ''
        if self.valid_inscription_manuscrite=='no':
            msg_inscription = ('Demande d’inscription manuscrite est %s')% (self.motif_inscription_manuscrite)

        if self.valid_iscae_certificate=='no':
            msg_iscae = ('Attestation ISCAE est %s')%(self.motif_iscae_certificate)

        if self.valid_work_certificate=='no':
            msg_work = ('Attestation originale de travail est %s')%(self.motif_work_certificate)

        if self.valid_attestation_cnss=='no':
            msg_attestation_cnss = ('Attestation de déclaration des salaires CNSS %s')%(self.motif_attestation_cnss)

        if self.valid_attestation_prise_en_charge_maitre=='no':
            msg_attestation_prise_en_charge_maitre = ('Attestation de prise en charge par un maître de stage %s')%(self.motif_attestation_prise_en_charge_maitre)

        if self.valid_attestation_prise_en_charge_commissaire_compte=='no':
            msg_attestation_prise_en_charge_commissaire_compte = ('Attestation de prise en charge par le commissaire aux comptes %s')%(self.motif_attestation_prise_en_charge_commissaire_compte)

        if self.valid_pv=='no':
            msg_pv = ('PV de nomination de Commissaire Aux Comptes %s')%(self.motif_pv)

        if self.valid_anthropometric_profile=='no':
            msg_anthropometric_profile = ('Casier judiciaire ou Fiche anthropométrique %s')%(self.motif_anthropometric_profile)

        if self.valid_cin=='no':
            msg_cin = ('Photocopie légalisée de la CIN %s')%(self.motif_cin)

        if self.valid_photo=='no':
            msg_photo = ('Deux photos %s')%(self.motif_photo)

        try:
            internship_template.with_context(url=url,email_from=email,msg_inscription=msg_inscription,msg_iscae=msg_iscae,msg_work=msg_work,msg_attestation_cnss=msg_attestation_cnss,
                                             msg_attestation_prise_en_charge_maitre=msg_attestation_prise_en_charge_maitre,
                                             msg_attestation_prise_en_charge_commissaire_compte=msg_attestation_prise_en_charge_commissaire_compte,
                                             msg_pv=msg_pv,
                                             msg_anthropometric_profile=msg_anthropometric_profile,
                                             msg_cin=msg_cin,
                                             msg_photo=msg_photo).send_mail(self.id,force_send=True)
            self.write({
                'status':'incompleted'
            })
        except Exception as exp:
            self.env.cr.rollback()
            _logger.error('Failed to Send mail of Notification')
            _logger.error(str(exp))

    def button_drop_off(self):
        internship_template = self.env.ref('internship_management_module.email_template_notification_drop_off_internship')
        base_url = request.httprequest.url_root
        if base_url and base_url[-1:] != '/':
            base_url += '/'
        db = self._cr.dbname
        url = "{}web?db={}#id={}&view_type=form&model={}".format(base_url, db, self.id, 'res.partner')
        email = self.env.ref('base.user_admin').email
        self.write({'depot_date': date.today().strftime('%Y-%m-%d')
                    })
        try:
            internship_template.with_context(url=url,email_from=email).send_mail(self.id,force_send=True)
            self.write({
                'status':'drop_off'
            })
        except Exception as exp:
            self.env.cr.rollback()
            _logger.error('Failed to Send mail of Notification')
            _logger.error(str(exp))

    def button_signed_contract(self):
        self.write({'status':'signed_contract'})


    @api.depends('resume')
    def _compute_session_link(self):
        for record in self:
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            related_servey = self.env['survey.survey'].search(
                [('survey_type','=','internship')],limit=1
            )
            record.session_link = werkzeug.urls.url_join(base_url, related_servey.get_start_url()) if related_servey else False

    @api.depends('contract_date', 'depot_date', 'date_integration')
    def _compute_get_start_date(self):
        for record in self:
            if record.depot_date and record.contract_date and record.date_integration:
                diff = record.depot_date - record.contract_date
                if diff.days < 90:
                    record.start_date = min(record.contract_date, record.date_integration)
                else:
                    record.start_date = min(record.depot_date - relativedelta(months=3), record.date_integration)
            else:
                record.start_date = False

    def button_print(self):
        return self.env.ref('internship_management_module.internship_livret').report_action(self)

class ResPartnerFile(models.Model):
    _name = 'res.partner.file'
    _description = 'Fichiers supplémentaires pour partenaire'

    name = fields.Char("Nom du fichier")
    datas = fields.Binary("Fichier", required=True)
    partner_id = fields.Many2one('res.partner', string="Partenaire", ondelete='cascade')
