# -*- coding: utf-8 -*-
import random
import string
from odoo import api, fields, models, _
from datetime import datetime, timedelta,date
from odoo.exceptions import ValidationError, UserError
from odoo.http import request
import logging
import werkzeug
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):

    _inherit = 'res.users'
    
    def write(self, vals):
        User = self.env['res.users']
        if 'in_group_104' in vals:
            if len(User.sudo().search([('groups_id', '=', self.env.ref( "internship_management_module.group_conseil_national" ).id)])) !=0 and vals.get('in_group_104') == True:
                raise ValidationError(_('Un seul utilisateur devera avoir le profil Conseil National'))
            elif len(User.sudo().search([('groups_id', '=', self.env.ref( "internship_management_module.group_conseil_national" ).id)])) ==0 and vals.get('in_group_104') == True:
                self.env['profil.change'].create({'user_id': self.id, 'date':fields.Date.today(), 'profil': 'cn'})
        res = super(ResUsers, self).write(vals)
        return res



class ResGroups(models.Model):
    _inherit = 'res.groups'

    @api.model
    def _register_hook(self):
        res = super()._register_hook()

        try:
            president = self.env.ref('internship_management_module.group_president_croec')
            conseil = self.env.ref('internship_management_module.group_conseil_national')

            if conseil.id not in president.implied_ids.ids:
                president.write({'implied_ids': [(4, conseil.id)]})

        except Exception as e:
            _logger = self.env['ir.logging']
            _logger.create({
                'name': 'Group Hook Error',
                'type': 'server',
                'level': 'error',
                'message': str(e),
                'path': __file__,
                'line': 0,
                'func': '_register_hook'
            })

        return res

    