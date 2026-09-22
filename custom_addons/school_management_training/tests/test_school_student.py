# -*- coding: utf-8 -*-
# =============================================================================
# STUDENT MODEL TESTS
# =============================================================================
# These tests validate the school.student model implementation.
# Trainees must complete the model for these tests to pass.
# =============================================================================

from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

from odoo.tests import TransactionCase, tagged, Form
from odoo.exceptions import ValidationError, UserError


@tagged('post_install', '-at_install', 'school', 'student')
class TestSchoolStudent(TransactionCase):
    """
    Test cases for the school.student model.
    
    These tests verify:
    - Field definitions and types
    - Computed fields
    - Constraints (SQL and Python)
    - CRUD operations
    - State transitions
    - Business methods
    """
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Student = cls.env['school.student']
        cls.Partner = cls.env['res.partner']
        
        # Create a guardian
        cls.guardian = cls.Partner.create({
            'name': 'Test Guardian',
            'email': 'guardian@test.com',
        })
    
    # =========================================================================
    # TEST 1: Basic Field Definitions
    # =========================================================================
    
    def test_01_student_creation_basic(self):
        """Test basic student creation with required fields."""
        student = self.Student.create({
            'name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@test.com',
            'date_of_birth': date.today() - relativedelta(years=20),
        })
        
        self.assertTrue(student.id, "Student should be created")
        self.assertEqual(student.name, 'John', "Name should be 'John'")
        self.assertEqual(student.last_name, 'Doe', "Last name should be 'Doe'")
        self.assertTrue(student.student_code, "Student code should be auto-generated")
        self.assertNotEqual(student.student_code, 'New', "Student code should not be 'New'")
    
    def test_02_student_code_sequence(self):
        """Test that student codes are unique and sequential."""
        student1 = self.Student.create({
            'name': 'Student',
            'last_name': 'One',
            'date_of_birth': date.today() - relativedelta(years=18),
        })
        student2 = self.Student.create({
            'name': 'Student',
            'last_name': 'Two',
            'date_of_birth': date.today() - relativedelta(years=18),
        })
        
        self.assertNotEqual(student1.student_code, student2.student_code,
                           "Student codes should be unique")
    
    def test_03_default_state_is_draft(self):
        """Test that new students have 'draft' state by default."""
        student = self.Student.create({
            'name': 'Test',
            'last_name': 'Student',
            'date_of_birth': date.today() - relativedelta(years=15),
        })
        
        self.assertEqual(student.state, 'draft', 
                        "Default state should be 'draft'")
    
    def test_04_default_active_is_true(self):
        """Test that new students are active by default."""
        student = self.Student.create({
            'name': 'Test',
            'last_name': 'Student',
            'date_of_birth': date.today() - relativedelta(years=15),
        })
        
        self.assertTrue(student.active, "Students should be active by default")
    
    # =========================================================================
    # TEST 2: Computed Fields
    # =========================================================================
    
    def test_05_display_name_computed(self):
        """Test display_name computation."""
        student = self.Student.create({
            'name': 'John',
            'last_name': 'Smith',
            'date_of_birth': date.today() - relativedelta(years=18),
        })
        
        expected = 'Smith, John'
        self.assertEqual(student.display_name, expected,
                        f"Display name should be '{expected}', got '{student.display_name}'")
    
    def test_06_age_computed(self):
        """Test age computation from date_of_birth."""
        birth_date = date.today() - relativedelta(years=20)
        student = self.Student.create({
            'name': 'Test',
            'last_name': 'Student',
            'date_of_birth': birth_date,
        })
        
        self.assertEqual(student.age, 20, 
                        f"Age should be 20, got {student.age}")
    
    def test_07_age_boundary(self):
        """Test age computation at birthday boundary."""
        # Born exactly 18 years ago today
        birth_date = date.today() - relativedelta(years=18)
        student = self.Student.create({
            'name': 'Test',
            'last_name': 'Student',
            'date_of_birth': birth_date,
        })
        
        self.assertEqual(student.age, 18,
                        f"Age should be 18 on birthday, got {student.age}")
    
    def test_08_total_courses_computed(self):
        """Test total_courses computation."""
        student = self.Student.create({
            'name': 'Test',
            'last_name': 'Student',
            'date_of_birth': date.today() - relativedelta(years=18),
        })
        
        # Initially no courses
        self.assertEqual(student.total_courses, 0,
                        "Student should have 0 courses initially")
    
    # =========================================================================
    # TEST 3: Constraints
    # =========================================================================
    
    def test_09_age_minimum_constraint(self):
        """Test that students must be at least 5 years old."""
        with self.assertRaises(ValidationError):
            self.Student.create({
                'name': 'Too',
                'last_name': 'Young',
                'date_of_birth': date.today() - relativedelta(years=3),
            })
    
    def test_10_age_maximum_constraint(self):
        """Test that students must be less than 100 years old."""
        with self.assertRaises(ValidationError):
            self.Student.create({
                'name': 'Too',
                'last_name': 'Old',
                'date_of_birth': date.today() - relativedelta(years=105),
            })
    
    def test_11_email_unique_constraint(self):
        """Test that email must be unique."""
        self.Student.create({
            'name': 'First',
            'last_name': 'Student',
            'email': 'unique@test.com',
            'date_of_birth': date.today() - relativedelta(years=18),
        })
        
        with self.assertRaises(Exception):  # Could be IntegrityError or ValidationError
            self.Student.create({
                'name': 'Second',
                'last_name': 'Student',
                'email': 'unique@test.com',
                'date_of_birth': date.today() - relativedelta(years=19),
            })
    
    def test_12_future_birth_date_constraint(self):
        """Test that date_of_birth cannot be in the future."""
        with self.assertRaises(Exception):  # ValidationError or IntegrityError
            self.Student.create({
                'name': 'Future',
                'last_name': 'Person',
                'date_of_birth': date.today() + timedelta(days=30),
            })
    
    # =========================================================================
    # TEST 4: CRUD Operations
    # =========================================================================
    
    def test_13_create_posts_message(self):
        """Test that creating a student posts a message to chatter."""
        student = self.Student.create({
            'name': 'Test',
            'last_name': 'Chatter',
            'date_of_birth': date.today() - relativedelta(years=18),
        })
        
        # Check if any message was posted
        messages = student.message_ids.filtered(lambda m: m.message_type == 'notification')
        self.assertTrue(len(messages) > 0 or len(student.message_ids) > 0,
                       "A message should be posted on creation")
    
    def test_14_copy_clears_student_code(self):
        """Test that copying a student generates a new student code."""
        student = self.Student.create({
            'name': 'Original',
            'last_name': 'Student',
            'date_of_birth': date.today() - relativedelta(years=18),
        })
        
        copied = student.copy()
        
        self.assertNotEqual(student.student_code, copied.student_code,
                           "Copied student should have a different code")
        self.assertIn('Copy', copied.name,
                     "Copied student name should contain 'Copy'")
    
    def test_15_copy_resets_state(self):
        """Test that copying a student resets state to draft."""
        student = self.Student.create({
            'name': 'Original',
            'last_name': 'Student',
            'date_of_birth': date.today() - relativedelta(years=18),
            'state': 'enrolled',
        })
        
        copied = student.copy()
        
        self.assertEqual(copied.state, 'draft',
                        "Copied student state should be 'draft'")
    
    # =========================================================================
    # TEST 5: State Transitions
    # =========================================================================
    
    def test_16_action_enroll_requires_enrollment(self):
        """Test that action_enroll requires at least one enrollment."""
        student = self.Student.create({
            'name': 'Test',
            'last_name': 'Student',
            'date_of_birth': date.today() - relativedelta(years=18),
            'state': 'draft',
        })
        
        # Should raise error because no enrollments
        with self.assertRaises(UserError):
            student.action_enroll()
    
    def test_17_state_transition_draft_to_enrolled(self):
        """Test state transition from draft to enrolled."""
        student = self.Student.create({
            'name': 'Test',
            'last_name': 'Student',
            'date_of_birth': date.today() - relativedelta(years=18),
            'state': 'draft',
        })
        
        # Create a course and enrollment first
        Course = self.env['school.course']
        Enrollment = self.env['school.enrollment']
        
        course = Course.create({
            'code': 'TEST001',
            'name': 'Test Course',
        })
        
        enrollment = Enrollment.create({
            'student_id': student.id,
            'course_id': course.id,
            'state': 'confirmed',
        })
        
        # Now enroll should work
        student.action_enroll()
        
        self.assertEqual(student.state, 'enrolled',
                        "State should be 'enrolled' after action_enroll")
    
    # =========================================================================
    # TEST 6: Business Methods
    # =========================================================================
    
    def test_18_get_grade_summary_empty(self):
        """Test grade summary with no grades."""
        student = self.Student.create({
            'name': 'Test',
            'last_name': 'Student',
            'date_of_birth': date.today() - relativedelta(years=18),
        })
        
        summary = student.get_grade_summary()
        
        self.assertIsInstance(summary, dict, "Should return a dictionary")
        self.assertIn('total', summary, "Summary should have 'total' key")
        self.assertIn('average', summary, "Summary should have 'average' key")
        self.assertEqual(summary['total'], 0, "Total should be 0 with no grades")
    
    # =========================================================================
    # TEST 7: Form View Testing
    # =========================================================================
    
    def test_19_form_create(self):
        """Test creating a student through the form."""
        with Form(self.Student) as form:
            form.name = 'Form'
            form.last_name = 'Test'
            form.date_of_birth = date.today() - relativedelta(years=20)
            
            student = form.save()
        
        self.assertTrue(student.id, "Student should be created via form")
        self.assertEqual(student.name, 'Form', "Name should match")
    
    def test_20_form_onchange_guardian(self):
        """Test onchange behavior for guardian."""
        with Form(self.Student) as form:
            form.name = 'Test'
            form.last_name = 'Onchange'
            form.date_of_birth = date.today() - relativedelta(years=18)
            form.guardian_id = self.guardian
            
            # If student email is empty and guardian has email,
            # the onchange might suggest copying it
            student = form.save()
        
        # This test validates the onchange is implemented and doesn't crash
        self.assertTrue(student.id)
    
    # =========================================================================
    # TEST 8: Search and Name Methods
    # =========================================================================
    
    def test_21_name_search_by_code(self):
        """Test searching students by student code."""
        student = self.Student.create({
            'name': 'SearchByCode',
            'last_name': 'TestStudent',
            'date_of_birth': date.today() - relativedelta(years=18),
        })
        
        # Search by part of student code (e.g., 'STU/2025')
        code_prefix = student.student_code.rsplit('/', 1)[0] if '/' in student.student_code else student.student_code
        results = self.Student.name_search(code_prefix)
        result_ids = [r[0] for r in results]
        
        self.assertIn(student.id, result_ids,
                     "Should find student by student_code")
    
    def test_22_name_search_by_name(self):
        """Test searching students by name."""
        student = self.Student.create({
            'name': 'UniqueSearchName',
            'last_name': 'Test',
            'date_of_birth': date.today() - relativedelta(years=18),
        })
        
        results = self.Student.name_search('UniqueSearchName')
        result_ids = [r[0] for r in results]
        
        self.assertIn(student.id, result_ids,
                     "Should find student by name")
    
    def test_23_name_search_by_email(self):
        """Test searching students by email."""
        unique_email = f'unique.search.{date.today().strftime("%Y%m%d%H%M%S")}@test.com'
        student = self.Student.create({
            'name': 'EmailSearchTest',
            'last_name': 'SearchStudent',
            'email': unique_email,
            'date_of_birth': date.today() - relativedelta(years=18),
        })
        
        # Search by email domain part
        results = self.Student.name_search('unique.search')
        result_ids = [r[0] for r in results]
        
        self.assertIn(student.id, result_ids,
                     "Should find student by email")
