# -*- coding: utf-8 -*-
# =============================================================================
# TEACHER MODEL
# =============================================================================
# This model represents teachers in the school system.
# Complete all TODO items to implement the full functionality.
# =============================================================================

from datetime import date 
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class SchoolTeacher(models.Model):
    """
    Teacher Model
    
    Concepts covered:
    - Delegation inheritance (_inherits)
    - Related fields
    - Default values with lambda
    - Domain filters on relational fields
    - Monetary fields
    - Company-dependent fields
    """
    _name = 'school.teacher'
    _description = 'Teacher'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name asc'
    
    # ==========================================================================
    # TODO 1: Define Basic Fields
    # ==========================================================================
    # Add the following fields:
    # - employee_code: Char field, readonly, copy=False (auto-generated)
    # - name: Char field, required, tracking=True
    # - email: Char field, required
    # - phone: Char field
    # - date_of_birth: Date field
    # - hire_date: Date field, required, default=today
    # - department: Selection (science, arts, mathematics, languages, physical_education, other)
    # - qualification: Char field
    # - experience_years: Integer field with default 0
    # - biography: Html field
    # - photo: Binary field
    # - active: Boolean with default True
    # ==========================================================================
    
    # YOUR CODE HERE - Basic Fields
    employee_code = fields.Char(
        string='Employee Code',
        readonly=True,
        copy=False,
        default=lambda self: _('New'),
    )
    # TODO: Add remaining basic fields
    name = fields.Char(string='Name', required=True, tracking=True)
    user_id = fields.Many2one(
        'res.users', 
        string='Related User Account',
        ondelete='set null',
        help="The Odoo login user account associated with this teacher."
    )
    email = fields.Char(string='Email', required=True)
    phone = fields.Char(string='Phone')
    date_of_birth = fields.Date(string='Date of Birth')
    hire_date = fields.Date(string='Hire Date', required=True, default=fields.Date.today)
    department = fields.Selection([
        ('science', 'Science'),
        ('arts', 'Arts'),
        ('mathematics', 'Mathematics'),
        ('languages', 'Languages'),
        ('physical_education', 'Physical Education'),
        ('other', 'Other')
    ], string='Department')
    qualification = fields.Char(string='Qualification')
    experience_years = fields.Integer(string='Experience (Years)', default=0)
    biography = fields.Html(string='Biography')
    photo = fields.Binary(string='Photo')
    active = fields.Boolean(string='Active', default=True)

    # ==========================================================================
    # TODO 2: Define Monetary Field
    # ==========================================================================
    # Add salary field:
    # - salary: Monetary field
    # - currency_id: Many2one to 'res.currency' (use company's currency as default)
    # 
    # Hint: For monetary fields, you need both the monetary field and a currency field
    # ==========================================================================
    
    # YOUR CODE HERE - Monetary Fields
    salary = fields.Monetary(string='Salary', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    
    # ==========================================================================
    # TODO 3: Define Relational Fields
    # ==========================================================================
    # Add the following relational fields:
    # - course_ids: One2many to 'school.course' (inverse: teacher_id)
    # - user_id: Many2one to 'res.users' (linked portal user)
    # - company_id: Many2one to 'res.company' with default
    # ==========================================================================
    
    # YOUR CODE HERE - Relational Fields
    course_ids = fields.One2many('school.course', 'teacher_id', string='Courses')
    user_id = fields.Many2one('res.users', string='User')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    
    # ==========================================================================
    # TODO 4: Define Computed Fields
    # ==========================================================================
    # Implement:
    # - total_courses: Integer, count of course_ids
    # - total_students: Integer, count of all students across all courses
    # - age: Integer, calculated from date_of_birth
    # - years_of_service: Integer, calculated from hire_date
    # ==========================================================================
    
    # YOUR CODE HERE - Computed Fields and their compute methods
    total_courses = fields.Integer(string='Total Courses', compute='_compute_total_courses')
    total_students = fields.Integer(string='Total Students', compute='_compute_total_students')
    age = fields.Integer(string='Age', compute='_compute_age')
    years_of_service = fields.Integer(string='Years of Service', compute='_compute_years_of_service')

    @api.depends('course_ids')
    def _compute_total_courses(self):
        """Counts the total number of courses assigned to this teacher"""
        for record in self:
            record.total_courses = len(record.course_ids) if record.course_ids else 0

    @api.depends('course_ids.enrollment_ids')
    def _compute_total_students(self):
        """Counts all unique student profiles enrolled across all courses taught by this teacher"""
        for record in self:
            if record.course_ids:
                student_ids = set()
                for course in record.course_ids:
                    if course.enrollment_ids:
                        active_enrollments = course.enrollment_ids.filtered(lambda e: e.state in ('confirmed', 'pending'))
                        student_ids.update(active_enrollments.mapped('student_id.id'))
                record.total_students = len(student_ids)
            else:
                record.total_students = 0

    @api.depends('date_of_birth')
    def _compute_age(self):
        """Calculates current age based on Date of Birth"""
        today = date.today()
        for record in self:
            if record.date_of_birth:
                dob = fields.Date.from_string(record.date_of_birth)
                record.age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            else:
                record.age = 0

    @api.depends('hire_date')
    def _compute_years_of_service(self):
        """Calculates continuous years of service based on the staff hire date"""
        today = date.today()
        for record in self:
            if record.hire_date:
                h_date = fields.Date.from_string(record.hire_date)
                record.years_of_service = today.year - h_date.year - ((today.month, today.day) < (h_date.month, h_date.day))
                if record.years_of_service < 0:
                    record.years_of_service = 0
            else:
                record.years_of_service = 0

    # ==========================================================================
    # TODO 5: Define Related Fields
    # ==========================================================================
    # Add related fields:
    # - company_name: Char, related to company_id.name
    # - company_currency_id: Many2one, related to company_id.currency_id
    # ==========================================================================
    
    # YOUR CODE HERE - Related Fields
    company_name = fields.Char(string='Company Name', related='company_id.name', store=True)
    company_currency_id = fields.Many2one('res.currency', string='Company Currency', related='company_id.currency_id', store=True)
    
    # ==========================================================================
    # TODO 6: Define SQL and Python Constraints
    # ==========================================================================
    # SQL Constraints:
    # - unique_employee_code: employee_code must be unique
    # - check_experience: experience_years must be >= 0
    #
    # Python Constraints:
    # - hire_date cannot be in the future
    # - salary must be positive if provided
    # ==========================================================================
    
    _sql_constraints = [
        # YOUR CODE HERE
        ('unique_employee_code', 'unique(employee_code)', 'Employee code must be unique!'),
        ('check_experience', 'CHECK (experience_years >= 0)', 'Experience years must be non-negative!'),
    ]
    
    # YOUR CODE HERE - Python constraints
    @api.constrains('hire_date')
    def _check_hire_date(self):
        for record in self:
            if record.hire_date and record.hire_date > fields.Date.today():
                raise models.ValidationError("Hire date cannot be in the future!")

    @api.constrains('salary')
    def _check_salary(self):
        for record in self:
            if record.salary and record.salary <= 0:
                raise models.ValidationError("Salary must be positive!")

    # ==========================================================================
    # TODO 7: Override create method
    # ==========================================================================
    # - Generate employee_code using sequence 'school.teacher.sequence'
    # - Post creation message
    # ==========================================================================
    
    @api.model_create_multi
    def create(self, vals_list):
        """Override create to generate sequence and post tracking message"""
        for vals in vals_list:
            if vals.get('employee_code', _('New')) == _('New'):
                vals['employee_code'] = self.env['ir.sequence'].next_by_code('school.teacher.sequence') or _('New')
        
        records = super().create(vals_list)
        
        for record in records:
            record.message_post(
                body=_("Teacher profile successfully created with Employee Code: %s") % record.employee_code,
                subtype_xmlid="mail.mt_note"  # Posts it as a clean internal log note
            )
            
        return records

    
    
    # ==========================================================================
    # TODO 8: Implement Business Methods
    # ==========================================================================
    # 
    # 8.1 get_courses_summary(): Returns dict with course statistics
    #
    # 8.2 assign_to_course(course_id): Assigns teacher to a course
    #     - Validate teacher is not already assigned
    #     - Update course's teacher_id
    #
    # 8.3 remove_from_course(course_id): Removes teacher from a course
    # ==========================================================================
    
    def get_courses_summary(self):
        """TODO: Implement course summary"""
        self.ensure_one()
        return {
            'total_courses': len(self.course_ids),
            'total_students': sum(course.enrollment_ids.mapped('student_id').__len__() for course in self.course_ids),
            'course_details': [{
                'course_name': course.name,
                'enrolled_students': len(course.enrollment_ids)
            } for course in self.course_ids]
        }
    
    # TODO: Implement remaining methods
    def assign_to_course(self, course_id):
        """Assign teacher to a course"""
        course = self.env['school.course'].browse(course_id)
        if course.teacher_id:
            raise UserError(_("This course already has a teacher assigned."))
        course.teacher_id = self.id

    def remove_from_course(self, course_id):
        """Remove teacher from a course"""
        course = self.env['school.course'].browse(course_id)
        if course.teacher_id != self:
            raise UserError(_("You are not assigned to this course."))
        course.teacher_id = False

    def action_view_teacher_courses(self):
        """Opens a filtered window showing only the courses assigned to this teacher"""
        self.ensure_one()
        return {
            'name': _('Teacher Courses'),
            'type': 'ir.actions.act_window',
            'res_model': 'school.course',
            'view_mode': 'list,form',
            'domain': [('teacher_id', '=', self.id)],
            'context': {'default_teacher_id': self.id},
        }