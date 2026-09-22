# -*- coding: utf-8 -*-
# =============================================================================
# ATTENDANCE MODEL TESTS
# =============================================================================

from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

from odoo.tests import TransactionCase, tagged, Form
from odoo.exceptions import ValidationError


@tagged('post_install', '-at_install', 'school', 'attendance')
class TestSchoolAttendance(TransactionCase):
    """Test cases for the school.attendance model."""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Student = cls.env['school.student']
        cls.Course = cls.env['school.course']
        cls.Enrollment = cls.env['school.enrollment']
        cls.Attendance = cls.env['school.attendance']
        
        cls.student = cls.Student.create({
            'name': 'Attendance',
            'last_name': 'Student',
            'date_of_birth': date.today() - relativedelta(years=18),
        })
        
        cls.course = cls.Course.create({
            'code': 'ATT001',
            'name': 'Attendance Test Course',
        })
        
        cls.enrollment = cls.Enrollment.create({
            'student_id': cls.student.id,
            'course_id': cls.course.id,
            'state': 'confirmed',
        })
    
    # =========================================================================
    # Basic Tests
    # =========================================================================
    
    def test_01_attendance_creation(self):
        """Test basic attendance creation."""
        attendance = self.Attendance.create({
            'student_id': self.student.id,
            'course_id': self.course.id,
            'status': 'present',
        })
        
        self.assertTrue(attendance.id)
        self.assertEqual(attendance.status, 'present')
    
    def test_02_default_date_today(self):
        """Test default date is today."""
        attendance = self.Attendance.create({
            'student_id': self.student.id,
            'course_id': self.course.id,
            'status': 'present',
        })
        
        self.assertEqual(attendance.date, date.today())
    
    def test_03_default_recorded_by(self):
        """Test recorded_by defaults to current user."""
        attendance = self.Attendance.create({
            'student_id': self.student.id,
            'course_id': self.course.id,
            'status': 'present',
        })
        
        self.assertEqual(attendance.recorded_by, self.env.user)
    
    # =========================================================================
    # Unique Constraint Tests
    # =========================================================================
    
    def test_04_unique_attendance_per_day(self):
        """Test only one attendance per student per course per day."""
        self.Attendance.create({
            'student_id': self.student.id,
            'course_id': self.course.id,
            'status': 'present',
            'date': date.today(),
        })
        
        with self.assertRaises(Exception):
            self.Attendance.create({
                'student_id': self.student.id,
                'course_id': self.course.id,
                'status': 'absent',
                'date': date.today(),
            })
    
    def test_05_different_dates_allowed(self):
        """Test attendance on different dates is allowed."""
        self.Attendance.create({
            'student_id': self.student.id,
            'course_id': self.course.id,
            'status': 'present',
            'date': date.today(),
        })
        
        attendance2 = self.Attendance.create({
            'student_id': self.student.id,
            'course_id': self.course.id,
            'status': 'present',
            'date': date.today() - timedelta(days=1),
        })
        
        self.assertTrue(attendance2.id)
    
    # =========================================================================
    # Computed Fields Tests
    # =========================================================================
    
    def test_06_display_name_computed(self):
        """Test display_name computation."""
        attendance = self.Attendance.create({
            'student_id': self.student.id,
            'course_id': self.course.id,
            'status': 'present',
        })
        
        self.assertTrue(attendance.display_name)
        self.assertIn(self.student.name, attendance.display_name)
    
    def test_07_duration_hours_computed(self):
        """Test duration_hours computation."""
        check_in = datetime.now().replace(hour=9, minute=0, second=0)
        check_out = datetime.now().replace(hour=12, minute=0, second=0)
        
        attendance = self.Attendance.create({
            'student_id': self.student.id,
            'course_id': self.course.id,
            'status': 'present',
            'check_in': check_in,
            'check_out': check_out,
        })
        
        self.assertAlmostEqual(attendance.duration_hours, 3.0, places=1)
    
    def test_08_is_on_time_true(self):
        """Test is_on_time is True for early check-in."""
        early_check_in = datetime.now().replace(hour=8, minute=30, second=0)
        
        attendance = self.Attendance.create({
            'student_id': self.student.id,
            'course_id': self.course.id,
            'status': 'present',
            'check_in': early_check_in,
        })
        
        self.assertTrue(attendance.is_on_time)
    
    def test_09_is_on_time_false(self):
        """Test is_on_time is False for late check-in."""
        late_check_in = datetime.now().replace(hour=9, minute=30, second=0)
        
        attendance = self.Attendance.create({
            'student_id': self.student.id,
            'course_id': self.course.id,
            'status': 'late',
            'check_in': late_check_in,
        })
        
        self.assertFalse(attendance.is_on_time)
    
    # =========================================================================
    # Constraint Tests
    # =========================================================================
    
    def test_10_checkout_after_checkin(self):
        """Test check_out must be after check_in."""
        check_in = datetime.now().replace(hour=12, minute=0, second=0)
        check_out = datetime.now().replace(hour=9, minute=0, second=0)
        
        with self.assertRaises(Exception):
            self.Attendance.create({
                'student_id': self.student.id,
                'course_id': self.course.id,
                'status': 'present',
                'check_in': check_in,
                'check_out': check_out,
            })
    
    # =========================================================================
    # Quick Action Tests
    # =========================================================================
    
    def test_11_mark_present(self):
        """Test mark_present quick action."""
        attendance = self.Attendance.create({
            'student_id': self.student.id,
            'course_id': self.course.id,
            'status': 'absent',
        })
        
        attendance.mark_present()
        
        self.assertEqual(attendance.status, 'present')
        self.assertTrue(attendance.check_in)
    
    def test_12_mark_absent(self):
        """Test mark_absent quick action."""
        attendance = self.Attendance.create({
            'student_id': self.student.id,
            'course_id': self.course.id,
            'status': 'present',
        })
        
        attendance.mark_absent()
        
        self.assertEqual(attendance.status, 'absent')
    
    # =========================================================================
    # Bulk Operations Tests
    # =========================================================================
    
    def test_13_bulk_create_attendance(self):
        """Test bulk_create_attendance method."""
        # Create another student and enrollment
        student2 = self.Student.create({
            'name': 'Bulk',
            'last_name': 'Student',
            'date_of_birth': date.today() - relativedelta(years=19),
        })
        self.Enrollment.create({
            'student_id': student2.id,
            'course_id': self.course.id,
            'state': 'confirmed',
        })
        
        # Use a past date to avoid validation error (date cannot be in future)
        test_date = date.today() - timedelta(days=1)
        
        records = self.Attendance.bulk_create_attendance(
            self.course.id, 
            test_date
        )
        
        self.assertGreaterEqual(len(records), 2)
    
    # =========================================================================
    # Reporting Tests
    # =========================================================================
    
    def test_14_get_attendance_report(self):
        """Test get_attendance_report method."""
        # Create some attendance records
        self.Attendance.create({
            'student_id': self.student.id,
            'course_id': self.course.id,
            'status': 'present',
            'date': date.today() - timedelta(days=1),
        })
        
        report = self.Attendance.get_attendance_report(
            date.today() - timedelta(days=7),
            date.today()
        )
        
        self.assertIsInstance(report, dict)
        self.assertIn('total_records', report)
        self.assertIn('present', report)
        self.assertIn('rate', report)
    
    def test_15_student_attendance_rate(self):
        """Test student attendance rate computation."""
        # Create mix of present and absent
        dates = [date.today() - timedelta(days=i) for i in range(2, 7)]
        
        for i, d in enumerate(dates):
            self.Attendance.create({
                'student_id': self.student.id,
                'course_id': self.course.id,
                'status': 'present' if i < 3 else 'absent',
                'date': d,
            })
        
        # Refresh student
        self.student.invalidate_recordset()
        
        # Should be 60% (3 present out of 5)
        self.assertAlmostEqual(self.student.attendance_rate, 60.0, places=0)
    
    # =========================================================================
    # Form Tests
    # =========================================================================
    
    def test_16_form_create(self):
        """Test creating attendance through form."""
        student2 = self.Student.create({
            'name': 'Form',
            'last_name': 'Attendance',
            'date_of_birth': date.today() - relativedelta(years=20),
        })
        self.Enrollment.create({
            'student_id': student2.id,
            'course_id': self.course.id,
            'state': 'confirmed',
        })
        
        with Form(self.Attendance) as form:
            form.student_id = student2
            form.course_id = self.course
            form.status = 'present'
            
            attendance = form.save()
        
        self.assertTrue(attendance.id)
        self.assertEqual(attendance.status, 'present')
