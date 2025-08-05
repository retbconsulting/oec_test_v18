# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError

class ResPartnerLevel(models.Model):

    _name = 'res.partner.level'
    _description = 'Niveau'
    _rec_name = 'name' 

    # --------------------------------------------------------------------
    # FIELDS
    # --------------------------------------------------------------------

    name = fields.Char(
        string='Name',
    )