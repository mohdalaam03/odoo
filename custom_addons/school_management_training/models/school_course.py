# -*- coding: utf-8 -*-
# =============================================================================
# COURSE MODEL
# =============================================================================
# This model represents courses offered by the school.
# Complete all TODO items to implement the full functionality.
# =============================================================================

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class SchoolCourse(models.Model):
    """
    Course Model
    
    Concepts covered:
    - Default values with context
    - Domain constraints on fields
    - Recursive relationships (prerequisites)
    - Inverse fields
    - Method decorators (@api.model, @api.depends, etc.)
    """
    _name = 'school.course'
    _description = 'Course'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'code asc'
    
    # ==========================================================================
    # TODO 1: Define Basic Fields
    # ==========================================================================
    # Add the following fields:
    # - code: Char field, required, size=10
    # - name: Char field, required, tracking=True, translate=True
    # - description: Html field, translate=True
    # - credits: Integer field, required, default=3
    # - max_students: Integer field, default=30
    # - min_students: Integer field, default=5
    # - hours_per_week: Float field, digits=(4, 1)
    # - is_mandatory: Boolean field
    # - level: Selection (beginner, intermediate, advanced)
    # - start_date: Date field
    # - end_date: Date field
    # - active: Boolean, default=True
    # ==========================================================================
    
    # YOUR CODE HERE - Basic Fields
    code = fields.Char(
        string='Course Code',
        required=True,
        size=10,
        tracking=True,
    )
    # TODO: Add remaining basic fields
    name = fields.Char(string='Course Name', required=True, tracking=True, translate=True)
    description = fields.Html(string='Description', translate=True)
    credits = fields.Integer(string='Credits', required=True, default=3)
    max_students = fields.Integer(string='Max Students', default=30)
    min_students = fields.Integer(string='Min Students', default=5)
    hours_per_week = fields.Float(string='Hours per Week', digits=(4, 1))
    is_mandatory = fields.Boolean(string='Is Mandatory')
    level = fields.Selection([
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced')
    ], string='Level')
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    active = fields.Boolean(string='Active', default=True)

    # ==========================================================================
    # TODO 2: Define Relational Fields
    # ==========================================================================
    # Add the following fields:
    # - teacher_id: Many2one to 'school.teacher', tracking=True
    # - enrollment_ids: One2many to 'school.enrollment' (inverse: course_id)
    # - student_ids: Many2many to 'school.student' (computed or through relation)
    # - grade_ids: One2many to 'school.grade' (inverse: course_id)
    # - prerequisite_ids: Many2many to 'school.course' (self-referential for prerequisites)
    # - category_id: Many2one to 'school.course.category'
    # - tag_ids: Many2many to 'school.course.tag'
    # ==========================================================================
    
    # YOUR CODE HERE - Relational Fields
    teacher_id = fields.Many2one('school.teacher', string='Teacher', tracking=True)
    enrollment_ids = fields.One2many('school.enrollment', 'course_id', string='Enrollments')
    student_ids = fields.Many2many('school.student', 'student_course_rel', 'student_id', 'course_id', string='Students')
    grade_ids = fields.One2many('school.grade', 'course_id', string='Grades')
    prerequisite_ids = fields.Many2many('school.course', 'course_prerequisite_rel', 'course_id', 'prerequisite_id', string='Prerequisites')
    category_id = fields.Many2one('school.course.category', string='Category')
    tag_ids = fields.Many2many('school.course.tag', 'course_tag_rel', 'course_id', 'tag_id', string='Tags')

    # ==========================================================================
    # TODO 3: Define State Field with Workflow
    # ==========================================================================
    # Add state field with states:
    # - draft: Draft
    # - planned: Planned  
    # - in_progress: In Progress
    # - completed: Completed
    # - cancelled: Cancelled
    # ==========================================================================
    
    # YOUR CODE HERE - State Field
    state = fields.Selection([
        ('draft', 'Draft'),
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string='State', default='draft')

    # ==========================================================================
    # TODO 4: Define Computed Fields
    # ==========================================================================
    # Implement:
    # - enrolled_count: Integer, count of confirmed enrollments
    # - available_seats: Integer, max_students - enrolled_count
    # - is_full: Boolean, True if available_seats <= 0
    # - progress_percentage: Float, percentage of course completion based on dates
    # - average_grade: Float, average of all grades for this course
    # ==========================================================================
    
    

    # TODO: Add remaining computed fields
    grade_count = fields.Integer(
        string='Grade Count',
        compute='_compute_grade_count_stat',
    )
    enrolled_count = fields.Integer(
        string='Enrolled Students',
        compute='_compute_enrollment_stats',
        store=True,
    )
    available_seats = fields.Integer(
        string='Available Seats',
        compute='_compute_enrollment_stats',
        store=True
    )
    is_full = fields.Boolean(
        string='Is Full',
        compute='_compute_enrollment_stats',
        store=True
    )
    progress_percentage = fields.Float(
        string='Progress Percentage',
        compute='_compute_progress_percentage',
        store=True
    )
    average_grade = fields.Float(
        string='Average Grade',
        compute='_compute_average_grade',
        store=True
    )

    @api.depends('enrollment_ids', 'enrollment_ids.state', 'max_students')
    def _compute_enrollment_stats(self):
        """
        TODO: Implement enrollment statistics computation
        Calculate enrolled_count, available_seats, is_full
        """
        for record in self:
            # YOUR CODE HERE
            confirmed_count = len(record.enrollment_ids.filtered(lambda e: e.state == 'confirmed'))
            
            record.enrolled_count = confirmed_count
            
            record.available_seats = record.max_students - confirmed_count
            record.is_full = record.available_seats <= 0

    # TODO: Implement remaining compute methods
    @api.depends('start_date', 'end_date')
    def _compute_progress_percentage(self):
        """
        Computes course completion progress based on elapsed time.
        Clamps boundaries between 0.0% and 100.0% to prevent logical overflow.
        """
        today = fields.Date.today()
        for record in self:
            if record.start_date and record.end_date:
                total_days = (record.end_date - record.start_date).days
                
                if total_days > 0:
                    elapsed_days = (today - record.start_date).days
                    raw_percentage = (elapsed_days / total_days) * 100.0
                    
                    record.progress_percentage = max(0.0, min(raw_percentage, 100.0))
                else:
                    record.progress_percentage = 100.0 if today >= record.end_date else 0.0
            else:
                record.progress_percentage = 0.0

    @api.depends('grade_ids.score', 'grade_ids.max_score')
    def _compute_average_grade(self):
        """
        Computes the course class average as a true percentage.
        Compares cumulative points earned by all students against total possible points.
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


    @api.depends('grade_ids')
    def _compute_grade_count_stat(self):
        for record in self:
            # Counts the number of total grade records linked to this course
            if getattr(record, 'grade_ids', False):
                record.grade_count = len(record.grade_ids)
            else:
                record.grade_count = 0

    # ==========================================================================
    # TODO 5: Define Constraints
    # ==========================================================================
    # SQL Constraints:
    # - unique_code: code must be unique
    # - check_credits: credits must be between 1 and 10
    # - check_max_students: max_students must be positive
    #
    # Python Constraints:
    # - end_date must be after start_date
    # - min_students must be less than max_students
    # - prerequisites cannot include self
    # ==========================================================================
    
    _sql_constraints = [
        # YOUR CODE HERE
        ('unique_code', 'unique(code)', 'Course code must be unique!'),
        ('check_credits', 'CHECK (credits >= 1 AND credits <= 10)', 'Credits must be between 1 and 10!'),
        ('check_max_students', 'CHECK (max_students > 0)', 'Max students must be positive!'),
    ]
    
    # YOUR CODE HERE - Python constraints
    @api.constrains('end_date', 'start_date')
    def _check_date_order(self):
        for record in self:
            if record.start_date and record.end_date:
                if record.end_date < record.start_date:
                    raise models.ValidationError("End date must be after start date!")

    @api.constrains('min_students', 'max_students')
    def _check_student_limits(self):
        for record in self:
            if record.min_students >= record.max_students:
                raise models.ValidationError("Minimum students must be less than maximum students!")

    @api.constrains('prerequisite_ids')
    def _check_prerequisites(self):
        for record in self:
            if record.id in record.prerequisite_ids.ids:
                raise models.ValidationError("Prerequisites cannot include self!")

    # ==========================================================================
    # TODO 6: Implement State Transition Methods
    # ==========================================================================
    # - action_plan(): draft -> planned (requires teacher_id)
    # - action_start(): planned -> in_progress (requires min_students enrolled)
    # - action_complete(): in_progress -> completed
    # - action_cancel(): any -> cancelled (unless completed)
    # - action_reset_draft(): cancelled -> draft
    # ==========================================================================
    
    def action_plan(self):
        """TODO: Implement plan action"""
        for record in self:
            # YOUR CODE HERE
            if record.state != 'draft':
                raise UserError(_("Only draft courses can be planned."))
            if not record.teacher_id:
                raise UserError(_("You must assign a Teacher before planning this course."))
            record.state = 'planned'
    
    # TODO: Implement remaining action methods
        # ==========================================================================
    # TODO 6: State Transition Methods
    # ==========================================================================

    def action_start(self):
        """Transition from planned -> in_progress (requires min_students enrolled)"""
        for record in self:
            if record.state != 'planned':
                raise UserError(_("Only planned courses can be started."))
            if record.enrolled_count < record.min_students:
                raise UserError(_("You must have at least %s enrolled students to start this course.") % record.min_students)
            record.state = 'in_progress'

    def action_complete(self):
        """Transition from in_progress -> completed"""
        for record in self:
            if record.state != 'in_progress':
                raise UserError(_("Only courses currently in progress can be marked completed."))
            record.state = 'completed'

    def action_cancel(self):
        """Transition from any -> cancelled (unless completed)"""
        for record in self:
            if record.state == 'completed':
                raise UserError(_("You cannot cancel a course that has already been completed."))
            record.state = 'cancelled'

    def action_reset_draft(self):
        """Transition from cancelled -> draft"""
        for record in self:
            if record.state != 'cancelled':
                raise UserError(_("Only cancelled courses can be reset to draft."))
            record.state = 'draft'

    def action_view_enrollments(self):
        """
        Triggered by the XML stat button on the Course form.
        Opens a filtered view containing only the enrollment rows for this specific course.
        """
        self.ensure_one()
        return {
            'name': _('Course Enrollments'),
            'type': 'ir.actions.act_window',
            'res_model': 'school.enrollment', 
            'view_mode': 'list,form',
            'domain': [('course_id', '=', self.id)],
            'context': {
                'default_course_id': self.id,
                'search_default_course_id': self.id,
            },
        }

    def action_view_grades(self):
        """
        Triggered by the XML stat button on the Course form.
        Opens a filtered window containing only the grade slips for this specific course.
        """
        self.ensure_one()
        return {
            'name': _('Course Grades'),
            'type': 'ir.actions.act_window',
            'res_model': 'school.grade',  
            'view_mode': 'list,form,pivot,graph',  
            'domain': [('course_id', '=', self.id)],
            'context': {
                'default_course_id': self.id,
                'search_default_course_id': self.id,
            },
        }

    # ==========================================================================
    # TODO 7: Implement Business Methods
    # ==========================================================================
    # - get_eligible_students(): Returns students who meet prerequisites
    # - check_prerequisites(student): Returns True if student meets prerequisites
    # - get_schedule(): Returns schedule information
    # - clone_for_next_term(): Creates copy for next academic term
    # ==========================================================================
    
    def get_eligible_students(self):
        """TODO: Return students eligible to enroll (meet prerequisites)"""
        self.ensure_one()
        return self.env['school.student']
    
    # TODO: Implement remaining methods
    def check_prerequisites(self, student):
        """TODO: Check if a student meets the prerequisites for this course"""
        self.ensure_one()
        return True

    def get_schedule(self):
        """TODO: Return schedule information for this course"""
        self.ensure_one()
        return {
            'start_date': self.start_date,
            'end_date': self.end_date,
            'hours_per_week': self.hours_per_week,
        }

    def clone_for_next_term(self):
        """TODO: Create a copy of this course for the next academic term"""
        self.ensure_one()
        return self.copy()


class SchoolCourseCategory(models.Model):
    """
    Course Category Model (for grouping courses)
    
    Concepts covered:
    - Parent/child hierarchy
    - Recursive name computation
    - Complete name with parent path
    """
    _name = 'school.course.category'
    _description = 'Course Category'
    _parent_name = 'parent_id'
    _parent_store = True
    _order = 'complete_name asc'
    
    # ==========================================================================
    # TODO 8: Define Category Fields
    # ==========================================================================
    # - name: Char, required
    # - parent_id: Many2one to self
    # - child_ids: One2many to self
    # - parent_path: Char (for parent_store)
    # - complete_name: Char, computed (shows full path like "Parent / Child")
    # - course_ids: One2many to 'school.course'
    # - course_count: Integer, computed count of courses
    # ==========================================================================
    
    name = fields.Char(string='Name', required=True)
    # TODO: Add remaining fields
    parent_id = fields.Many2one('school.course.category', string='Parent Category', ondelete='restrict')
    child_ids = fields.One2many('school.course.category', 'parent_id', string='Child Categories')
    parent_path = fields.Char(index=True)
    complete_name = fields.Char(string='Complete Name', compute='_compute_complete_name', store=True)
    course_ids = fields.One2many('school.course', 'category_id', string='Courses')
    course_count = fields.Integer(string='Course Count', compute='_compute_course_count', store=True)

    # TODO: Implement _compute_complete_name
    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for category in self:
            if category.parent_id:
                category.complete_name = f"{category.parent_id.complete_name} / {category.name}"
            else:
                category.complete_name = category.name

    # TODO: Add SQL constraint for parent not being self
    _sql_constraints = [
        ('parent_not_self', 'CHECK(parent_id != id)', 'Parent category cannot be the category itself!')
    ]

class SchoolCourseTag(models.Model):
    """
    Course Tags Model (for labeling courses)
    
    Concepts covered:
    - Simple tagging model
    - Color field for kanban
    """
    _name = 'school.course.tag'
    _description = 'Course Tag'
    _order = 'name asc'
    
    # ==========================================================================
    # TODO 9: Define Tag Fields
    # ==========================================================================
    # - name: Char, required
    # - color: Integer (for kanban color)
    # - course_ids: Many2many to 'school.course'
    # ==========================================================================
    
    name = fields.Char(string='Name', required=True)
    # TODO: Add remaining fields
    color = fields.Integer(string='Color', default=10)
    course_ids = fields.Many2many('school.course', 'course_tag_rel', 'tag_id', 'course_id', string='Courses')