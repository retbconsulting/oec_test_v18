# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import time
import base64
from odoo.exceptions import   RedirectWarning, ValidationError
from io import StringIO,BytesIO

class OecCommittee(models.Model):
    _name = 'oec.committee'
    _description = 'Le commité'
    
    name = fields.Char(string='Nom', default='/')
    date = fields.Date(string="Date")
    partner_ids = fields.Many2many(comodel_name='res.partner', string="Demandes d'inscription")
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('in_progress', 'En cours de traitement'),
        ('done', 'Terminée'),
        ('cancel', 'Annulée')
    ], string=u'Etat', required=True, default='draft')
    pv = fields.Binary(string='PV', attachment=True)
    pv_filename = fields.Char(string='PV Filename')
    
    file_data = fields.Binary('Excel File', readonly=True, attachment=False)
    filename = fields.Char(string='Filename', size=256, readonly=True)
    
    def print_recap(self):
        
        _pfc = '26'  
        _bc = '28'
        xls_styles = {
            'xls_title': 'font: bold true, height 140;',
            'xls_title2': 'font: bold true, height 140;',
            'bold': 'font: bold true;',
            'underline': 'font: underline true;',
            'italic': 'font: italic true;',
            'fill': 'pattern: pattern solid, fore_color %s;' % _pfc,
            'fill_blue': 'pattern: pattern solid, fore_color 27;',
            'fill_grey': 'pattern: pattern solid, fore_color 22;',
            'borders_all': 'borders: left thin, right thin, top thin, bottom thin, '
                'left_colour %s, right_colour %s, top_colour %s, bottom_colour %s;' % (_bc, _bc, _bc, _bc),
            'borders_all2': 'borders: left thin, right thin, top thick, bottom thin, '
                'left_colour %s, right_colour %s, top_colour %s, bottom_colour %s;' % (_bc, _bc, _bc, _bc),
            'left': 'align: horz left;',
            'center': 'align: horz center;',
            'right': 'align: horz right;',
            'wrap': 'align: wrap true;',
            'top': 'align: vert top;',
            'ver_top': 'align: vert center;',
            'bottom': 'align: vert bottom;',
        }
        cell_format = xls_styles['xls_title'] + xls_styles['borders_all'] + xls_styles['wrap'] + xls_styles['ver_top']
        cell_body_format = xls_styles['xls_title2'] +  xls_styles['ver_top']
        cell_style_header_tab = xlwt.easyxf(cell_format + xls_styles['bold']+ xls_styles['center'] + xls_styles['fill'])
        cell_style_body_tab = xlwt.easyxf(cell_body_format)
        date_style = xlwt.easyxf('align: wrap yes', num_format_str='YYYY-MM-DD')
        datetime_style = xlwt.easyxf('align: wrap yes', num_format_str='YYYY-MM-DD HH:mm:SS')
        filename= 'Récapitulatif.xls'
        workbook= xlwt.Workbook(encoding="UTF-8")
        worksheet= workbook.add_sheet('Récapitulatif.xls')
        worksheet.write_merge(0,1,0,6,'Récapitulatif.',cell_style_header_tab)
        worksheet.write(3,0,'Nom.',cell_style_header_tab)
        worksheet.write(3,1,'Prénom.',cell_style_header_tab)
        worksheet.write(3,2,'Email.',cell_style_header_tab)
        worksheet.write(3,3,'Comment. CROEC.',cell_style_header_tab)
        worksheet.write(3,4,'Comment. Commission réglementation et déontologie',cell_style_header_tab)
        worksheet.write(3,5,'Comment. Secrétaire général',cell_style_header_tab)
        worksheet.write(3,6,'Comment. Président du CROEC',cell_style_header_tab)
        
        row=4
        for partner in self.partner_ids:
            worksheet.write(row,0,partner.name,cell_style_body_tab)
            worksheet.write(row,1,partner.second_name,cell_style_body_tab)
            worksheet.write(row,2,partner.email,cell_style_body_tab)
            worksheet.write(row,3,partner.reserve_croec,cell_style_body_tab)
            worksheet.write(row,4,partner.reserve_member_elu,cell_style_body_tab)
            worksheet.write(row,5,partner.reserve_secretaire_general,cell_style_body_tab)
            worksheet.write(row,6,partner.reserve_president_conseil,cell_style_body_tab)
            
        fp = BytesIO()
        workbook.save(fp)
        self.write({
            'file_data': base64.encodestring(fp.getvalue()),
            'filename': filename,
        })
        fp.close()
        return {
            'type': 'ir.actions.act_url',
            'url': "web/content/?model=oec.committee&id=" + str(self.id) + "&filename_field=filename&field=file_data&download=true&filename=" + filename,
            'target': 'self',
        }
         
    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code('oec.committee') or '/'
        return super(OecCommittee, self).create(vals)
    
    def action_in_progress(self):
        ### Load registred memeber
        self.filter_confirm()
        self.state = 'in_progress'
        
    def action_done(self):
        self.state = 'done'
        
    
    def filter_confirm(self):
        ResPartner = self.env['res.partner']
        partners = ResPartner.search([('contact_type', '=', 'TEC'), ('status_register', '=', 'in_progress_conseil_national')])
        self.partner_ids = [(6, 0, partners.ids)]