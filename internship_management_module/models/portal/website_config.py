from odoo import models, fields, api

import logging
_logger = logging.getLogger(__name__)


class WebsiteConfig(models.Model):
    _name = 'website.config'
    _description = 'Website Configuration'

    header_options = fields.Json("Header Option (JSON)")
    header_list = fields.Char("Header Options as list")

    @api.model
    def evaluate(self, source):
        """ A permission to use 'eval' built-in function """
        allowed = {
            '__builtins__': {},   ### Prevent 'eval' from running dangerous code by restricting the use of the builtins  
        }
        return eval(source, allowed)

    @api.model_create_multi
    def create(self, vals_list):
        if len(vals_list) > 1:
            _logger.warn(f"Cannot create more than 1 website config. Creating just the first one provided")
        vals_list = [vals_list[0], ]

        if self.search_count([]) == 0:
            return super().create(vals_list) 
            
        _logger.warn(f"Failed to create record because one already exists. Use update_config instead to update it")

    @api.model
    def update_config(self, vals_list):
        if isinstance(vals_list, list) and len(vals_list) == 1:
            if self.search_count([]) >= 1:
                self.search([]).unlink()
                self.create(vals_list)

    @api.model
    def get_config(self):
        """ Returns the unique configuration record """
        config = self.sudo().search([], limit=1)
        if not config.header_list:
            config.unlink()
            config = self.sudo().create(
                {
                    'header_list': [
                        ('Mon compte', '/my'),
                        ('Mes cotisations', '/cotisations'),
                        ('Mes déclarations', '/declarations'),
                        ('Mes stagiaires encadrés', '/my/internships/ms'),
                        ('Mes stagiaires contrôlés', '/my/internships/cs'),
                    ], 
                    'header_options': {
                        'cotisations_option': {
                            'name': 'Mes cotisations',
                            'href': '/cotisations'
                        },
                        'declarations_option': {
                            'name': 'Mes déclarations',
                            'href': '/declarations'
                        },
                        'supervised_interns_option': {
                            'name': 'Mes stagiaires encadrés',
                            'href': '/'
                        },
                        'controlled_interns_option': {
                            'name': 'Mes stagiaires contrôlés',
                            'href': '/'
                        },
                        'quality_control_option': {
                            'name': 'Mes contrôles qualité',
                            'href': '/'
                        },
                        'rdv_option': {
                            'name': 'Rendez-vous',
                            'href': '/rendez-vous'
                        },
                        'event_option': {
                            'name': 'Événements',
                            'href': '/event'
                        },
                    }
                }
            )
        return config

    def get_filtered_menus(self, partner_status=None):
        config = self.get_config()
        if partner_status == 'in_progress':
            return [
                ('Mon compte', '/my'),
                ("S'inscrire", '/demande-inscription')
            ]
        return config.header_list or []


