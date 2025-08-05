# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)

class SurveySurvey(models.Model):

    _inherit = 'survey.survey'

    # --------------------------------------------------------------------
    # FIELDS
    # --------------------------------------------------------------------

    survey_type = fields.Selection(
        string='Type',
        selection='_get_survey_type',
    )


    # --------------------------------------------------------------------
    # METHODS
    # --------------------------------------------------------------------

    @api.model
    def _get_survey_type(self):
        return [
            ('internship', _('Stagiares')),
            ('other', _('Autres')),
        ]

class SurveyUserInput(models.Model):

    _inherit = 'survey.user_input'


    # --------------------------------------------------------------------
    # METHODS
    # --------------------------------------------------------------------

    @api.model
    def create(self,values):
        res = super(SurveyUserInput,self).create(values)
        if res.partner_id:
        	res.partner_id.survey_input_id=res.id 
        return res