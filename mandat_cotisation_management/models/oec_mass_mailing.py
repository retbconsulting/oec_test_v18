from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime, date

class OecMailing(models.Model):
    _inherit = 'mailing.mailing'

    year = fields.Selection(
        string="Année",
        selection=list(zip(map(str, range(datetime.now().year, 2018, -1)), map(str, range(datetime.now().year, 2018, -1))))
    )
  
    open_date = fields.Date(
        string="Date d'ouverture"
    )

    due_date = fields.Date(
        string="Date d'échéance"
    )

    oec_mailing_type = fields.Selection(
        string="Appel à",
        selection=[
            ('none', 'Autre'),
            ('cotisation', 'Cotisation'),
            ('declaration', 'Déclaration'),
        ],
        default='none',
    )

    @api.onchange('year')
    def set_open_date(self):
        if self.year:
            self.open_date = date(int(self.year), 1, 1)

    def action_launch(self):
        if self.oec_mailing_type == 'none':
            return super().action_launch()
            
        recipients = self._get_recipients()
        
        if self.oec_mailing_type == 'cotisation':
            if not self.due_date:
                raise UserError("La date d'échéance est requise pour les cotisations")
            for recipient in recipients:
                vals = {
                    'year': self.year,
                    'partner_id': recipient,
                    'date_open': self.open_date,
                    'due_date': self.due_date,
                }
                self.env['oec.cotisation'].sudo().create(vals)
                
        if self.oec_mailing_type == 'declaration':
            for recipient in recipients:
                vals = {
                    'partner_id': recipient,
                    'date_start': self.open_date,
                    'date_end': self.due_date,
                }
                self.env['oec.mandat.declaration'].sudo().create(vals)
        return super().action_launch()
            
            
