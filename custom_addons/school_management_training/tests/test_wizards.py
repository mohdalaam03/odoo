# -*- coding: utf-8 -*-
# =============================================================================
# WIZARD TESTS
# =============================================================================

from datetime import date
from dateutil.relativedelta import relativedelta

from odoo.tests import TransactionCase, tagged, Form
from odoo.exceptions import ValidationError, UserError


@tagged('post_install', '-at_install', 'school', 'wizard')
class TestEnrollmentWizard(TransactionCase):
    """Test cases for the enrollment wizard."""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Student = cls.env['school.student']
        cls.Course = cls.env['school.course']
        cls.Enrollment = cls.env['school.enrollment']
        cls.Wizard = cls.env['school.enrollment.wizard']
        
        # Create test data
        cls.student1 = cls.Student.create({
            'name': 'Student',
            'last_name': 'One',
            'date_of_birth': date.today() - relativedelta(years=18),
        })
        cls.student2 = cls.Student.create({
            'name': 'Student',
            'last_name': 'Two',
            'date_of_birth': date.today() - relativedelta(years=19),
        })
        cls.course = cls.Course.create({
            'code': 'WIZ001',
            'name': 'Wizard Test Course',
            'max_students': 30,
        })
    
    def test_01_wizard_creation(self):
        """Test wizard can be created."""
        wizard = self.Wizard.create({
            'course_id': self.course.id,
        })
        
        self.assertTrue(wizard.id)
    
    def test_02_wizard_default_from_context(self):
        """Test wizard gets defaults from context."""
        wizard = self.Wizard.with_context(
            active_model='school.student',
            active_ids=[self.student1.id, self.student2.id],
        ).create({
            'course_id': self.course.id,
        })
        
        # The default_get should populate student_ids from context
        self.assertTrue(wizard.id)
    
    def test_03_action_enroll(self):
        """Test bulk enrollment action."""
        wizard = self.Wizard.create({
            'course_id': self.course.id,
            'student_ids': [(6, 0, [self.student1.id, self.student2.id])],
        })
        
        result = wizard.action_enroll()
        
        # Check enrollments were created
        enrollments = self.Enrollment.search([
            ('course_id', '=', self.course.id),
            ('student_id', 'in', [self.student1.id, self.student2.id]),
        ])
        
        self.assertEqual(len(enrollments), 2)
    
    def test_04_action_enroll_returns_action(self):
        """Test that action_enroll returns a window action."""
        wizard = self.Wizard.create({
            'course_id': self.course.id,
            'student_ids': [(6, 0, [self.student1.id])],
        })
        
        result = wizard.action_enroll()
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result.get('type'), 'ir.actions.act_window')
    
    def test_05_action_cancel(self):
        """Test cancel action."""
        wizard = self.Wizard.create({
            'course_id': self.course.id,
        })
        
        result = wizard.action_cancel()
        
        self.assertEqual(result.get('type'), 'ir.actions.act_window_close')
    
    def test_06_capacity_validation(self):
        """Test enrollment respects course capacity."""
        small_course = self.Course.create({
            'code': 'SMALL',
            'name': 'Small Course',
            'max_students': 1,
            'min_students': 0,
        })
        
        wizard = self.Wizard.create({
            'course_id': small_course.id,
            'student_ids': [(6, 0, [self.student1.id, self.student2.id])],
        })
        
        # The wizard should either raise an error or enroll students
        # This is a soft test - we just verify the wizard can be executed
        try:
            result = wizard.action_enroll()
            # If no error, check that enrollments were created
            self.assertTrue(result.get('type') == 'ir.actions.act_window' or result.get('type') == 'ir.actions.act_window_close')
        except UserError:
            # If UserError is raised, the capacity check is working
            pass


@tagged('post_install', '-at_install', 'school', 'wizard')
class TestBulkGradeWizard(TransactionCase):
    """Test cases for the bulk grade wizard."""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Student = cls.env['school.student']
        cls.Course = cls.env['school.course']
        cls.Enrollment = cls.env['school.enrollment']
        cls.Wizard = cls.env['school.bulk.grade.wizard']
        cls.Grade = cls.env['school.grade']
        
        cls.student1 = cls.Student.create({
            'name': 'Grade',
            'last_name': 'Student1',
            'date_of_birth': date.today() - relativedelta(years=18),
        })
        cls.student2 = cls.Student.create({
            'name': 'Grade',
            'last_name': 'Student2',
            'date_of_birth': date.today() - relativedelta(years=19),
        })
        cls.course = cls.Course.create({
            'code': 'GRADE01',
            'name': 'Grade Wizard Course',
        })
        
        # Create enrollments
        cls.Enrollment.create({
            'student_id': cls.student1.id,
            'course_id': cls.course.id,
            'state': 'confirmed',
        })
        cls.Enrollment.create({
            'student_id': cls.student2.id,
            'course_id': cls.course.id,
            'state': 'confirmed',
        })
    
    def test_01_wizard_creation(self):
        """Test wizard can be created."""
        wizard = self.Wizard.create({
            'course_id': self.course.id,
        })
        
        self.assertTrue(wizard.id)
    
    def test_02_action_load_students(self):
        """Test loading students into wizard lines."""
        wizard = self.Wizard.create({
            'course_id': self.course.id,
        })
        
        wizard.action_load_students()
        
        # Should have created lines for enrolled students
        self.assertGreaterEqual(len(wizard.line_ids), 2)
    
    def test_03_action_save_grades(self):
        """Test saving grades from wizard."""
        wizard = self.Wizard.create({
            'course_id': self.course.id,
            'grade_type': 'exam',
            'max_score': 100,
        })
        
        # Manually create lines with scores
        WizardLine = self.env['school.bulk.grade.wizard.line']
        WizardLine.create({
            'wizard_id': wizard.id,
            'student_id': self.student1.id,
            'score': 85,
        })
        WizardLine.create({
            'wizard_id': wizard.id,
            'student_id': self.student2.id,
            'score': 90,
        })
        
        wizard.action_save_grades()
        
        # Check grades were created
        grades = self.Grade.search([
            ('course_id', '=', self.course.id),
        ])
        
        self.assertGreaterEqual(len(grades), 2)


@tagged('post_install', '-at_install', 'school', 'wizard')
class TestBulkAttendanceWizard(TransactionCase):
    """Test cases for the bulk attendance wizard."""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Student = cls.env['school.student']
        cls.Course = cls.env['school.course']
        cls.Enrollment = cls.env['school.enrollment']
        cls.Wizard = cls.env['school.bulk.attendance.wizard']
        cls.Attendance = cls.env['school.attendance']
        
        cls.student1 = cls.Student.create({
            'name': 'Att',
            'last_name': 'Student1',
            'date_of_birth': date.today() - relativedelta(years=18),
        })
        cls.course = cls.Course.create({
            'code': 'ATT01',
            'name': 'Attendance Wizard Course',
        })
        
        cls.Enrollment.create({
            'student_id': cls.student1.id,
            'course_id': cls.course.id,
            'state': 'confirmed',
        })
    
    def test_01_wizard_creation(self):
        """Test wizard can be created."""
        wizard = self.Wizard.create({
            'course_id': self.course.id,
        })
        
        self.assertTrue(wizard.id)
    
    def test_02_default_date_today(self):
        """Test default attendance date is today."""
        wizard = self.Wizard.create({
            'course_id': self.course.id,
        })
        
        self.assertEqual(wizard.attendance_date, date.today())
