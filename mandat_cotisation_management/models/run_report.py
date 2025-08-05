# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import date


class MembershipRunRapport(models.Model):
    _name = 'membership.run.report'
    _description = 'run report'

    @api.model
    def _run_rapport(self):

        print("Crone exécuté evec succés")

        internships = self.env['res.partner'].search([('contact_type', '=', 'ST')])

        for internship in internships:
            if internship.start_date:
                date_now = date.today()
                inscription_date = internship.start_date
                dif = (date_now - inscription_date).days
                print(dif)
                if 182 <= dif < 364:
                    self.env['documents.document'].create(
                        {
                            'name': '/',
                            'report_id': self.env['documents.document.report'].search(
                                [('name', '=', "Premier Rapport")],
                                limit=1).id,
                            'internship_id': internship.id,
                            'folder_id': self.env['documents.folder'].search([('name', '=', "Rapports de stage")],
                                                                             limit=1).id,
                        }
                    )
                elif 364 <= dif < 546:
                    self.env['documents.document'].create(
                        {
                            'name': '/',
                            'report_id': self.env['documents.document.report'].search(
                                [('name', '=', "Deuxième Rapport")],
                                limit=1).id,
                            'internship_id': internship.id,
                            'folder_id': self.env['documents.folder'].search([('name', '=', "Rapports de stage")],
                                                                             limit=1).id,
                        }
                    )
                elif 546 <= dif < 728:
                    self.env['documents.document'].create(
                        {
                            'name': '/',
                            'report_id': self.env['documents.document.report'].search(
                                [('name', '=', "Troisième Rapport")],
                                limit=1).id,
                            'internship_id': internship.id,
                            'folder_id': self.env['documents.folder'].search([('name', '=', "Rapports de stage")],
                                                                             limit=1).id,
                        }
                    )
                elif 728 <= dif < 910:
                    self.env['documents.document'].create(
                        {
                            'name': '/',
                            'report_id': self.env['documents.document.report'].search(
                                [('name', '=', "Quatrième Rapport")],
                                limit=1).id,
                            'internship_id': internship.id,
                            'folder_id': self.env['documents.folder'].search([('name', '=', "Rapports de stage")],
                                                                             limit=1).id,
                        }
                    )
                elif 910 <= dif < 1092:
                    self.env['documents.document'].create(
                        {
                            'name': '/',
                            'report_id': self.env['documents.document.report'].search(
                                [('name', '=', "Cinquième Rapport")],
                                limit=1).id,
                            'internship_id': internship.id,
                            'folder_id': self.env['documents.folder'].search([('name', '=', "Rapports de stage")],
                                                                             limit=1).id,
                        }
                    )
                elif dif >= 1092:
                    self.env['documents.document'].create(
                        {
                            'name': '/',
                            'report_id': self.env['documents.document.report'].search(
                                [('name', '=', "Sixième Rapport")],
                                limit=1).id,
                            'internship_id': internship.id,
                            'folder_id': self.env['documents.folder'].search([('name', '=', "Rapports de stage")],
                                                                             limit=1).id,
                        }
                    )
        return True
