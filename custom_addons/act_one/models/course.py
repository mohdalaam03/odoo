from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Course(models.Model):
    _name = "course"
    _description = "Training Courses"

    # attributes
    name = fields.Char(string='Course Name', required=True)
    description = fields.Text(string='Course Description', required=True)

    serial_number = fields.Char(string='Serial Number', readonly=True, copy=False, default='New')

    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True)
    
    number_of_days = fields.Integer(
        string='Number of Days', 
        compute='_compute_number_of_days', 
        store=True
    )

    time = fields.Float(string='Class/Lecture Time', required=True)
    total_seats = fields.Integer(string='Total Seats Limit', default=20, required=True)
    available_seats = fields.Integer(
        string='Available Seats',
        compute='_compute_available_seats',
        store=True 
    )

    target_gender = fields.Selection([
        ('male', 'Male'),   
        ('female', 'Female')
        ], required=True)
    deadline = fields.Date(string='Registration Deadline', required=True)

    active = fields.Boolean('Active', default=True)
    
    #relations
    teacher_id = fields.Many2one('teacher', string='Teacher Name')
    room_id = fields.Many2one('room', string='Room Number')
    location_id = fields.Many2one('location', string='Course Location')
    registration_ids = fields.One2many('registration', 'course_id', string='Registrations')

    #methods
    @api.depends('registration_ids.state')
    def _compute_available_seats(self):
        for record in self:
            approved_registrations = record.registration_ids.filtered(lambda r: r.state == 'approved')
            taken_seats = self.env['registration'].search_count([
                ('course_id', '=', record.id),
                ('state', '=', 'approved')
            ])
            
            record.available_seats = max(0, record.total_seats - taken_seats)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('serial_number', 'New') == 'New':
                vals['serial_number'] = self.env['ir.sequence'].next_by_code('course.serial.seq') or 'New'
        return super(Course, self).create(vals_list)

    @api.depends('start_date', 'end_date')
    def _compute_number_of_days(self):
        for record in self:
            if record.start_date and record.end_date:
                delta = record.end_date - record.start_date
                
                if delta.days >= 0:
                    record.number_of_days = delta.days + 1
                else:
                    record.number_of_days = 0
            else:
                record.number_of_days = 0

    @api.constrains('start_date', 'end_date')
    def _check_date_sanity(self):
        for record in self:
            if record.start_date and record.end_date and record.end_date < record.start_date:
                raise ValidationError("The end date cannot be earlier than the start date.")