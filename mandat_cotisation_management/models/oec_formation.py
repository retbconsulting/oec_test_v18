# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError

class OecFormation(models.Model):

    _name = 'oec.formation'
    _description = 'Formation'
    
    partner_id = fields.Many2one(comodel_name="res.partner", string="Expert comptable")
    year = fields.Selection(selection=[(str(num), str(num)) for num in range(2018, (datetime.now().year)+1 )], string="Année", required=True)
    oec_formation_one_ids = fields.One2many(comodel_name='oec.formation.one', inverse_name='oec_formation_id', string='Séminaires organisés par le CNOEC,CREOC,IFOEC  ou par des organismes de formation continue (1)')
    oec_formation_two_ids = fields.One2many(comodel_name='oec.formation.two', inverse_name='oec_formation_id', string="Etudes entreprises à l'Université /établissements assimilés (2)")
    oec_formation_three_ids = fields.One2many(comodel_name='oec.formation.three', inverse_name='oec_formation_id', string="Programmes d’auto Formation (3)")
    oec_formation_four_ids = fields.One2many(comodel_name='oec.formation.four', inverse_name='oec_formation_id', string="Animation des formations,conférences,colloques,réunions d'information techniques  (4)")
    oec_formation_five_ids = fields.One2many(comodel_name='oec.formation.five', inverse_name='oec_formation_id', string="Travaux techniques, travaux de publication, participation à des jurys (5)")
    total = fields.Float(compute='_get_total_hours', string='Total')
    state = fields.Selection(string="Etat", selection='_get_status', default='draft')
    
    @api.model
    def _get_status(self):
        return [
            ('draft', _("Brouillon")),
            ('confirmed', _("Confirmé"))
        ]
        
    def _get_total_hours(self):
        for formation in self:
            formation.total = sum(oec_formation_1.hours_number for oec_formation_1 in formation.oec_formation_one_ids) + \
                                sum(oec_formation_2.hours_number for oec_formation_2 in formation.oec_formation_two_ids) + \
                                sum(oec_formation_3.hours_number for oec_formation_3 in formation.oec_formation_three_ids) + \
                                sum(oec_formation_4.hours_number for oec_formation_4 in formation.oec_formation_four_ids) + \
                                sum(oec_formation_5.hours_number for oec_formation_5 in formation.oec_formation_five_ids)
        
    
    def button_confirm(self):
        self.write({'state': 'confirmed'})
        
class oecFormationOne(models.Model):
    
    _name = 'oec.formation.one'
    
    subject = fields.Char(string="Sujet")
    hours_number = fields.Float(string="Nbre d'heures")
    date = fields.Date(string='Date')
    animateur = fields.Char(string='Animateur')
    organisme = fields.Char(string='Organisme')
    city = fields.Char(string='Ville')
    oec_formation_id = fields.Many2one(comodel_name='oec.formation', string='Formation')
    
class oecFormationTwo(models.Model):
    
    _name = 'oec.formation.two'
    
    subject = fields.Char(string="Sujet")
    hours_number = fields.Float(string="Nbre d'heures")
    date = fields.Date(string='Date')
    animateur = fields.Char(string='Animateur')
    organisme = fields.Char(string='Organisme')
    city = fields.Char(string='Ville')
    oec_formation_id = fields.Many2one(comodel_name='oec.formation', string='Formation')
    
class oecFormationThree(models.Model):
    
    _name = 'oec.formation.three'
    
    subject = fields.Char(string="Sujet")
    hours_number = fields.Float(string="Nbre d'heures")
    date = fields.Date(string='Date')
    animateur = fields.Char(string='Animateur')
    organisme = fields.Char(string='Organisme')
    city = fields.Char(string='Ville')
    oec_formation_id = fields.Many2one(comodel_name='oec.formation', string='Formation')
    
class oecFormationFour(models.Model):
    
    _name = 'oec.formation.four'
    
    subject = fields.Char(string="Sujet")
    hours_number = fields.Float(string="Nbre d'heures")
    date = fields.Date(string='Date')
    animateur = fields.Char(string='Animateur')
    organisme = fields.Char(string='Organisme')
    city = fields.Char(string='Ville')
    oec_formation_id = fields.Many2one(comodel_name='oec.formation', string='Formation')
    
class oecFormationFive(models.Model):
    
    _name = 'oec.formation.five'
    
    subject = fields.Char(string="Sujet")
    hours_number = fields.Float(string="Nbre d'heures")
    date = fields.Date(string='Date')
    animateur = fields.Char(string='Animateur')
    organisme = fields.Char(string='Organisme')
    city = fields.Char(string='Ville')
    oec_formation_id = fields.Many2one(comodel_name='oec.formation', string='Formation')
