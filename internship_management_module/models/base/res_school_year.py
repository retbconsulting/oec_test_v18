# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError

class ResSchoolYear(models.Model):

    _name = 'res.school.year'
    _description = 'Niveau'
    _rec_name = 'name' 

    # --------------------------------------------------------------------
    # FIELDS
    # --------------------------------------------------------------------

    name = fields.Char(
        string='Name',
        required=True
    )
    
    start_date = fields.Date(
        string = "Date début"
    )
    
    end_date = fields.Date(
        string = "Date fin"
    )