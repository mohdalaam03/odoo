# -*- coding: utf-8 -*-
# =============================================================================
# ENROLLMENT MODEL TESTS
# =============================================================================

from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

from odoo.tests import TransactionCase, tagged, Form
from odoo.exceptions import ValidationError, UserError


@tagged('post_install', '-at_install', 'school', 'enrollment')
class TestSchoolEnrollment(TransactionCase):
    """Test cases for the school.enrollment model."""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Student = cls.env['school.student']
        cls.Course = cls.env['school.course']
        cls.Enrollment = cls.env['school.enrollment']
        
        cls.student = cls.Student.create({
            'name': 'Test',
            'last_name': 'Student',
            'date_of_birth': date.today() - relativedelta(years=18),
        })
        
        cls.course = cls.Course.create({
            'code': 'TEST001',
            'name': 'Test Course',
            'max_students': 30,
        })
    
    # =========================================================================
    # Basic Tests
    # =========================================================================
    
    def test_01_enrollment_creation(self):
        """Test basic enrollment creation."""
        enrollment = self.Enrollment.create({
            'student_id': self.student.id,
            'course_id': self.course.id,
        })
        
        self.assertTrue(enrollment.id)
        self.assertEqual(enrollment.student_id, self.student)
        self.assertEqual(enrollment.course_id, self.course)
    
    def test_02_default_enrollment_date(self):
        """Test default enrollment date is today."""
        enrollment = self.Enrollment.create({
            'student_id': self.student.id,
            'course_id': self.course.id,
        })
        
        self.assertEqual(enrollment.enrollment_date, date.today())
    
    def test_03_default_state_draft(self):
        """Test default state is draft."""
        enrollment = self.Enrollment.create({
            'student_id': self.student.id,
            'course_id': self.course.id,
        })
        
        self.assertEqual(enrollment.state, 'draft')
    
    # =========================================================================
    # Unique Constraint Tests
    # =========================================================================
    
    def test_04_unique_student_course(self):
        """Test student can only enroll once per course."""
        self.Enrollment.create({
            'student_id': self.student.id,
            'course_id': self.course.id,
        })
        
        with self.assertRaises(Exception):
            self.Enrollment.create({
                'student_id': self.student.id,
                'course_id': self.course.id,
            })
    
    # =========================================================================
    # Computed Fields Tests
    # =========================================================================
    
    def test_05_display_name_computed(self):
        """Test display_name computation."""
        enrollment = self.Enrollment.create({
            'student_id': self.student.id,
            'course_id': self.course.id,
        })
        
        # Display name should contain student and course info
        self.assertIn(self.student.name, enrollment.display_name or '')
        self.assertIn(self.course.name, enrollment.display_name or '')
    
    def test_06_teacher_id_related(self):
        """Test teacher_id is related from course."""
        Teacher = self.env['school.teacher']
        teacher = Teacher.create({
            'name': 'Related Teacher',
            'email': 'related@test.com',
            'hire_date': date.today(),
        })
        
        course = self.Course.create({
            'code': 'REL001',
            'name': 'Related Course',
            'teacher_id': teacher.id,
        })
        
        enrollment = self.Enrollment.create({
            'student_id': self.student.id,
            'course_id': course.id,
        })
        
        self.assertEqual(enrollment.teacher_id, teacher)
    
    def test_07_duration_days_computed(self):
        """Test duration_days computation."""
        enrollment = self.Enrollment.create({
            'student_id': self.student.id,
            'course_id': self.course.id,
            'enrollment_date': date.today() - timedelta(days=10),
        })
        
        self.assertGreaterEqual(enrollment.duration_days, 10)
    
    def test_08_is_active_computed(self):
        """Test is_active computation."""
        enrollment = self.Enrollment.create({
            'student_id': self.student.id,
            'course_id': self.course.id,
            'state': 'confirmed',
        })
        
        self.assertTrue(enrollment.is_active)
        
        enrollment.state = 'cancelled'
        self.assertFalse(enrollment.is_active)
    
    # =========================================================================
    # Constraint Tests
    # =========================================================================
    
    def test_09_completion_after_enrollment(self):
        """Test completion_date must be after enrollment_date."""
        with self.assertRaises(Exception):
            self.Enrollment.create({
                'student_id': self.student.id,
                'course_id': self.course.id,
                'enrollment_date': date.today(),
                'completion_date': date.today() - timedelta(days=30),
            })
    
    # =========================================================================
    # State Transition Tests
    # =========================================================================
    
    def test_10_action_submit(self):
        """Test submit action."""
        enrollment = self.Enrollment.create({
            'student_id': self.student.id,
            'course_id': self.course.id,
            'state': 'draft',
        })
        
        enrollment.action_submit()
        
        self.assertEqual(enrollment.state, 'pending')
    
    def test_11_action_approve(self):
        """Test approve action."""
        enrollment = self.Enrollment.create({
            'student_id': self.student.id,
            'course_id': self.course.id,
            'state': 'pending',
        })
        
        enrollment.action_approve()
        
        self.assertEqual(enrollment.state, 'confirmed')
    
    def test_12_action_complete(self):
        """Test complete action sets completion_date."""
        enrollment = self.Enrollment.create({
            'student_id': self.student.id,
            'course_id': self.course.id,
            'state': 'confirmed',
        })
        
        enrollment.action_complete()
        
        self.assertEqual(enrollment.state, 'completed')
        self.assertEqual(enrollment.completion_date, date.today())
    
    def test_13_action_cancel(self):
        """Test cancel action."""
        enrollment = self.Enrollment.create({
            'student_id': self.student.id,
            'course_id': self.course.id,
            'state': 'pending',
        })
        
        enrollment.action_cancel()
        
        self.assertEqual(enrollment.state, 'cancelled')
    
    def test_14_action_drop(self):
        """Test drop action."""
        enrollment = self.Enrollment.create({
            'student_id': self.student.id,
            'course_id': self.course.id,
            'state': 'confirmed',
        })
        
        enrollment.action_drop()
        
        self.assertEqual(enrollment.state, 'dropped')
    
    # =========================================================================
    # Capacity Tests
    # =========================================================================
    
    def test_15_enrollment_updates_course_count(self):
        """Test that enrollment updates course enrolled_count."""
        initial_count = self.course.enrolled_count
        
        enrollment = self.Enrollment.create({
            'student_id': self.student.id,
            'course_id': self.course.id,
            'state': 'confirmed',
        })
        
        # Refresh course
        self.course.invalidate_recordset()
        
        self.assertEqual(self.course.enrolled_count, initial_count + 1)
    
    # =========================================================================
    # Business Methods Tests
    # =========================================================================
    
    def test_16_check_prerequisites(self):
        """Test check_prerequisites method."""
        enrollment = self.Enrollment.create({
            'student_id': self.student.id,
            'course_id': self.course.id,
        })
        
        result = enrollment.check_prerequisites()
        
        self.assertIsInstance(result, bool)
    
    # =========================================================================
    # CRUD Tests
    # =========================================================================
    
    def test_17_cannot_delete_confirmed(self):
        """Test cannot delete confirmed enrollments."""
        enrollment = self.Enrollment.create({
            'student_id': self.student.id,
            'course_id': self.course.id,
            'state': 'confirmed',
        })
        
        with self.assertRaises(UserError):
            enrollment.unlink()
    
    # =========================================================================
    # Form Tests
    # =========================================================================
    
    def test_18_form_create(self):
        """Test creating enrollment through form."""
        student2 = self.Student.create({
            'name': 'Form',
            'last_name': 'Student',
            'date_of_birth': date.today() - relativedelta(years=19),
        })
        
        with Form(self.Enrollment) as form:
            form.student_id = student2
            form.course_id = self.course
            
            enrollment = form.save()
        
        self.assertTrue(enrollment.id)
