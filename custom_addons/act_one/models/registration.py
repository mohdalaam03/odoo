from dateutil.relativedelta import relativedelta
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from datetime import date

class Registration(models.Model):
    _name = 'registration'
    _description = 'Course Registration'
    _rec_name = 'serial_number' 

    serial_number = fields.Char(string='Registration Serial', readonly=True, copy=False, default='New')

    name = fields.Char(string='Registration Name')
    trainee_id = fields.Many2one(
        'res.users', 
        string='Trainee Name', 
        required=True,
        default=lambda self: self.env.user,
        index=True
    )

    trainee_joining_date = fields.Date(
        string='Trainee Joining Date',
        compute='_compute_trainee_joining_date',
        store=True
    )

    course_id = fields.Many2one(
        'course',
        string='Course Name',
        required=True,
        domain="[('end_date', '>=', context_today())]")

    course_description = fields.Text(related='course_id.description', string='Course Description', readonly=True)
    start_date = fields.Date(related='course_id.start_date', string='Start Date', readonly=True, store=True)
    end_date = fields.Date(related='course_id.end_date', string='End Date', readonly=True, store=True)
    number_of_days = fields.Integer(related='course_id.number_of_days', string='Number of Days', readonly=True)
    time = fields.Float(related='course_id.time', string='Time', readonly=True)

    job_position = fields.Char(
        string='Job Position', 
        default='Trainee Employee',
        help="The current job role/title of the employee inside the company."
    )

    teacher_id = fields.Many2one(related='course_id.teacher_id', string='Teacher Name', store=True)
    room_id = fields.Many2one(related='course_id.room_id', string='Room Number', readonly=True)
    location_id = fields.Many2one(related='course_id.location_id', string='Course Location', readonly=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('teacher', 'Teacher Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], string='Status', default='draft', required=True)

    def action_confirm(self):
        for record in self:
            if record.state != 'draft':
                raise UserError("Only draft registrations can be confirmed.")
            record._check_yearly_enrollment_rules()
            record.state = 'teacher'

    def action_approve(self):
        for record in self:
            if record.state != 'teacher':
                raise UserError("Only registrations in Teacher Review can be approved.")

            if self.env.uid != 1 and record.course_id.teacher_id.user_id != self.env.user:
                raise UserError("Only the designated teacher for this course can approve this registration.")
                
            record._check_yearly_enrollment_rules()
            record.state = 'approved'

    def action_reject(self):
        for record in self:
            if record.state != 'teacher':
                raise UserError("Only registrations in Teacher Review can be rejected.")

            if self.env.uid != 1 and record.course_id.teacher_id.user_id != self.env.user:
                raise UserError("Only the designated teacher for this course can reject this registration.")
                
            record.state = 'rejected'

    @api.constrains('course_id', 'state')
    def _check_course_seat_availability(self):
        for record in self:
            if record.course_id and record.state == 'approved':
                
                approved_count = self.search_count([
                    ('course_id', '=', record.course_id.id),
                    ('state', '=', 'approved')
                ])

                if approved_count > record.course_id.total_seats:
                    raise ValidationError("Seats are full! You cannot register for this course.")

    @api.constrains('trainee_id', 'course_id', 'state')
    def _check_yearly_enrollment_rules(self):
        for record in self:
            if record.state in ['draft', 'rejected'] or not record.start_date:
                continue

            if self.env.uid == 1:
                continue

            target_year = record.start_date.year
            start_of_year = date(target_year, 1, 1)
            end_of_year = date(target_year, 12, 31)

            existing_records = self.search([
                ('trainee_id', '=', record.trainee_id.id),
                ('id', '!=', record._origin.id if hasattr(record, '_origin') else record.id),
                ('start_date', '>=', start_of_year),
                ('start_date', '<=', end_of_year),
                ('state', 'in', ['teacher', 'approved'])
            ])

            if any(r.state == 'teacher' for r in existing_records):
                raise ValidationError(
                    "If Employee has pending request for the current year, the employee can not apply for another course."
                )

            if any(r.state == 'approved' for r in existing_records):
                raise ValidationError(
                    "Employee can not enroll in more than one course per year."
                )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('serial_number', 'New') == 'New':
                vals['serial_number'] = self.env['ir.sequence'].next_by_code('registration.serial.seq') or 'New'
        return super(Registration, self).create(vals_list)

    @api.depends('trainee_id')
    def _compute_trainee_joining_date(self):
        for record in self:
            if record.trainee_id and record.trainee_id.create_date:
                record.trainee_joining_date = record.trainee_id.create_date.date()
            else:
                record.trainee_joining_date = fields.Date.today()

    @api.constrains('trainee_id', 'trainee_joining_date')
    def _check_trainee_employment_tenure(self):
        for record in self:
            if not record.trainee_joining_date:
                continue
                
            if self.env.uid == 1:
                continue

            six_months_ago_limit = fields.Date.today() - relativedelta(months=6)

            if record.trainee_joining_date > six_months_ago_limit:
                raise ValidationError(
                    "Any Employee who has not completed 6 months of joining the company cannot register."
                )
