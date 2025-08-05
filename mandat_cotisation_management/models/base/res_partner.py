from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)

class Partner(models.Model):
    _inherit = 'res.partner'



    associate_type = fields.Selection(
        string="Qualité de l'associé",
        selection=[
            ('manager', _('Expert-comptable gérant')),
            ('non_manager', _('Expert-comptable associé non gérant')),
            ('employee', _('Expert-comptable salarié')),
        ]
    )

    # def _get_parent_fields(self, vals):
    #     if vals.get('parent_id', None):
    #         _logger.warning(f"--------------------------------> {vals['parent_id']}")
    #         parent = self.browse(vals['parent_id'])
    #         parent_fields = parent._fields
    #         parent_field_names = set(parent_fields.keys())
    #         excluded_field_names = {
    #             # database specific fields
    #             'id', 
    #             'create_uid', 
    #             'create_date', 
    #             'write_uid', 
    #             'write_date', 
    #             # other fields
    #             'parent_id', 
    #             'child_ids', 
    #             'associate_type',
    #             }
    #         to_copy = parent_field_names.symmetric_difference(excluded_field_names)
    #         return dict(filter(lambda a: a[0] in to_copy, parent_fields.items()))
    
    # @api.model_create_multi
    # def create(self, vals_list):
    #     for vals in vals_list:
    #         parent_fields = self._get_parent_fields(vals)
    #         if parent_fields:
    #             vals.update(
    #                 parent_fields
    #             )
    #     return super().create(vals_list)  

    @api.model_create_multi
    def create(self, vals_list):
        for i, vals in enumerate(vals_list):
            # Check if this is a child partner being created
            if vals.get('parent_id'):
                parent = self.env['res.partner'].browse(vals['parent_id'])
                
                # Define fields to always exclude
                system_fields = [
                    'id', 'create_date', 'create_uid', 
                    'write_date', 'write_uid', 
                    'display_name', 
                    'parent_id', 'child_ids',
                    'commercial_company_name'
                ]
                
                # Custom fields to exclude (can be modified as needed)
                custom_exclude_fields = [
                    'name',  # Example of a custom field to exclude
                    # Add any other fields you want to exclude
                    'associate_type',
                ]
                
                # Combine system and custom excluded fields
                exclude_fields = system_fields + custom_exclude_fields
                
                # Prepare default values
                default = {
                    field: False for field in exclude_fields
                }
                default['parent_id'] = vals['parent_id']
                
                # Use copy_data to get inheritable values
                inherited_vals = parent.copy_data(default=default)[0]
                
                # Update creation values with inherited data
                # Only add fields not already specified
                for key, value in inherited_vals.items():
                    if key not in vals:
                        vals[key] = value
                
                vals_list[i] = vals
            
        # Call original create method
        return super(Partner, self).create(vals_list)