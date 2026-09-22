# -*- coding: utf-8 -*-
# =============================================================================
# GRADE MODEL
# =============================================================================
# This model handles student grades for courses.
# Complete all TODO items to implement the full functionality.
# =============================================================================

from datetime import date

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class SchoolGrade(models.Model):
    """
    Grade Model
    
    Tracks grades/scores for students in courses.
    
    Concepts covered:
    - Float field with digits precision
    - Selection computed from score
    - Related fields usage
    - Aggregation with read_group
    """
    _name = 'school.grade'
    _description = 'Student Grade'
    _inherit = ['mail.thread']
    _order = 'date desc, id desc'
    _rec_name = 'display_name'
    
    # ==========================================================================
    # TODO 1: Define Basic Fields
    # ==========================================================================
    # Add the following fields:
    # - date: Date, required, default=today
    # - score: Float, required, digits=(5, 2)
    # - max_score: Float, required, default=100, digits=(5, 2)
    # - weight: Float, default=1.0 (for weighted average calculations)
    # - grade_type: Selection (exam, quiz, assignment, project, participation, final)
    # - description: Char (e.g., "Midterm Exam", "Quiz 1")
    # - feedback: Text (teacher's feedback)
    # ==========================================================================
    
    # YOUR CODE HERE - Basic Fields
    date = fields.Date(
        string='Date',
        required=True,
        default=fields.Date.today,
    )
    # TODO: Add remaining basic fields
    score = fields.Float(
        string='Score',
        required=True,
        digits=(5, 2)
    )
    max_score = fields.Float(
        string='Maximum Score',
        required=True,
        default=100.0,
        digits=(5, 2)
    )
    weight = fields.Float(
        string='Weight',
        default=1.0
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
        default='exam',
        string='Grade Type',
        required=True
    )
    description = fields.Char(
        string='Description'
    )
    feedback = fields.Text(
        string='Feedback'
    )

    # ==========================================================================
    # TODO 2: Define Relational Fields
    # ==========================================================================
    # - student_id: Many2one to 'school.student', required, ondelete='cascade'
    # - course_id: Many2one to 'school.course', required, ondelete='cascade'
    # - teacher_id: Many2one to 'school.teacher' (who gave the grade)
    # - enrollment_id: Many2one to 'school.enrollment' (find matching enrollment)
    # ==========================================================================
    
    # YOUR CODE HERE - Relational Fields
    student_id = fields.Many2one(
        comodel_name='school.student',
        string='Student',
        required=True,
        ondelete='cascade'
    )
    course_id = fields.Many2one(
        comodel_name='school.course',
        string='Course',
        required=True,
        ondelete='cascade'
    )
    teacher_id = fields.Many2one(
        comodel_name='school.teacher',
        string='Teacher'
    )
    enrollment_id = fields.Many2one(
        comodel_name='school.enrollment',
        string='Enrollment',
        required=True,
        ondelete='cascade'
    )

    # ==========================================================================
    # TODO 3: Define Computed Fields
    # ==========================================================================
    # - display_name: Computed as "Student - Course - Type (Score)"
    # - percentage: Float, computed as (score / max_score) * 100
    # - letter_grade: Selection, computed from percentage:
    #   * A: >= 90
    #   * B: >= 80
    #   * C: >= 70
    #   * D: >= 60
    #   * F: < 60
    # - is_passing: Boolean, True if percentage >= 60
    # - weighted_score: Float, score * weight
    # ==========================================================================
    
    display_name = fields.Char(
        string='Display Name',
        compute='_compute_display_name',
        store=True,
    )
    
    percentage = fields.Float(
        string='Percentage',
        compute='_compute_percentage',
        store=True,
        digits=(5, 2),
    )
    
    letter_grade = fields.Selection(
        selection=[
            ('A', 'A (Excellent)'),
            ('B', 'B (Good)'),
            ('C', 'C (Average)'),
            ('D', 'D (Below Average)'),
            ('F', 'F (Failing)'),
        ],
        string='Letter Grade',
        compute='_compute_letter_grade',
        store=True,
    )
    
    # TODO: Add remaining computed fields (is_passing, weighted_score)
    is_passing = fields.Boolean(
        string='Is Passing',
        compute='_compute_is_passing',
        store=True
    )
    weighted_score = fields.Float(
        string='Weighted Score',
        compute='_compute_weighted_score',
        store=True,
        digits=(5, 2)
    )

    @api.depends('student_id', 'course_id', 'grade_type', 'score')
    def _compute_display_name(self):
        """TODO: Implement display name"""
        for record in self:
            # YOUR CODE HERE

            record.display_name = f"{record.student_id.name if record.student_id else 'Unknown Student'} - {record.course_id.name if record.course_id else 'Unknown Course'} - {record.grade_type} ({record.score})"

    @api.depends('score', 'max_score')
    def _compute_percentage(self):
        """TODO: Compute percentage from score and max_score"""
        for record in self:
            # YOUR CODE HERE
            if record.max_score > 0:
                record.percentage = (record.score / record.max_score) * 100
            else:
                record.percentage = 0.0
    
    @api.depends('percentage')
    def _compute_letter_grade(self):
        """TODO: Compute letter grade from percentage"""
        for record in self:
            # YOUR CODE HERE
            if record.percentage >= 90:
                record.letter_grade = 'A'
            elif record.percentage >= 80:
                record.letter_grade = 'B'
            elif record.percentage >= 70:
                record.letter_grade = 'C'
            elif record.percentage >= 60:
                record.letter_grade = 'D'
            else:
                record.letter_grade = 'F'

    # TODO: Implement remaining compute methods
    @api.depends('percentage')
    def _compute_is_passing(self):
        for record in self:
            record.is_passing = record.percentage >= 60

    @api.depends('score', 'weight')
    def _compute_weighted_score(self):
        for record in self:
            record.weighted_score = record.score * record.weight

    # ==========================================================================
    # TODO 4: Define Constraints
    # ==========================================================================
    # SQL Constraints:
    # - check_score: score must be >= 0
    # - check_max_score: max_score must be > 0
    # - check_score_max: score must be <= max_score
    # - check_weight: weight must be > 0
    #
    # Python Constraints:
    # - Student must be enrolled in the course to receive a grade
    # - Date cannot be in the future
    # ==========================================================================
    
    _sql_constraints = [
        ('check_score', 'CHECK(score >= 0)', 'Score cannot be negative!'),
        ('check_max_score', 'CHECK(max_score > 0)', 'Maximum score must be positive!'),
        ('check_score_max', 'CHECK(score <= max_score)', 'Score cannot exceed maximum score!'),
        ('check_weight', 'CHECK(weight > 0)', 'Weight must be positive!'),
    ]
    
    @api.constrains('student_id', 'en')
    def _check_enrollment(self):
        """TODO: Validate student is enrolled in the course"""
        for record in self:
            # YOUR CODE HERE
            if not record.student_id or not record.course_id:
                continue
                
            enrollment = self.env['school.enrollment'].search([
                ('student_id', '=', record.student_id.id), 
                ('course_id', '=', record.course_id.id)
            ], limit=1)
            
            if not enrollment:
                raise ValidationError(_("Student %s is not enrolled in course %s.") % (record.student_id.name, record.course_id.name))

    # TODO: Implement remaining constraints
    @api.constrains('date')
    def _check_date_not_future(self):
            """TODO: Validate date is not in the future"""
            for record in self:
                if record.date and record.date > fields.Date.today():
                    raise ValidationError(_("Date cannot be in the future."))
    
    # ==========================================================================
    # TODO 5: Override CRUD Methods
    # ==========================================================================
    # - create(): Validate enrollment exists, set teacher from course
    # - write(): Track score changes in chatter
    # - unlink(): Prevent deletion of old grades (more than 30 days old)
    # ==========================================================================
    
    # YOUR CODE HERE - CRUD overrides
    @api.model_create_multi
    def create(self, vals_list):
        """Override create to validate enrollment and set teacher"""
        for vals in vals_list:
            if not vals.get('grade_type'):
                vals['grade_type'] = 'exam'
                
            if not vals.get('enrollment_id') and vals.get('student_id') and vals.get('course_id'):
                enrollment = self.env['school.enrollment'].search([
                    ('student_id', '=', vals.get('student_id')),
                    ('course_id', '=', vals.get('course_id'))
                ], limit=1)
                
                if enrollment:
                    vals['enrollment_id'] = enrollment.id
                else:
                    raise ValidationError(_("Cannot assign a grade. The student is not enrolled in this course."))
                    
            elif not vals.get('enrollment_id'):
                raise ValidationError(_("An enrollment reference is required to create a grade record."))

        return super(SchoolGrade, self).create(vals_list)

    def write(self, vals):
        """Override write to track score changes in chatter"""
        if 'score' in vals:
            for record in self:
                old_score = record.score
                new_score = vals['score']
                if old_score != new_score:
                    record.message_post(
                        body=_("Score changed from %.2f to %.2f" % (old_score, new_score)),
                        subtype_xmlid="mail.mt_note"
                    )
        return super(SchoolGrade, self).write(vals)

    def unlink(self):
        """Override unlink to prevent deletion of old grades"""
        for record in self:
            if (fields.Date.today() - record.date).days > 30:
                raise UserError(_("Cannot delete grades older than 30 days."))
        return super(SchoolGrade, self).unlink()
    
    # ==========================================================================
    # TODO 6: Implement Business Methods
    # ==========================================================================
    # - recalculate_letter_grade(): Force recomputation of letter grade
    # - get_grade_statistics(): Returns dict with min, max, avg for course
    # - compare_to_class_average(): Returns difference from class average
    # ==========================================================================

    def get_grade_statistics(self):
        """
        Get grade statistics for the course using efficient SQL read_group aggregation.
        Return dict with: count, average, min, max
        """
        self.ensure_one()
        # YOUR CODE HERE - Use read_group for efficient aggregation
        if not self.course_id:
            return {'count': 0, 'average': 0.0, 'min': 0.0, 'max': 0.0}

        domain = [('course_id', '=', self.course_id.id)]
        
        result = self.env['school.grade']._read_group(
            domain=domain,
            aggregates=['__count', 'score:avg', 'score:min', 'score:max']
        )
        
        if result and result[0]:
            count, avg, minimum, maximum = result[0]
            return {
                'count': count or 0,
                'average': round(avg or 0.0, 2),
                'min': minimum or 0.0,
                'max': maximum or 0.0,
            }

        return {'count': 0, 'average': 0.0, 'min': 0.0, 'max': 0.0}
    
    # TODO: Implement remaining methods
    def recalculate_letter_grade(self):
        """
        Force recomputation of the letter grade.
        If it's a standard compute field, self.env.add_to_compute handles it cleanly.
        """
        self.ensure_one()
        # If letter_grade is an @api.depends compute field, you can force it to clear and re-trigger:
        letter_grade_field = self._fields.get('letter_grade')
        if letter_grade_field and letter_grade_field.compute:
            self.env.add_to_compute(letter_grade_field, self)
            self._compute_letter_grade()  # Directly calls your existing compute method
        return True

    def compare_to_class_average(self):
        """
        Returns the numeric difference between this student's grade and the course class average.
        Positive means above average, negative means below average.
        """
        self.ensure_one()
        # 1. Fetch the aggregate dictionary stats for the course
        stats = self.get_grade_statistics()
        class_average = stats.get('average', 0.0)
        
        # 2. Compare the current record score to the class average (Assuming current field is 'score')
        current_score = getattr(self, 'score', 0.0)
        difference = current_score - class_average
        
        return round(difference, 2)
    
    # ==========================================================================
    # TODO 7: Implement Class Methods
    # ==========================================================================
    # - calculate_course_average(course_id): Returns average grade for a course
    # - calculate_student_gpa(student_id): Returns GPA for a student
    # - get_top_students(course_id, limit=10): Returns top students in a course
    # ==========================================================================
    
    @api.model
    def calculate_course_average(self, course_id):
        """
        TODO: Calculate average grade for a course
        Use search and aggregate methods
        """
        # YOUR CODE HERE
        grades = self.search([('course_id', '=', course_id)])
        if not grades:
            return 0.0
        total_score = sum(grade.score for grade in grades)
        average = total_score / len(grades)
        return round(average, 2)

    # TODO: Implement remaining class methods
    @api.model
    def calculate_student_gpa(self, student_id):
        """
        TODO: Calculate GPA for a student
        Use search and aggregate methods
        """
        # YOUR CODE HERE
        grades = self.search([('student_id', '=', student_id)])
        if not grades:
            return 0.0
        total_points = sum(grade.score * grade.credits for grade in grades)
        total_credits = sum(grade.credits for grade in grades)
        if total_credits == 0:
            return 0.0
        gpa = total_points / total_credits
        return round(gpa, 2)

    @api.model
    def get_top_students(self, course_id, limit=10):
        """
        TODO: Get top students in a course
        Use search and order methods
        """
        # YOUR CODE HERE
        students = self.search([('course_id', '=', course_id)], order='score DESC', limit=limit)
        return students