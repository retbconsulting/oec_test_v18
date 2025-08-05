from odoo import models, api 

class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.constrains('partner_id')
    def _check_value(self):
        if self.partner_id.company_type == 'company':
            raise ValidationError("Vous ne pouvez pas créer un utilisateur pour une société")