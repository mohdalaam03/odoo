from odoo import models, fields, api

class Location(models.Model):
    _name = "location"
    _description = "Course Location"

    name = fields.Char(string='Location Name', required=True)
    code = fields.Char(string='Location Code', readonly=True, default='New')


    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('code', 'New') == 'New':
                vals['code'] = self.env['ir.sequence'].next_by_code('location.code.seq') or 'New'
        return super(Location, self).create(vals_list)