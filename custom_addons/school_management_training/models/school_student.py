# -*- coding: utf-8 -*-
# =============================================================================
# STUDENT MODEL
# =============================================================================
# This is the main student model for the school management system.
# Complete all TODO items to implement the full functionality.
# =============================================================================

from datetime import date
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class SchoolStudent(models.Model):
    """
    Student Model
    
    This model represents a student in the school system.
    Students can enroll in courses, receive grades, and have attendance tracked.
    
    Concepts covered:
    - Basic field types (Char, Text, Date, Selection, Boolean, Integer, Float)
    - Relational fields (Many2one, One2many, Many2many)
    - Computed fields with @api.depends
    - Constraints with @api.constrains
    - Onchange methods with @api.onchange
    - CRUD method overrides (create, write, unlink, copy)
    - Mail integration for messaging/chatter
    - Sequence generation
    - SQL constraints
    - State machine pattern
    """
    _name = 'school.student'
    _description = 'Student'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name asc'
    _rec_name = 'display_name'
    
    # ==========================================================================
    # TODO 1: Define Basic Fields
    # ==========================================================================
    # Add the following fields:
    # - student_code: Char field, readonly, copy=False (will be auto-generated)
    # - name: Char field, required, tracking=True
    # - last_name: Char field, required
    # - email: Char field with email validation
    # - phone: Char field
    # - date_of_birth: Date field, required
    # - gender: Selection field with options: male, female, other
    # - address: Text field
    # - photo: Binary field for student photo
    # - active: Boolean field with default True
    # - notes: Html field
    # ==========================================================================

    
    # YOUR CODE HERE - Basic Fields
    student_code = fields.Char(
        string='Student Code',
        readonly=True,
        copy=False,
        default=lambda self: _('New'),
    )
    # TODO: Add remaining basic fields below
    name = fields.Char(string='First Name', required=True, tracking=True)
    user_id = fields.Many2one(
        'res.users', 
        string='Related User Account',
        ondelete='set null',
        help="The Odoo login user account associated with this student."
    )
    last_name = fields.Char(string='Last Name', required=True)
    email = fields.Char(string='Email', copy=False)
    phone = fields.Char(string='Phone')
    date_of_birth = fields.Date(string='Date of Birth', required=True)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ], string='Gender')
    address = fields.Text(string='Address')
    photo = fields.Binary(string='Photo')
    active = fields.Boolean(string='Active', default=True)
    notes = fields.Html(string='Notes')
    
    # ==========================================================================
    # TODO 2: Define Relational Fields
    # ==========================================================================
    # Add the following relational fields:
    # - guardian_id: Many2one to 'res.partner' (parent/guardian)
    # - enrollment_ids: One2many to 'school.enrollment' (inverse: student_id)
    # - course_ids: Many2many to 'school.course' (through school_student_course_rel)
    # - grade_ids: One2many to 'school.grade' (inverse: student_id)
    # - attendance_ids: One2many to 'school.attendance' (inverse: student_id)
    # - class_id: Many2one to 'school.course' for current primary class
    # ==========================================================================
    
    # YOUR CODE HERE - Relational Fields
    guardian_id = fields.Many2one('res.partner', string='Guardian')
    enrollment_ids = fields.One2many('school.enrollment', 'student_id', string='Enrollments')
    course_ids = fields.Many2many('school.course', string='Courses')
    grade_ids = fields.One2many('school.grade', 'student_id', string='Grades')
    attendance_ids = fields.One2many('school.attendance', 'student_id', string='Attendance')
    
    # ==========================================================================
    # TODO 3: Define Selection Field for State
    # ==========================================================================
    # Add a 'state' selection field with the following states:
    # - draft: Draft
    # - enrolled: Enrolled
    # - graduated: Graduated
    # - suspended: Suspended
    # - withdrawn: Withdrawn
    # Default should be 'draft', and it should have tracking=True
    # ==========================================================================
    
    # YOUR CODE HERE - State Field
    state = fields.Selection([
        ('draft', 'Draft'),
        ('enrolled', 'Enrolled'),
        ('graduated', 'Graduated'),
        ('suspended', 'Suspended'),
        ('withdrawn', 'Withdrawn'),
    ], string='State', default='draft', tracking=True)
    
    # ==========================================================================
    # TODO 4: Define Computed Fields
    # ==========================================================================
    # Implement the following computed fields:
    # 
    # 4.1 display_name: Combines name and last_name
    #     - Should compute as "last_name, name" (e.g., "Smith, John")
    #     - Depends on: name, last_name
    #
    # 4.2 age: Integer field computed from date_of_birth
    #     - Calculate years between date_of_birth and today
    #     - Depends on: date_of_birth
    #
    # 4.3 total_courses: Integer field counting enrolled courses
    #     - Count the number of records in enrollment_ids
    #     - Depends on: enrollment_ids
    #
    # 4.4 average_grade: Float field with digits=(5, 2)
    #     - Calculate average of all grades from grade_ids
    #     - Depends on: grade_ids.score
    #
    # 4.5 attendance_rate: Float field with digits=(5, 2)
    #     - Calculate percentage of 'present' attendance records
    #     - Depends on: attendance_ids.status
    # ==========================================================================
    
    # YOUR CODE HERE - Computed Fields
    display_name = fields.Char(
        string='Display Name',
        compute='_compute_display_name',
        store=True,
    )
    
    # TODO: Add age, total_courses, average_grade, attendance_rate fields
    age = fields.Integer(
        string="Age", 
        compute="_compute_age", 
        store=True
    )
    total_courses = fields.Integer(
        string="Total Courses", 
        compute="_compute_total_courses", 
        store=True
    )
    average_grade = fields.Float(
        string="Average Grade", 
        compute="_compute_average_grade", 
        store=True
    )
    attendance_rate = fields.Float(
        string="Attendance Rate (%)", 
        compute="_compute_attendance_rate", 
        store=True
    )

    # TODO: Implement all compute methods below
    
    @api.depends('name', 'last_name')
    def _compute_display_name(self):
        """
        TODO: Implement display_name computation
        Format: "last_name, name" (e.g., "Smith, John")
        Handle cases where last_name or name might be empty
        """
        for record in self:
            # YOUR CODE HERE
            if record.name and record.last_name:
                record.display_name = f"{record.last_name}, {record.name}"
            elif record.name:
                record.display_name = record.name
            else:
                # Safe fallback configuration if fields are blank during initial generation
                record.display_name = record.student_code or _("New Student")
    
    # TODO: Implement _compute_age method
    # Example implementation for age:
    age = fields.Integer(string='Age', compute='_compute_age', store=True)

    @api.depends('date_of_birth')
    def _compute_age(self):
        for record in self:
            if record.date_of_birth:
                today = date.today()
                record.age = today.year - record.date_of_birth.year - (
                    (today.month, today.day) < (record.date_of_birth.month, record.date_of_birth.day)
                )
            else:
                record.age = 0

    # TODO: Implement _compute_total_courses method
    @api.depends('course_ids')
    def _compute_total_courses(self):
        for record in self:
            record.total_courses = len(record.course_ids) if record.course_ids else 0

    # TODO: Implement _compute_average_grade method
    @api.depends('grade_ids.score', 'grade_ids.max_score')
    def _compute_average_grade(self):
        """
        Computes the student's true overall performance percentage.
        Compares cumulative points earned against total points possible.
        """
        for record in self:
            if record.grade_ids:
                total_earned = sum(grade.score for grade in record.grade_ids) 
                
                total_possible = sum(grade.max_score for grade in record.grade_ids) 
                
                if total_possible > 0:  
                    record.average_grade = (total_earned / total_possible) * 100.0
                else:
                    record.average_grade = 0.0
            else:
                record.average_grade = 0.0
    
    # TODO: Implement _compute_attendance_rate method
    @api.depends('attendance_ids.status')
    def _compute_attendance_rate(self):
        for record in self:
            total = len(record.attendance_ids)
            if total > 0:
                present_count = len(record.attendance_ids.filtered(lambda a: a.status == 'present'))
                record.attendance_rate = (present_count / total) * 100
            else:
                record.attendance_rate = 0.0
    
    # ==========================================================================
    # TODO 5: Define SQL Constraints
    # ==========================================================================
    # Add _sql_constraints with:
    # - unique_student_code: student_code must be unique
    # - unique_email: email must be unique
    # - check_date_of_birth: date_of_birth must be in the past
    # ==========================================================================
    
    # YOUR CODE HERE - SQL Constraints
    _sql_constraints = [
        ('unique_student_code', 'UNIQUE(student_code)', 'Student code must be unique!'),
        ('unique_email', 'UNIQUE(email)', 'Email must be unique!'),
        ('check_date_of_birth', 'CHECK(date_of_birth < CURRENT_DATE)', 'Date of birth must be in the past!'),
    ]
    
    
    # ==========================================================================
    # TODO 6: Define Python Constraints
    # ==========================================================================
    # Implement @api.constrains methods for:
    # 
    # 6.1 _check_age: Validate that student is between 5 and 100 years old
    #
    # 6.2 _check_email_format: Validate email contains @ symbol
    # ==========================================================================
    
    # YOUR CODE HERE - Python Constraints
    
    @api.constrains('date_of_birth')
    def _check_age(self):
        """
        TODO: Implement age validation
        - Student must be at least 5 years old
        - Student must be less than 100 years old
        - Raise ValidationError with appropriate message if invalid
        """
        for record in self:
            # YOUR CODE HERE
            age = (fields.Date.today() - record.date_of_birth).days // 365
            if age < 5 or age > 100:
                raise ValidationError("Student must be between 5 and 100 years old!")
    
    # TODO: Implement _check_email_format method
    @api.constrains('email')
    def _check_email_format(self):
        for record in self:
            if record.email and '@' not in record.email:
                raise ValidationError("Email must contain '@' symbol!")
    
    # ==========================================================================
    # TODO 7: Define Onchange Methods
    # ==========================================================================
    # Implement @api.onchange methods for:
    #
    # 7.1 _onchange_guardian: When guardian_id changes, if guardian has email,
    #     suggest to copy it to student's email (only if student email is empty)
    #
    # 7.2 _onchange_date_of_birth: Show a warning if student is under 6 years old
    # ==========================================================================
    
    # YOUR CODE HERE - Onchange Methods
    @api.onchange('guardian_id')
    def _onchange_guardian(self):
        if self.guardian_id and self.guardian_id.email and not self.email:
            self.email = self.guardian_id.email
            return {
                'warning': {
                    'title': "Guardian Email Copied",
                    'message': "Guardian's email has been copied to student's email.",
                }
            }

    @api.onchange('date_of_birth')
    def _onchange_date_of_birth(self):
        if self.date_of_birth:
            age = (fields.Date.today() - self.date_of_birth).days // 365
            if age < 6:
                return {
                    'warning': {
                        'title': "Age Warning",
                        'message': "Student is under 6 years old.",
                    }
                }
    
    # ==========================================================================
    # TODO 8: Override CRUD Methods
    # ==========================================================================
    # 
    # 8.1 Override create():
    #     - Generate student_code using sequence 'school.student.sequence'
    #     - Post a message "Student record created" to chatter
    #
    # 8.2 Override write():
    #     - If state changes, post message about state change
    #     - Prevent editing if student is 'graduated' (raise UserError)
    #
    # 8.3 Override unlink():
    #     - Prevent deletion if student has any enrollments
    #     - Raise UserError with appropriate message
    #
    # 8.4 Override copy():
    #     - Clear student_code (should be regenerated)
    #     - Append " (Copy)" to the name
    #     - Reset state to 'draft'
    # ==========================================================================
    
    @api.model_create_multi
    def create(self, vals_list):
        """
        TODO: Implement create override
        - Generate sequence for student_code
        - Post creation message to chatter
        """
        for vals in vals_list:
            if vals.get('student_code', _('New')) == _('New'):
                vals['student_code'] = self.env['ir.sequence'].next_by_code('school.student.sequence') or _('New')
        
        records = super().create(vals_list)
        
        # TODO: Post message to chatter for each record
        for record in records:
            record.message_post(body="Student record created.")
        
        return records
    
    # TODO: Implement write override
    def write(self, vals):
        for record in self:
            if 'state' in vals and vals['state'] != record.state:
                record.message_post(body=f"State changed from {record.state} to {vals['state']}.")
        return super().write(vals)
    
    # TODO: Implement unlink override
    def unlink(self):
        for record in self:
            if record.enrollment_ids:
                raise UserError("Cannot delete student with enrollments.")
        return super().unlink()
    
    # TODO: Implement copy override
    def copy(self, default=None):
        default = dict(default or {})
        default['student_code'] = _('New')
        default['name'] = f"{self.name} (Copy)"
        default['state'] = 'draft'
        return super().copy(default)
    
    # ==========================================================================
    # TODO 9: Implement State Transition Methods (Action Buttons)
    # ==========================================================================
    # Implement button action methods for state transitions:
    #
    # 9.1 action_enroll(): draft -> enrolled
    #     - Validate student has at least one enrollment
    #
    # 9.2 action_graduate(): enrolled -> graduated
    #     - Validate average_grade >= 60
    #
    # 9.3 action_suspend(): enrolled -> suspended
    #     - Require a reason (use wizard or simple field)
    #
    # 9.4 action_withdraw(): any state -> withdrawn
    #
    # 9.5 action_reactivate(): suspended/withdrawn -> enrolled
    #     - Only allowed if student was previously enrolled
    #
    # 9.6 action_reset_to_draft(): any state -> draft
    #     - Only allowed for users with manager group
    # ==========================================================================
    
    def action_enroll(self):
        """
        TODO: Implement enrollment action
        - Change state from 'draft' to 'enrolled'
        - Validate that student has at least one enrollment
        - Post message about enrollment
        """
        for record in self:
            # YOUR CODE HERE
            if not record.enrollment_ids:
                raise UserError("Cannot enroll student without any enrollments.")
            record.state = 'enrolled'
            record.message_post(body="Student enrolled.")
    
    # TODO: Implement remaining action methods
    def action_graduate(self):
        for record in self:
            if record.average_grade < 60:
                raise UserError("Cannot graduate student with average grade below 60.")
            record.state = 'graduated'
            record.message_post(body="Student graduated.")

    def action_suspend(self):
        for record in self:
            record.state = 'suspended'
            record.message_post(body="Student suspended.")

    def action_withdraw(self):
        for record in self:
            record.state = 'withdrawn'
            record.message_post(body="Student withdrawn.")

    def action_reactivate(self):
        for record in self:
            if record.state not in ['suspended', 'withdrawn']:
                raise UserError("Can only reactivate suspended or withdrawn students.")
            record.state = 'enrolled'
            record.message_post(body="Student reactivated to enrolled state.")

    def action_reset_to_draft(self):
        for record in self:
            if not self.env.user.has_group('school_management_training.group_school_manager'):
                raise UserError("Only managers can reset to draft.")
            record.state = 'draft'
            record.message_post(body="Student state reset to draft.")

    def action_view_enrollments(self):
        """
        Triggered by the XML stat button.
        Opens a window showing only the enrollment records for this specific student.
        """
        self.ensure_one()
        return {
            'name': _('Student Enrollments'),
            'type': 'ir.actions.act_window',
            'res_model': 'school.enrollment',
            'view_mode': 'list,form',
            'domain': [('student_id', '=', self.id)],
            'context': {'default_student_id': self.id},
        }

    
    # ==========================================================================
    # TODO 10: Implement Business Logic Methods
    # ==========================================================================
    # Implement the following business methods:
    #
    # 10.1 get_grade_summary(): Returns dict with grade statistics
    #      {'total': int, 'average': float, 'highest': float, 'lowest': float}
    #
    # 10.2 get_attendance_summary(): Returns attendance statistics dict
    #      {'total': int, 'present': int, 'absent': int, 'late': int, 'rate': float}
    #
    # 10.3 send_welcome_email(): Sends welcome email to student (use mail.template)
    #
    # 10.4 check_eligibility_for_graduation(): Returns True/False based on criteria
    #      - Average grade >= 60
    #      - Attendance rate >= 75
    #      - All required courses completed
    # ==========================================================================
    
    def get_grade_summary(self):
        """
        TODO: Implement grade summary calculation
        Return dict with: total, average, highest, lowest grades
        """
        self.ensure_one()
        # YOUR CODE HERE
        return {
            'total': len(self.grade_ids),
            'average': self.average_grade,
            'highest': max(self.grade_ids.mapped('grade')) if self.grade_ids else 0,
            'lowest': min(self.grade_ids.mapped('grade')) if self.grade_ids else 0
        }
    
    # TODO: Implement remaining business methods
    def get_attendance_summary(self):
        self.ensure_one()
        total = len(self.attendance_ids)
        present = len(self.attendance_ids.filtered(lambda a: a.status == 'present'))
        absent = len(self.attendance_ids.filtered(lambda a: a.status == 'absent'))
        late = len(self.attendance_ids.filtered(lambda a: a.status == 'late'))
        rate = (present / total * 100) if total > 0 else 0.0
        return {
            'total': total,
            'present': present,
            'absent': absent,
            'late': late,
            'rate': rate
        }

    def send_welcome_email(self):
        self.ensure_one()
        template = self.env.ref('school_management_training.email_template_welcome_student')
        if template:
            template.send_mail(self.id, force_send=True)

    def check_eligibility_for_graduation(self):
        self.ensure_one()
        grade_ok = self.average_grade >= 60
        attendance_ok = self.get_attendance_summary()['rate'] >= 75
        required_courses = self.env['school.course'].search([('is_mandatory', '=', True)])
        courses_ok = all(course in self.course_ids for course in required_courses)
        return grade_ok and attendance_ok and courses_ok
    
    # ==========================================================================
    # TODO 11: Implement Search and Name Methods
    # ==========================================================================
    #
    # 11.1 Override _name_search to allow searching by:
    #      - student_code
    #      - name
    #      - last_name
    #      - email
    #
    # 11.2 Implement name_get alternative if needed (for special display)
    # ==========================================================================
    
    @api.model
    def _name_search(self, name='', domain=None, operator='ilike', limit=None, order=None):
        """
        TODO: Implement custom name search
        Allow searching by student_code, name, last_name, or email
        """
        domain = domain or []
        if name:
            search_domain = ['|', '|', '|',
                ('student_code', operator, name),
                ('name', operator, name),
                ('last_name', operator, name),
                ('email', operator, name)
            ]
            domain = search_domain + domain
            
        return self._search(domain, limit=limit, order=order)

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        """
        Legacy & Test Framework Shorthand Method Override.
        Ensures a list of classic tuples is explicitly returned when requested by tests.
        """
        args = args or []
        records = self._name_search(name, domain=args, operator=operator, limit=limit)
        
        return [(r.id, r.display_name) for r in self.browse(records)]