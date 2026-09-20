from odoo import models, fields, api

class Teacher(models.Model):
    _name = "teacher"
    _description = "Training Course Teacher"

    name = fields.Char(string='Teacher Name', required=True)
    code = fields.Char(string='Teacher Code', readonly=True, default='New')

    user_id = fields.Many2one('res.users', string='Related User')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('code', 'New') == 'New':
                vals['code'] = self.env['ir.sequence'].next_by_code('teacher.code.seq') or 'New'

        records = super(Teacher, self).create(vals_list)
        
        teacher_group = self.env.ref('act_one.group_training_teacher', raise_if_not_found=False)
        
        if teacher_group:
            for record in records:
                if record.user_id:
                    teacher_group.write({'users': [(4, record.user_id.id)]})
                    
        return records