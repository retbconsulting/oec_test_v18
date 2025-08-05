# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError

class ResPartnerType(models.Model):

    _name = 'res.partner.type'
    _description = 'Type de Contact'
    _rec_name = 'name' 

    # --------------------------------------------------------------------
    # FIELDS
    # --------------------------------------------------------------------

    name = fields.Char(
        string='Name',
    )

    code = fields.Char(
        string='Code',
    )