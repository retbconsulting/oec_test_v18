# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import datetime, timedelta,date
from odoo.exceptions import ValidationError
from odoo.http import request
import logging
import werkzeug

_logger = logging.getLogger(__name__)

class DocumentsDocumentReport(models.Model):

    _name = 'documents.document.report'
    _description = 'Rapports de stage'
    _rec_name = 'name'

    # --------------------------------------------------------------------
    # FIELDS
    # --------------------------------------------------------------------

    name = fields.Char(
        string='Name',
    )

    declenchement = fields.Char(
        string='Declenchement',
    )

    first_rappel = fields.Integer(
        string='1er rappel après',
    )

    second_rappel = fields.Integer(
        string='2ème rappel après',
    )

    third_rappel = fields.Integer(
        string='3ème rappel après',
    )