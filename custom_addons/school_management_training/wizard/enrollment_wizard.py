# -*- coding: utf-8 -*-
# =============================================================================
# ENROLLMENT WIZARD
# =============================================================================
# This wizard handles bulk enrollment of students in courses.
# Complete all TODO items to implement the full functionality.
# =============================================================================

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class EnrollmentWizard(models.TransientModel):
    """
    Enrollment Wizard
    
    A transient model for bulk enrolling students in courses.
    
    Concepts covered:
    - TransientModel usage
    - Wizard workflow
    - Context handling
    - Multiple record processing
    - Return actions
    """
    _name = 'school.enrollment.wizard'
    _description = 'Bulk Enrollment Wizard'
    
    # ==========================================================================
    # TODO 1: Define Wizard Fields
    # ==========================================================================
    # Add the following fields:
    # - course_id: Many2one to 'school.course', required
    # - student_ids: Many2many to 'school.student'
    # - enrollment_date: Date, default=today
    # - send_notification: Boolean, default=True
    # - skip_prerequisites: Boolean, default=False
    # - notes: Text
    # ==========================================================================
    
    # YOUR CODE HERE - Wizard Fields
    course_id = fields.Many2one(
        comodel_name='school.course',
        string='Course',
        required=True,
    )
    # TODO: Add remaining fields
    student_ids = fields.Many2many(
        comodel_name='school.student',
        string='Students',
    )
    enrollment_date = fields.Date(
        string='Enrollment Date',
        default=fields.Date.today,
    )
    send_notification = fields.Boolean(
        string='Send Notification',
        default=True,
    )
    skip_prerequisites = fields.Boolean(
        string='Skip Prerequisites',
        default=False,
    )
    notes = fields.Text(
        string='Notes',
    )

    # ==========================================================================
    # TODO 2: Define Default Methods
    # ==========================================================================
    # - _default_course_id: Get course from context if available
    # - _default_student_ids: Get students from context (active_ids)
    # ==========================================================================
    
    @api.model
    def default_get(self, fields_list):
        """
        TODO: Override default_get to set defaults from context
        - If called from a course, set course_id
        - If called from student list, set student_ids
        """
        res = super().default_get(fields_list)
        
        # YOUR CODE HERE
        # Check context for 'active_model' and 'active_ids'
        active_model = self.env.context.get('active_model')
        active_id = self.env.context.get('active_id')
        
        if active_id and active_model == 'school.course':
            res['course_id'] = active_id
            
            enrollments = self.env['school.enrollment'].search([
                ('course_id', '=', active_id),
                ('state', 'in', ('confirmed', 'pending'))
            ])
            
            line_values = []
            for enrollment in enrollments:
                line_values.append((0, 0, {
                    'student_id': enrollment.student_id.id,
                    'status': 'absent',
                    'remarks': ''
                }))
                
            if line_values:
                res['line_ids'] = line_values
                
        return res
    
    
    # ==========================================================================
    # TODO 3: Define Computed Fields
    # ==========================================================================
    # - available_seats: Integer, computed from course capacity
    # - student_count: Integer, count of selected students
    # - can_enroll_all: Boolean, True if all students can be enrolled
    # - warning_message: Text, computed warnings about capacity, prerequisites
    # ==========================================================================
    
    # YOUR CODE HERE - Computed fields
    available_seats = fields.Integer(
        string='Available Seats',
        compute='_compute_available_seats'
    )
    student_count = fields.Integer(
        string='Number of Students',
        compute='_compute_student_count'
    )
    can_enroll_all = fields.Boolean(
        string='Can Enroll All',
        compute='_compute_can_enroll_all'
    )
    warning_message = fields.Text(
        string='Warning Message',
        compute='_compute_warning_message'
    )

    @api.depends('course_id')
    def _compute_available_seats(self):
        """Calculates current available seats directly from the selected course profile"""
        for wizard in self:
            if wizard.course_id:
                # Fallback check to support any seat naming convention used across your project models
                if hasattr(wizard.course_id, 'available_seats'):
                    wizard.available_seats = wizard.course_id.available_seats
                elif hasattr(wizard.course_id, 'seats_available'):
                    wizard.available_seats = wizard.course_id.seats_available
                else:
                    wizard.available_seats = wizard.course_id.max_students - wizard.course_id.enrolled_count
            else:
                wizard.available_seats = 0

    @api.depends('student_ids')
    def _compute_student_count(self):
        """Counts how many total student rows are currently selected inside the wizard"""
        for wizard in self:
            wizard.student_count = len(wizard.student_ids) if wizard.student_ids else 0

    @api.depends('available_seats', 'student_count')
    def _compute_can_enroll_all(self):
        """Determines if the class capacity constraints can fully support all selected candidates"""
        for wizard in self:
            wizard.can_enroll_all = wizard.student_count <= wizard.available_seats

    @api.depends('course_id', 'student_ids', 'available_seats', 'student_count', 'skip_prerequisites')
    def _compute_warning_message(self):
        """Generates contextual warning strings inside the wizard modal banner area dynamically"""
        for wizard in self:
            warnings = []

            # 1. Capacity Mismatch Warning Layer Validation
            if wizard.student_count > wizard.available_seats:
                warnings.append(_(
                    "Capacity Limit Alert: You have selected %s students but only %s seats remain open."
                ) % (wizard.student_count, wizard.available_seats))

            # 2. Prerequisite Check Warning Layer Validation
            if wizard.course_id and wizard.student_ids and not wizard.skip_prerequisites:
                if hasattr(wizard.course_id, 'prerequisite_ids') and wizard.course_id.prerequisite_ids:
                    prereq_ids = wizard.course_id.prerequisite_ids.ids
                    
                    for student in wizard.student_ids:
                        # Count completed matching prerequisites courses for this candidate
                        completed_count = self.env['school.enrollment'].search_count([
                            ('student_id', '=', student.id),
                            ('course_id', 'in', prereq_ids),
                            ('state', '=', 'completed')
                        ])
                        
                        if completed_count < len(prereq_ids):
                            warnings.append(_(
                                "Prerequisite Gap: Student '%s' has not finalized all prerequisite course units required."
                            ) % (student.display_name or student.name))

            # Join all discovered issues into a single clean text block banner layout
            if warnings:
                wizard.warning_message = "\n".join(warnings)
            else:
                wizard.warning_message = False

    # ==========================================================================
    # TODO 4: Implement Onchange Methods
    # ==========================================================================
    # - _onchange_course_id: Clear students that don't meet prerequisites
    # - _onchange_student_ids: Show warning if too many students selected
    # ==========================================================================
    
    # YOUR CODE HERE - Onchange methods
    @api.onchange('course_id')
    def _onchange_course_id(self):
        if self.course_id:
            self.student_ids = [(5, 0, 0)]  # Clear existing students

    @api.onchange('student_ids')
    def _onchange_student_ids(self):
        if self.course_id and self.student_ids:
            if len(self.student_ids) > self.available_seats:
                return {
                    'warning': {
                        'title': _('Capacity Warning'),
                        'message': _('Selected students exceed available seats.'),
                    }
                }
            
    # ==========================================================================
    # TODO 5: Implement Action Methods
    # ==========================================================================
    # - action_enroll(): Main action to create enrollments
    #   * Validate capacity
    #   * Check prerequisites (unless skip_prerequisites)
    #   * Create enrollment records
    #   * Send notifications if enabled
    #   * Return action to show created enrollments
    #
    # - action_enroll_and_new(): Enroll and open new wizard
    #
    # - action_cancel(): Close wizard
    # ==========================================================================
    
    def action_enroll(self):
        """
        Bulk enrollment action
        1. Validate inputs
        2. Check course capacity
        3. Check prerequisites for each student
        4. Create enrollment records
        5. Send notifications
        6. Return action to view created enrollments
        """
        self.ensure_one()
        
        if not self.course_id or not self.student_ids:
            raise UserError(_("Please select a Course and at least one Student."))

        if hasattr(self.course_id, 'available_seats'):
            seats_left = self.course_id.available_seats
        elif hasattr(self.course_id, 'seats_available'):
            seats_left = self.course_id.seats_available
        else:
            seats_left = self.course_id.max_students - getattr(self.course_id, 'enrolled_count', 0)

        requested_seats = len(self.student_ids)

        if not self.skip_prerequisites:
            if seats_left < requested_seats:
                raise UserError(_(
                    "Capacity Blocked: The course '%s' only has %s seats left, but you are trying to enroll %s students. "
                    "Toggle 'Skip Prerequisites' to force-override capacity boundaries if authorized."
                ) % (self.course_id.name, seats_left, requested_seats))

        enrollment_records = self.env['school.enrollment']
        check_prereqs = hasattr(self, 'skip_prerequisites') and not self.skip_prerequisites

        for student in self.student_ids:
            if check_prereqs and hasattr(self.course_id, 'prerequisite_ids') and self.course_id.prerequisite_ids:
                for prereq in self.course_id.prerequisite_ids:
                    completed = self.env['school.enrollment'].search_count([
                        ('student_id', '=', student.id),
                        ('course_id', '=', prereq.id),
                        ('state', '=', 'completed')
                    ])
                    if not completed:
                        raise UserError(_(
                            "Prerequisite Error: Student %s has not completed the required prerequisite: %s."
                        ) % (student.display_name or student.name, prereq.name))

            new_enrollment = self.env['school.enrollment'].create({
                'student_id': student.id,
                'course_id': self.course_id.id,
                'state': 'pending', 
            })
            enrollment_records |= new_enrollment

            if getattr(self, 'send_notifications', False) and hasattr(new_enrollment, 'message_post'):
                new_enrollment.message_post(
                    body=_("Student %s enrolled via processing wizard tool.") % (student.display_name or student.name),
                    subtype_xmlid="mail.mt_note"
                )

        try:
            action_id = "school_management_training.action_school_enrollment"
            if not self.env.ref(action_id, raise_if_not_found=False):
                action_id = "school_management_training.view_school_enrollment_action"
            
            action = self.env["ir.actions.actions"]._for_xml_id(action_id)
            
            if len(enrollment_records) == 1:
                action.update({
                    'view_mode': 'form',
                    'res_id': enrollment_records.id,
                    'views': [(False, 'form')],
                })
            else:
                action.update({
                    'view_mode': 'list,form',
                    'domain': [('id', 'in', enrollment_records.ids)],
                })
            return action

        except Exception:
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }
    
    def action_enroll_and_new(self):
        """TODO: Enroll students and open a new wizard"""
        self.action_enroll()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Bulk Enrollment'),
            'res_model': 'school.enrollment.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': self.env.context,
        }
    
    def action_cancel(self):
        """Close the wizard"""
        return {'type': 'ir.actions.act_window_close'}
    
    
    # ==========================================================================
    # TODO 6: Implement Helper Methods
    # ==========================================================================
    # - _check_prerequisites(student): Check if student meets prerequisites
    # - _get_eligible_students(): Filter students who can enroll
    # - _send_enrollment_notifications(enrollments): Send email notifications
    # ==========================================================================
    
    def _check_prerequisites(self, student):
        """TODO: Check if a student meets course prerequisites"""
        self.ensure_one()
        # YOUR CODE HERE
        if not self.course_id.prerequisite_ids:
            return True
        for prereq in self.course_id.prerequisite_ids:
            completed = self.env['school.enrollment'].search_count([
                ('student_id', '=', student.id),
                ('course_id', '=', prereq.id),
                ('state', '=', 'completed')
            ])
            if not completed:
                return False
        return True
    
    # TODO: Implement remaining helper methods
    def _get_eligible_students(self):
        """TODO: Get list of students eligible for enrollment"""
        self.ensure_one()
        eligible_students = self.student_ids.filtered(lambda s: self._check_prerequisites(s))
        return eligible_students

    def _send_enrollment_notifications(self, enrollments):
        """TODO: Send email notifications for enrolled students"""
        for enrollment in enrollments:
            if hasattr(enrollment, 'message_post'):
                enrollment.message_post(
                    body=_("Student %s has been enrolled in course %s.") % (enrollment.student_id.name, enrollment.course_id.name),
                    subtype_xmlid="mail.mt_note"
                )

class BulkGradeWizard(models.TransientModel):
    """
    Bulk Grade Entry Wizard
    
    Allows teachers to enter grades for multiple students at once.
    
    Concepts covered:
    - Wizard with line items
    - Dynamic form generation
    - One2many in transient models
    """
    _name = 'school.bulk.grade.wizard'
    _description = 'Bulk Grade Entry Wizard'
    
    # ==========================================================================
    # TODO 7: Define Bulk Grade Wizard Fields
    # ==========================================================================
    # - course_id: Many2one to 'school.course', required
    # - grade_date: Date, required, default=today
    # - grade_type: Selection (exam, quiz, assignment, etc.)
    # - max_score: Float, default=100
    # - description: Char
    # - line_ids: One2many to 'school.bulk.grade.wizard.line'
    # ==========================================================================
    
    course_id = fields.Many2one(
        comodel_name='school.course',
        string='Course',
        required=True,
    )
    # TODO: Add remaining fields
    grade_date = fields.Date(
        string='Grade Date',
        required=True,
        default=fields.Date.today
    )
    grade_type = fields.Selection(
        selection=[
            ('exam', 'Exam'),
            ('quiz', 'Quiz'),
            ('assignment', 'Assignment'),
            ('project', 'Project'),
            ('participation', 'Participation'),
            ('final', 'Final'),
        ], 
        string='Grade Type',
        default='exam',
        required=True
    )
    max_score = fields.Float(
        string='Max Score',
        default=100.0
    )
    description = fields.Char(
        string='Description'
    )
    line_ids = fields.One2many(
        comodel_name='school.bulk.grade.wizard.line',
        inverse_name='wizard_id',
        string='Grades'
    )

    # ==========================================================================
    # TODO 8: Implement Wizard Actions
    # ==========================================================================
    # - action_load_students(): Load enrolled students into line_ids
    # - action_save_grades(): Create grade records from line_ids
    # ==========================================================================
    
    def action_load_students(self):
        """TODO: Load enrolled students for grade entry"""
        self.ensure_one()
        # YOUR CODE HERE
        if not self.course_id:
            return False

        self.line_ids.unlink()
        
        enrollments = self.env['school.enrollment'].search([
            ('course_id', '=', self.course_id.id),
            ('state', 'in', ('confirmed', 'pending'))
        ])

        line_values = []
        for enrollment in enrollments:
            line_values.append((0, 0, {
                'student_id': enrollment.student_id.id,
                'score': 0.0,
                'feedback': '',
            }))

        if line_values:
            self.write({'line_ids': line_values})

        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }
            
    def action_save_grades(self):
        """TODO: Save all entered grades"""
        self.ensure_one()
        # YOUR CODE HERE
        for line in self.line_ids:
            self.env['school.grade'].create({
                'student_id': line.student_id.id,
                'course_id': self.course_id.id,
                'date': self.grade_date,
                'grade_type': self.grade_type,
                'max_score': self.max_score,
                'description': self.description,
                'score': line.score,
                'feedback': line.feedback
            })

    @api.onchange('course_id')
    def _onchange_course_id_load_students(self):
        """
        Triggers automatically when a user picks or changes 
        the course selection dropdown in the wizard window.
        """
        if not self.course_id:
            self.line_ids = [(5, 0, 0)]  
            return

        enrollments = self.env['school.enrollment'].search([
            ('course_id', '=', self.course_id.id),
            ('state', 'in', ('confirmed', 'pending'))
        ])

        line_values = []
        for enrollment in enrollments:
            line_values.append((0, 0, {
                'student_id': enrollment.student_id.id,
                'score': 0.0,
                'feedback': '',
            }))

        self.line_ids = [(5, 0, 0)] + line_values


class BulkGradeWizardLine(models.TransientModel):
    """Line items for bulk grade entry"""
    _name = 'school.bulk.grade.wizard.line'
    _description = 'Bulk Grade Entry Line'
    
    # ==========================================================================
    # TODO 9: Define Line Fields
    # ==========================================================================
    # - wizard_id: Many2one to 'school.bulk.grade.wizard'
    # - student_id: Many2one to 'school.student', required
    # - score: Float
    # - feedback: Text
    # ==========================================================================
    
    wizard_id = fields.Many2one(
        comodel_name='school.bulk.grade.wizard',
        string='Wizard',
        required=True,
        ondelete='cascade',
    )
    student_id = fields.Many2one(
        comodel_name='school.student',
        string='Student',
        readonly=True,
        required=True
    )
    score = fields.Float(
        string='Score'
    )
    feedback = fields.Text(
        string='Feedback'
    )


class BulkAttendanceWizard(models.TransientModel):
    """
    Bulk Attendance Wizard
    
    Allows marking attendance for multiple students at once.
    """
    _name = 'school.bulk.attendance.wizard'
    _description = 'Bulk Attendance Wizard'
    
    course_id = fields.Many2one(
        comodel_name='school.course',
        string='Course',
        required=True,
    )
    attendance_date = fields.Date(
        string='Date',
        required=True,
        default=fields.Date.today,
    )
    line_ids = fields.One2many(
        comodel_name='school.bulk.attendance.wizard.line',
        inverse_name='wizard_id',
        string='Attendance Lines'
    )
    check_in = fields.Datetime(string='Check In')
    check_out = fields.Datetime(string='Check Out')

    @api.model
    def default_get(self, fields_list):
        """Pre-populates student lines dynamically upon modal view opening with a safe fallback radar"""
        res = super(BulkAttendanceWizard, self).default_get(fields_list)
        
        active_id = self.env.context.get('active_id') or self.env.context.get('default_course_id')
        
        if active_id:
            res['course_id'] = active_id
            
            enrollments = self.env['school.enrollment'].search([
                ('course_id', '=', active_id),
                ('state', 'in', ('confirmed', 'pending'))
            ])
            
            line_values = []
            for enrollment in enrollments:
                if enrollment.student_id:
                    line_values.append((0, 0, {
                    'student_id': enrollment.student_id.id,
                    'status': 'absent',
                    }))
                
            if line_values:
                res['line_ids'] = line_values

        # raise UserError(
        #     "\n".join(
        #     f"Enrollment {e.id}: Student={e.student_id.id if e.student_id else False}"
        #     for e in enrollments
        #     )
        # )
        return res

    def action_mark_all_present(self):
        self.ensure_one()
        
        self.line_ids.write({
        'status': 'present',
        })
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }

    def action_save_attendance(self):
        """Triggered by the 'Save Attendance' footer button"""
        self.ensure_one()
        for line in self.line_ids:
            self.env['school.attendance'].create({
                'student_id': line.student_id.id,
                'course_id': self.course_id.id,
                'date': self.attendance_date,
                'status': line.status,
                'remarks': line.remarks,
                'check_in': self.check_in,
                'check_out': self.check_out,
            })
        return {'type': 'ir.actions.act_window_close'}


class BulkAttendanceWizardLine(models.TransientModel):
    """Line items for bulk attendance"""
    _name = 'school.bulk.attendance.wizard.line'
    _description = 'Bulk Attendance Line'
    
    wizard_id = fields.Many2one(
        comodel_name='school.bulk.attendance.wizard',
        string='Wizard',
        required=True,
        ondelete='cascade',
    )
    student_id = fields.Many2one(
        comodel_name='school.student',
        required=True,
        readonly=True,
    )
    status = fields.Selection(
        selection=[('present', 'Present'), ('absent', 'Absent')],
        string='Status',
        default='absent'
    )
    check_in = fields.Datetime(string='Check In')
    check_out = fields.Datetime(string='Check Out')
    remarks = fields.Text(string='Remarks')

