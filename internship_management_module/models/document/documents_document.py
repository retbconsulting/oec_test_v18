# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import datetime, timedelta,date
from odoo.exceptions import ValidationError
from odoo.http import request
import logging
import werkzeug

_logger = logging.getLogger(__name__)


class RealisedWorkLine(models.Model):
    _name = 'realised.work.line'
    
    name = fields.Char(string="Nature")
    charge_horaire = fields.Float(string="Charge horaire")
    document_id = fields.Many2one(comodel_name='documents.document', string="Rapport")
    
class DocumentsDocument(models.Model):

    _inherit = 'documents.document'

    # --------------------------------------------------------------------
    # FIELDS
    # --------------------------------------------------------------------

    internship_id = fields.Many2one(
        comodel_name='res.partner',
        string='Stagiaire',
    )

    internship_supervisor_id = fields.Many2one(
        related='internship_id.internship_supervisor_id',
        string='Maître de stage',
        store=True
    )

    internship_controler_id = fields.Many2one(
        related='internship_id.internship_controler_id',
        string='Contrôleur de stage',
        store=True
    )

    signature = fields.Binary(
        string='Signature MS',
    )

    signature_cs = fields.Binary(
        string='Signature CS',
    )

    signed = fields.Selection(
        string='Signé',
        selection='_get_signed',
    )

    report_content = fields.Selection(
        string='Teneur du rapport',
        selection='_get_report_content',
    )

    internship_progress = fields.Selection(
        string='Déroulement du stage',
        selection='_get_internship_progress',
    )

    respect_internship_condition = fields.Selection(
        string='Respet des conditions de stage',
        selection='_get_respect_internship_condition',
    )

    cs_decision = fields.Selection(
        string='Décision du CS',
        selection='_get_cs_decision',
    )

    report_id = fields.Many2one(
        comodel_name='documents.document.report',
        string='Rapport',
    )

    start_stage_date = fields.Date(string="Date de démarrage du stage")
    had_difficulties_finding_ms = fields.Selection(string="Avez vous rencontré des difficultés particulières pour trouver un maître de stage?", selection='_yes_no')
    had_change_maitre_stage = fields.Selection(string="Avez-vous changé de maître de stage?", selection='_yes_no')
    had_difficulties_courses = fields.Selection(string="Avez vous trouvé des difficultés particulières pour suivre les cours à l’ISCAE?", selection='_yes_no')
    remarks_difficulties_courses = fields.Text(string="Si oui, de quel ordre?")
    had_difficulties_works = fields.Selection(string="Avez vous rencontré des difficultés pour effectuer les travaux confiés par votre maître de stage?", selection='_yes_no')
    remarks_difficulties_works = fields.Text(string="Si oui, de quel ordre?")
    remarks_deroulement_stage = fields.Text(string="Vos remarques et observations concernant le déroulement de votre stage.")
    apprciation_ms = fields.Char(string="Appréciation du maitre de stage")
    apprciation_cs = fields.Char(string="Appréciation du contrôleur de stage")
    
    realised_works_ids = fields.One2many(comodel_name="realised.work.line", inverse_name="document_id", string="Travaux réalisés")
    depot_date = fields.Date(string=u"Date dépôt")
    validation_date = fields.Date(string=u"Date de vérification")
    controle_date = fields.Date(string=u"Date du contrôle")
    
    # ------------------------------------------------------------------------
    # METHODS
    # ------------------------------------------------------------------------
    @api.model
    def _yes_no(self):
        return [
            ('yes', _('Oui')),
            ('no', _('Non')),
        ]


    @api.model
    def _get_signed(self):
        return [
            ('yes', _('Oui')),
            ('no', _('Non')),
        ]

    @api.model
    def _get_report_content(self):
        return [
            ('conforme', _('Conforme')),
            ('non_conforme', _('Non Conforme')),
        ]

    @api.model
    def _get_internship_progress(self):
        return [
            ('valide', _('Valide')),
            ('non_valide', _('Non Valide')),
        ]

    @api.model
    def _get_respect_internship_condition(self):
        return [
            ('yes', _('Oui')),
            ('no', _('Non')),
        ]

    @api.model
    def _get_cs_decision(self):
        return [
            ('valide', _('Rapport validé')),
            ('reserve', _('Validé avec réserves')),
            ('rejet', _('Rapport rejeté')),
        ]
