# -*- coding: utf-8 -*-
# =============================================================================
# ATTENDANCE MODEL
# =============================================================================
# This model handles student attendance tracking.
# Complete all TODO items to implement the full functionality.
# =============================================================================

from datetime import date, datetime, timedelta

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class SchoolAttendance(models.Model):
    """
    Attendance Model
    
    Tracks daily attendance for students in courses.
    
    Concepts covered:
    - Datetime fields
    - Unique constraint with multiple fields
    - Batch operations
    - Scheduled actions (cron)
    """
    _name = 'school.attendance'
    _description = 'Student Attendance'
    _order = 'date desc, check_in desc'
    _rec_name = 'display_name'
    
    # ==========================================================================
    # TODO 1: Define Basic Fields
    # ==========================================================================
    # Add the following fields:
    # - date: Date, required, default=today, index=True
    # - check_in: Datetime (when student checked in)
    # - check_out: Datetime (when student checked out)
    # - status: Selection (present, absent, late, excused, half_day)
    # - remarks: Text (reason for absence, etc.)
    # - is_excused: Boolean (whether absence is excused)
    # ==========================================================================
    
    # YOUR CODE HERE - Basic Fields
    date = fields.Date(
        string='Date',
        required=True,
        default=fields.Date.today,
        index=True,
    )
    # TODO: Add remaining basic fields
    check_in = fields.Datetime(string='Check In')
    check_out = fields.Datetime(string='Check Out')
    status = fields.Selection(
        selection=[
            ('present', 'Present'),
            ('absent', 'Absent'),
            ('late', 'Late'),
            ('excused', 'Excused'),
            ('half_day', 'Half Day')
        ],
        string='Status',
        required=True,
        default='absent'
    )
    remarks = fields.Text(string='Remarks')
    is_excused = fields.Boolean(string='Is Excused')

    # ==========================================================================
    # TODO 2: Define Relational Fields
    # ==========================================================================
    # - student_id: Many2one to 'school.student', required, ondelete='cascade'
    # - course_id: Many2one to 'school.course', required, ondelete='cascade'
    # - recorded_by: Many2one to 'res.users', default=current user
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
    recorded_by = fields.Many2one(
        comodel_name='res.users',
        string='Recorded By',
        default=lambda self: self.env.user
    )

    # ==========================================================================
    # TODO 3: Define Computed Fields
    # ==========================================================================
    # - display_name: "Student - Course - Date (Status)"
    # - duration_hours: Float, computed from check_in and check_out
    # - is_on_time: Boolean, True if check_in before 9:00 AM
    # - day_of_week: Selection, computed from date (monday, tuesday, etc.)
    # ==========================================================================
    
    display_name = fields.Char(
        string='Display Name',
        compute='_compute_display_name',
        store=True,
    )
    duration_hours = fields.Float(
        string='Duration (Hours)',
        compute='_compute_duration_hours',
        store=True
    )
    is_on_time = fields.Boolean(
        string='Is On Time',
        compute='_compute_is_on_time',
        store=True
    )
    day_of_week = fields.Selection(
        selection=[
            ('monday', 'Monday'),
            ('tuesday', 'Tuesday'),
            ('wednesday', 'Wednesday'),
            ('thursday', 'Thursday'),
            ('friday', 'Friday'),
            ('saturday', 'Saturday'),
            ('sunday', 'Sunday')
        ],
        string='Day of Week',
        compute='_compute_day_of_week',
        store=True
    )

    @api.depends('student_id', 'course_id', 'date', 'status')
    def _compute_display_name(self):
        """TODO: Implement display name"""
        for record in self:
            # YOUR CODE HERE
            student_name = record.student_id.name if record.student_id else 'Unknown Student'
            course_name = record.course_id.name if record.course_id else 'Unknown Course'
            record.display_name = f"{student_name} - {course_name} - {record.date} ({record.status})"

    # TODO: Implement remaining computed fields
    @api.depends('check_in', 'check_out')
    def _compute_duration_hours(self):
        for record in self:
            if record.check_in and record.check_out:
                duration = (record.check_out - record.check_in).total_seconds() / 3600
                record.duration_hours = round(duration, 2)
            else:
                record.duration_hours = 0.0

    @api.depends('check_in')
    def _compute_is_on_time(self):
        import datetime as dt 
        for record in self:
            if record.check_in:
                # Extracts the clock time from the check-in timestamp
                check_in_clock = fields.Datetime.from_string(record.check_in).time()
                
                on_time_threshold = dt.time(9, 0)  # 9:00 AM
                record.is_on_time = check_in_clock < on_time_threshold
            else:
                record.is_on_time = False

    @api.depends('date')
    def _compute_day_of_week(self):
        for record in self:
            if record.date:
                day_index = record.date.weekday()
                days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
                record.day_of_week = days[day_index]
            else:
                record.day_of_week = False

    # ==========================================================================
    # TODO 4: Define Constraints
    # ==========================================================================
    # SQL Constraints:
    # - unique_attendance: One record per student per course per date
    #
    # Python Constraints:
    # - check_out must be after check_in
    # - date cannot be in the future
    # - Student must be enrolled in the course
    # ==========================================================================
    
    _sql_constraints = [
        ('unique_attendance', 'UNIQUE(student_id, course_id, date)', 
         'Attendance already recorded for this student in this course on this date!'),
    ]
    
    @api.constrains('check_in', 'check_out')
    def _check_times(self):
        """TODO: Validate check_out is after check_in"""
        for record in self:
            # YOUR CODE HERE
            if record.check_in and record.check_out:
                if record.check_out <= record.check_in:
                    raise ValidationError(_("Check-out time must be after check-in time."))

    # TODO: Implement remaining constraints
    @api.constrains('date')
    def _check_date_not_future(self):
        """TODO: Validate date is not in the future"""
        for record in self:
            if record.date and record.date > fields.Date.today():
                raise ValidationError(_("Date cannot be in the future."))
    
    @api.constrains('student_id', 'course_id', 'date')
    def _check_student_enrollment(self):
        """TODO: Validate student is enrolled in the course"""
        for record in self:
            if record.student_id and record.course_id:
                enrollment = self.env['school.enrollment'].search([
                    ('student_id', '=', record.student_id.id),
                    ('course_id', '=', record.course_id.id)
                ], limit=1)
                if not enrollment:
                    raise ValidationError(_("Student is not enrolled in this course."))
    
    # ==========================================================================
    # TODO 5: Implement Onchange Methods
    # ==========================================================================
    # - _onchange_check_in: If check_in is after 9:00, suggest status='late'
    # - _onchange_status: If status is 'excused', set is_excused=True
    # ==========================================================================
    
    # YOUR CODE HERE - Onchange methods
    def _onchange_check_in(self):
        if self.check_in:
            # Example logic: if check_in is after 9:00, suggest status='late'
            if self.check_in.time() > datetime.time(9, 0):
                self.status = 'late'

    def _onchange_status(self):
        if self.status == 'excused':
            self.is_excused = True

    # ==========================================================================
    # TODO 6: Implement Business Methods
    # ==========================================================================
    # - mark_present(): Quick action to mark as present with current time
    # - mark_absent(): Quick action to mark as absent
    # - get_student_attendance_summary(student_id, date_from, date_to):
    #   Returns attendance statistics for a student in date range
    # ==========================================================================
    
    def mark_present(self):
        """TODO: Mark attendance as present with current time"""
        # YOUR CODE HERE
        return self.write({
            'status': 'present',
            'check_in': fields.Datetime.now()
        })

    def mark_absent(self):
        """TODO: Mark attendance as absent"""
        # YOUR CODE HERE
        return self.write({
            'status': 'absent',
            'check_in': False 
        })
    
    # TODO: Implement remaining methods
    @api.model
    def get_student_attendance_summary(self, student_id, date_from, date_to):
        """
        Returns attendance statistics for a student in a specific date range.
        Calculated by actual hours present vs total scheduled hours.
        """
        if not student_id:
            return {'total': 0, 'present': 0, 'absent': 0, 'rate': 0.0}
            
        domain = [
            ('student_id', '=', student_id),
            ('date', '>=', date_from),
            ('date', '<=', date_to)
        ]
        
        attendance_records = self.search(domain)
        if not attendance_records:
            return {'total': 0, 'present': 0, 'absent': 0, 'rate': 0.0}

        total_hours = 0.0
        present_hours = 0.0
        absent_hours = 0.0

        for r in attendance_records:
            # Calculate actual session duration in hours from check-in/out timestamps
            if r.check_in and r.check_out:
                duration = (r.check_out - r.check_in).total_seconds() / 3600.0
            else:
                duration = 2.0  # Safe fallback default if explicit check-in data is missing

            total_hours += duration
            if r.status == 'present':
                present_hours += duration
            elif r.status == 'absent':
                absent_hours += duration

        attendance_rate = (present_hours / total_hours * 100.0) if total_hours > 0 else 0.0
        
        return {
            'total': len(attendance_records),  # Keeps instance counts for graph keys
            'present': len(attendance_records.filtered(lambda r: r.status == 'present')),
            'absent': len(attendance_records.filtered(lambda r: r.status == 'absent')),
            'rate': round(attendance_rate, 2), # Fixed hour-based rate
        }
    
    # ==========================================================================
    # TODO 7: Implement Batch/Bulk Operations
    # ==========================================================================
    # - bulk_create_attendance(course_id, date): Creates attendance records
    #   for all enrolled students in a course for a given date
    # - bulk_mark_present(ids): Marks multiple records as present
    # - bulk_mark_absent(ids): Marks multiple records as absent
    # ==========================================================================
    
    @api.model
    def bulk_create_attendance(self, course_id, attendance_date=None):
        """
        TODO: Create attendance records for all enrolled students
        Creates 'absent' records by default that can be updated to 'present'
        """
        if attendance_date is None:
            attendance_date = fields.Date.today()
        
        # YOUR CODE HERE
        # 1. Get course and its confirmed enrollments
        # 2. For each enrolled student, create attendance record if not exists
        # 3. Return created records
        course = self.env['school.course'].browse(course_id)
        if not course:
            raise UserError(_("Course not found."))

        for enrollment in course.enrollment_ids:
            student = enrollment.student_id
            existing_record = self.search([
                ('student_id', '=', student.id),
                ('course_id', '=', course.id),
                ('date', '=', attendance_date)
            ], limit=1)
            if not existing_record:
                self.create({
                    'student_id': student.id,
                    'course_id': course.id,
                    'date': attendance_date,
                    'status': 'absent'
                })

        return self.env['school.attendance'].search([
            ('course_id', '=', course.id),
            ('date', '=', attendance_date)
        ])
    
    # TODO: Implement bulk_mark_present and bulk_mark_absent
    def bulk_mark_present(self, ids):
        """Marks multiple attendance records as present"""
        records = self.browse(ids)
        return records.write({
            'status': 'present',
            'check_in': fields.Datetime.now()
        })
    
    def bulk_mark_absent(self, ids):
        """Marks multiple attendance records as absent"""
        records = self.browse(ids)
        return records.write({
            'status': 'absent',
            'check_in': None
        })

    # ==========================================================================
    # TODO 8: Implement Scheduled Action Method
    # ==========================================================================
    # - _cron_create_daily_attendance(): Cron job to create attendance
    #   records for all active courses every day
    # - _cron_send_absence_notifications(): Send notifications for absent students
    # ==========================================================================
    
    @api.model
    def _cron_create_daily_attendance(self):
        """
        TODO: Cron job to create daily attendance records
        Creates attendance records for all students in all active courses
        """
        # YOUR CODE HERE
        today = fields.Date.today()
        active_courses = self.env['school.course'].search([('state', '=', 'in_progress')])
        for course in active_courses:
            self.bulk_create_attendance(course.id, attendance_date=today)
    
    # TODO: Implement _cron_send_absence_notifications
    def _cron_send_absence_notifications(self):
        """TODO: Send notifications for students marked absent"""
        today = fields.Date.today()
        absent_records = self.search([
            ('date', '=', today),
            ('status', '=', 'absent')
        ])
        for record in absent_records:
            student = record.student_id
            if student and student.parent_email:
                # Send email notification to parent (pseudo-code)
                self.env['mail.mail'].create({
                    'subject': f"Attendance Alert: {student.name} Absent Today",
                    'body_html': f"<p>Dear Parent,</p><p>Your child {student.name} was marked absent on {today} for the course {record.course_id.name}.</p>",
                    'email_to': student.parent_email,
                }).send()
    
    # ==========================================================================
    # TODO 9: Implement Reporting Methods
    # ==========================================================================
    # - get_attendance_report(date_from, date_to, course_id=None):
    #   Returns aggregated attendance data for reporting
    # - get_student_attendance_percentage(student_id, course_id=None):
    #   Returns attendance percentage for a student
    # ==========================================================================
    
    @api.model
    def get_attendance_report(self, date_from, date_to, course_id=None):
        """
        Generate attendance report data aggregated by actual hours
        """
        domain = [
            ('date', '>=', date_from),
            ('date', '<=', date_to),
        ]
        if course_id:
            domain.append(('course_id', '=', course_id))
        
        attendance_records = self.search(domain)
        if not attendance_records:
            return {'total_records': 0, 'present': 0, 'absent': 0, 'rate': 0.0}

        total_hours = 0.0
        present_hours = 0.0

        for r in attendance_records:
            if r.check_in and r.check_out:
                duration = (r.check_out - r.check_in).total_seconds() / 3600.0
            else:
                duration = 2.0

            total_hours += duration
            if r.status == 'present':
                present_hours += duration

        attendance_rate = (present_hours / total_hours * 100.0) if total_hours > 0 else 0.0

        return {
            'total_records': len(attendance_records),
            'present': len(attendance_records.filtered(lambda r: r.status == 'present')),
            'absent': len(attendance_records.filtered(lambda r: r.status == 'absent')),
            'rate': round(attendance_rate, 2)
        }
    
    # TODO: Implement get_student_attendance_percentage
    def get_student_attendance_percentage(self, student_id, course_id=None):
        """ TODO: Calculate attendance percentage for a student """
        domain = [('student_id', '=', student_id)]
        if course_id:
            domain.append(('course_id', '=', course_id))
        
        total_records = self.search_count(domain)
        if total_records == 0:
            return 0.0
        
        present_records = self.search_count(domain + [('status', '=', 'present')])
        percentage = (present_records / total_records) * 100.0
        return round(percentage, 2)