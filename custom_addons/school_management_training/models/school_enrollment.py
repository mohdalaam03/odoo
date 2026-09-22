# -*- coding: utf-8 -*-
# =============================================================================
# ENROLLMENT MODEL
# =============================================================================
# This model handles student enrollments in courses.
# Complete all TODO items to implement the full functionality.
# =============================================================================

from datetime import date

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class SchoolEnrollment(models.Model):
    """
    Enrollment Model
    
    Manages the relationship between students and courses.
    
    Concepts covered:
    - Unique together constraint
    - Date validation
    - State workflow with validations
    - Automatic field computation
    - Record rules (security)
    """
    _name = 'school.enrollment'
    _description = 'Course Enrollment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'enrollment_date desc'
    _rec_name = 'display_name'
    
    # ==========================================================================
    # TODO 1: Define Basic Fields
    # ==========================================================================
    # Add the following fields:
    # - enrollment_date: Date, required, default=today
    # - completion_date: Date (when student completes the course)
    # - notes: Text
    # - priority: Selection (0: Normal, 1: Low, 2: Medium, 3: High)
    # ==========================================================================
    
    # YOUR CODE HERE - Basic Fields
    enrollment_date = fields.Date(
        string='Enrollment Date',
        required=True,
        default=fields.Date.today
    )
    completion_date = fields.Date(string='Completion Date')
    notes = fields.Text(string='Notes')
    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Low'),
        ('2', 'Medium'),
        ('3', 'High')
    ], string='Priority', default='0')

    # ==========================================================================
    # TODO 2: Define Relational Fields
    # ==========================================================================
    # Add the following fields:
    # - student_id: Many2one to 'school.student', required, ondelete='cascade'
    # - course_id: Many2one to 'school.course', required, ondelete='cascade'
    # - teacher_id: Many2one to 'school.teacher', related to course_id.teacher_id
    # ==========================================================================
    
    # YOUR CODE HERE - Relational Fields
    student_id = fields.Many2one('school.student', string='Student', required=True, ondelete='cascade')
    course_id = fields.Many2one('school.course', string='Course', required=True, ondelete='cascade')
    teacher_id = fields.Many2one('school.teacher', string='Teacher', related='course_id.teacher_id', readonly=True)

    # ==========================================================================
    # TODO 3: Define State Field
    # ==========================================================================
    # Add state field with states:
    # - draft: Draft
    # - pending: Pending Approval
    # - confirmed: Confirmed
    # - completed: Completed
    # - cancelled: Cancelled
    # - dropped: Dropped
    # ==========================================================================
    
    # YOUR CODE HERE - State Field
    state = fields.Selection([
        ('draft', 'Draft'), 
        ('pending', 'Pending Approval'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('dropped', 'Dropped')
    ], string='State', default='draft')

    # ==========================================================================
    # TODO 4: Define Computed Fields
    # ==========================================================================
    # - display_name: Computed as "Student Name - Course Name"
    # - duration_days: Integer, days between enrollment_date and completion_date or today
    # - is_active: Boolean, True if state in ('confirmed', 'pending')
    # - student_grade: Float, related to the student's grade in this course
    # ==========================================================================
    
    display_name = fields.Char(
        string='Display Name',
        compute='_compute_display_name',
        store=True,
    )
    duration_days = fields.Integer(
        string='Duration (Days)',
        compute='_compute_duration_days',
        store=True
    )
    is_active = fields.Boolean(
        string='Is Active',
        compute='_compute_is_active',
        store=True
    )
    student_grade = fields.Float(
        string='Student Grade',
        compute='_compute_student_grade',
        store=True
    )

    @api.depends('student_id', 'student_id.name', 'course_id', 'course_id.name')
    def _compute_display_name(self):
        """TODO: Implement display name computation"""
        for record in self:
            # YOUR CODE HERE
            if record.student_id and record.course_id:
                record.display_name = f"{record.student_id.name} - {record.course_id.name}"

    @api.depends('enrollment_date', 'completion_date')
    def _compute_duration_days(self):
        """TODO: Implement duration days computation"""
        for record in self:
            # YOUR CODE HERE
            if record.enrollment_date:
                if record.completion_date:
                    delta = record.completion_date - record.enrollment_date
                else:
                    delta = fields.Date.today() - record.enrollment_date
                record.duration_days = delta.days

    @api.depends('state')
    def _compute_is_active(self):
        """TODO: Implement is_active computation"""
        for record in self:
            # YOUR CODE HERE
            record.is_active = record.state in ('confirmed', 'pending')

    @api.depends('student_id', 'course_id')
    def _compute_student_grade(self):
        for record in self:
            record.student_grade = 0.0
            
            if record.student_id and record.course_id:
                grade_record = self.env['school.grade'].search([
                    ('student_id', '=', record.student_id.id),
                    ('course_id', '=', record.course_id.id)
                ], limit=1) 
                
                if grade_record:
                    record.student_grade = grade_record.score

    # ==========================================================================
    # TODO 5: Define Constraints
    # ==========================================================================
    # SQL Constraints:
    # - unique_student_course: A student can only enroll once per course
    #
    # Python Constraints:
    # - completion_date must be after enrollment_date
    # - Cannot enroll in a full course
    # - Cannot enroll if student doesn't meet prerequisites
    # ==========================================================================
    
    _sql_constraints = [
        ('unique_student_course', 'UNIQUE(student_id, course_id)', 
         'Student is already enrolled in this course!'),
        # TODO: Add more constraints if needed
    ]
    
    @api.constrains('enrollment_date', 'completion_date')
    def _check_dates(self):
        """TODO: Validate that completion_date is after enrollment_date"""
        for record in self:
            # YOUR CODE HERE
            if record.completion_date and record.enrollment_date:
                if record.completion_date < record.enrollment_date:
                    raise ValidationError("Completion date must be after enrollment date.")

    # TODO: Implement remaining constraints
    @api.constrains('student_id', 'course_id')
    def _check_course_capacity(self):
        """TODO: Validate that the course has available spots"""
        for record in self:
            if record.course_id:
                enrolled_count = self.search_count([
                    ('course_id', '=', record.course_id.id),
                    ('state', 'in', ['confirmed'])
                ])
                if enrolled_count >= record.course_id.max_students:
                    raise ValidationError("Cannot enroll: Course is full.")

    def _check_prerequisites(self):
        """TODO: Validate that the student meets the course prerequisites"""
        for record in self:
            if record.course_id and record.student_id:
                prerequisites = record.course_id.prerequisite_course_ids
                for prereq in prerequisites:
                    prereq_enrollment = self.search([
                        ('student_id', '=', record.student_id.id),
                        ('course_id', '=', prereq.id),
                        ('state', '=', 'completed')
                    ], limit=1)
                    if not prereq_enrollment:
                        raise ValidationError(
                            f"Cannot enroll: Student has not completed prerequisite course '{prereq.name}'."
                        )

    # ==========================================================================
    # TODO 6: Implement Onchange Methods
    # ==========================================================================
    # - _onchange_course_id: Warn if course is almost full
    # - _onchange_student_id: Warn if student has low attendance rate
    # ==========================================================================
    
    # YOUR CODE HERE - Onchange methods
    def _onchange_course_id(self):
        if self.course_id:
            enrolled_count = self.search_count([
                ('course_id', '=', self.course_id.id),
                ('state', 'in', ['confirmed'])
            ])
            if enrolled_count >= self.course_id.max_students:
                return {
                    'warning': {
                        'title': "Course Full",
                        'message': "This course is already full. You cannot enroll more students."
                    }
                }
            elif enrolled_count >= self.course_id.max_students - 1:
                return {
                    'warning': {
                        'title': "Course Almost Full",
                        'message': "This course is almost full. Only one spot left!"
                    }
                }

    def _onchange_student_id(self):
        if self.student_id:
            attendance_rate = self.student_id.attendance_rate
            if attendance_rate < 0.75:
                return {
                    'warning': {
                        'title': "Low Attendance Rate",
                        'message': f"Student has a low attendance rate of {attendance_rate*100:.1f}%. Consider discussing this with the student."
                    }
                }

    # ==========================================================================
    # TODO 7: Implement State Transition Methods
    # ==========================================================================
    # - action_submit(): draft -> pending
    # - action_approve(): pending -> confirmed (check capacity)
    # - action_complete(): confirmed -> completed (set completion_date)
    # - action_cancel(): pending/confirmed -> cancelled
    # - action_drop(): confirmed -> dropped
    # - action_reset_draft(): cancelled/dropped -> draft
    # ==========================================================================
    
    def action_submit(self):
        """TODO: Submit enrollment for approval"""
        for record in self:
            # YOUR CODE HERE
            record.state = 'pending'
    
    def action_approve(self):
        """TODO: Approve enrollment (check capacity)"""
        for record in self:
            # YOUR CODE HERE
            enrolled_count = self.search_count([
                ('course_id', '=', record.course_id.id),
                ('state', 'in', ['confirmed'])
            ])
            if enrolled_count < record.course_id.max_students:
                record.state = 'confirmed'
    
    # TODO: Implement remaining action methods
    def action_complete(self):
        """TODO: Complete enrollment"""
        for record in self:
            if record.state == 'confirmed':
                record.state = 'completed'
                record.completion_date = fields.Date.today()

    def action_cancel(self):
        """Transition from pending/confirmed -> cancelled"""
        for record in self:
            if record.state not in ('pending', 'confirmed'):
                raise UserError(_("You can only cancel records that are currently pending or confirmed."))
            record.state = 'cancelled'

    def action_drop(self):
        """Transition from confirmed -> dropped"""
        for record in self:
            if record.state != 'confirmed':
                raise UserError(_("Only confirmed records can be dropped."))
            record.state = 'dropped'

    def action_reset_draft(self):
        """Transition from cancelled/dropped -> draft"""
        for record in self:
            if record.state not in ('cancelled', 'dropped'):
                raise UserError(_("Only cancelled or dropped records can be reset to draft."))
            record.state = 'draft'

    # ==========================================================================
    # TODO 8: Override CRUD Methods
    # ==========================================================================
    # - create(): Check prerequisites, check capacity, send notification
    # - write(): Track state changes
    # - unlink(): Cannot delete confirmed enrollments
    # ==========================================================================
    
    @api.model_create_multi
    def create(self, vals_list):
        """Implement create with prerequisite and capacity validations"""
        for vals in vals_list:
        # YOUR CODE HERE - Add validations before create
            course = self.env['school.course'].browse(vals.get('course_id'))
            student = self.env['school.student'].browse(vals.get('student_id'))
            
            if course:
                if hasattr(course, 'prerequisite_ids') and course.prerequisite_ids:
                    for prereq in course.prerequisite_ids:
                        completed = self.env['school.enrollment'].search_count([
                            ('student_id', '=', student.id),
                            ('course_id', '=', prereq.id),
                            ('state', '=', 'completed')
                        ])
                        if not completed:
                            raise UserError(_(
                                "Cannot enroll %s. This course requires completing the prerequisite: %s."
                            ) % (student.name, prereq.name))

                if hasattr(course, 'seats_available') and course.seats_available <= 0:
                    raise UserError(_(
                        "Cannot enroll student. The course '%s' has reached its maximum seat capacity."
                    ) % course.name)

        records = super().create(vals_list)

        for record in records:
            if hasattr(record, 'message_post'):
                record.message_post(
                    body=_("New enrollment record created for student %s in course %s.") % (record.student_id.name, record.course_id.name),
                    subtype_xmlid="mail.mt_note"
                )
        return records
    
    # TODO: Implement write and unlink overrides
        # ==========================================================================
    # TODO 8: Override CRUD Methods
    # ==========================================================================

    def write(self, vals):
        """Track state changes, log them to chatter history, and promote student status if approved"""
        state_changed = 'state' in vals
        old_states = {record.id: record.state for record in self} if state_changed else {}

        # 1. Execute the base Odoo database save routine first
        result = super().write(vals)

        # 2. Process stage changes and automatic hooks
        if state_changed:
            new_state = vals.get('state')
            for record in self:
                old_state = old_states.get(record.id)
                
                if old_state != new_state:
                    # Log the enrollment stage shift to the chatter history timeline
                    if hasattr(record, 'message_post'):
                        record.message_post(
                            body=_("Enrollment Stage Changed: From '%s' to '%s'.") % (old_state.upper(), new_state.upper()),
                            subtype_xmlid="mail.mt_note"
                        )
                    
                    # AUTOMATIC TRIGGER HOOK: Promote student from 'draft' to 'enrolled' if confirmed
                    if new_state == 'confirmed':
                        student = record.student_id
                        if student and student.state == 'draft':
                            student.write({'state': 'enrolled'})
                            
                            # Log audit note directly onto the promoted student's chatter log timeline
                            if hasattr(student, 'message_post'):
                                student.message_post(
                                    body=_("Status automatically promoted from 'Draft' to 'Enrolled' upon confirmation in course: %s.") 
                                    % record.course_id.name,
                                    subtype_xmlid="mail.mt_note"
                                )
                                
        return result

    def unlink(self):
        """Prevent deletion of confirmed enrollment records"""
        for record in self:
            if record.state == 'confirmed':
                raise UserError(_(
                    "Security Restriction: You cannot delete an enrollment record that has already been 'Confirmed'. Please cancel or drop it instead."
                ))
        return super().unlink()

    
    # ==========================================================================
    # TODO 9: Implement Business Methods
    # ==========================================================================
    # - check_prerequisites(): Returns True if student meets course prerequisites
    # - calculate_final_grade(): Calculate and return final grade for enrollment
    # - send_confirmation_email(): Send confirmation email to student
    # - generate_certificate(): Generate completion certificate
    # ==========================================================================
    
    def check_prerequisites(self):
            """
            Returns True if student meets all course prerequisites.
            Can be called manually from a button or UI check.
            """
            self.ensure_one()
            if not self.course_id or not self.student_id:
                return False
    
            if not hasattr(self.course_id, 'prerequisite_ids') or not self.course_id.prerequisite_ids:
                return True
    
            for prereq in self.course_id.prerequisite_ids:
                completed = self.env['school.enrollment'].search_count([
                    ('student_id', '=', self.student_id.id),
                    ('course_id', '=', prereq.id),
                    ('state', '=', 'completed')
                ])
                if not completed:
                    return False
            return True
    
    # TODO: Implement remaining methods
    def calculate_final_grade(self):
        """
        Calculates and returns final grade for enrollment.
        Assumes grades are tracked in a child model or linked lines (e.g., school.grade).
        """
        self.ensure_one()
        grade_records = self.env['school.grade'].search([('enrollment_id', '=', self.id)])
        
        if not grade_records:
            return 0.0

        total_score = sum(grade.score for grade in grade_records)
        final_grade = total_score / len(grade_records)
        
        if hasattr(self, 'final_grade'):
            self.final_grade = final_grade
            
        return final_grade

    def send_confirmation_email(self):
        """
        Send confirmation email to student using Odoo's mail template system.
        """
        self.ensure_one()
        template = self.env.ref('school_management_training.email_template_enrollment_confirmation', raise_if_not_found=False)
        
        if template:
            template.send_mail(self.id, force_send=True)
        else:
            if hasattr(self, 'message_post'):
                self.message_post(body=_("Confirmation email triggered safely, but explicit mail template record was missing."))
        return True

    def generate_certificate(self):
        """
        Generate completion certificate PDF action report.
        """
        self.ensure_one()
        if self.state != 'completed':
            raise UserError(_("Certificates can only be generated for students who have successfully completed the course."))

        return self.env.ref('school_management_training.action_report_school_certificate').report_action(self)