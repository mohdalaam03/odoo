# -*- coding: utf-8 -*-
# =============================================================================
# TEACHER MODEL TESTS
# =============================================================================

from datetime import date
from dateutil.relativedelta import relativedelta

from odoo.tests import TransactionCase, tagged, Form
from odoo.exceptions import ValidationError


@tagged('post_install', '-at_install', 'school', 'teacher')
class TestSchoolTeacher(TransactionCase):
    """Test cases for the school.teacher model."""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Teacher = cls.env['school.teacher']
    
    # =========================================================================
    # Basic Tests
    # =========================================================================
    
    def test_01_teacher_creation(self):
        """Test basic teacher creation."""
        teacher = self.Teacher.create({
            'name': 'John Smith',
            'email': 'john.smith@school.edu',
            'hire_date': date.today(),
        })
        
        self.assertTrue(teacher.id, "Teacher should be created")
        self.assertTrue(teacher.employee_code, "Employee code should be generated")
        self.assertNotEqual(teacher.employee_code, 'New')
    
    def test_02_employee_code_unique(self):
        """Test that employee codes are unique."""
        teacher1 = self.Teacher.create({
            'name': 'Teacher One',
            'email': 'teacher1@school.edu',
            'hire_date': date.today(),
        })
        teacher2 = self.Teacher.create({
            'name': 'Teacher Two',
            'email': 'teacher2@school.edu',
            'hire_date': date.today(),
        })
        
        self.assertNotEqual(teacher1.employee_code, teacher2.employee_code)
    
    def test_03_default_active(self):
        """Test that teachers are active by default."""
        teacher = self.Teacher.create({
            'name': 'Active Teacher',
            'email': 'active@school.edu',
            'hire_date': date.today(),
        })
        
        self.assertTrue(teacher.active)
    
    # =========================================================================
    # Computed Fields Tests
    # =========================================================================
    
    def test_04_years_of_service_computed(self):
        """Test years of service computation."""
        hire_date = date.today() - relativedelta(years=5)
        teacher = self.Teacher.create({
            'name': 'Experienced Teacher',
            'email': 'exp@school.edu',
            'hire_date': hire_date,
        })
        
        self.assertEqual(teacher.years_of_service, 5,
                        f"Years of service should be 5, got {teacher.years_of_service}")
    
    def test_05_total_courses_computed(self):
        """Test total courses computation."""
        teacher = self.Teacher.create({
            'name': 'New Teacher',
            'email': 'new@school.edu',
            'hire_date': date.today(),
        })
        
        self.assertEqual(teacher.total_courses, 0,
                        "New teacher should have 0 courses")
    
    def test_06_age_computed(self):
        """Test age computation from date_of_birth."""
        teacher = self.Teacher.create({
            'name': 'Test Teacher',
            'email': 'test@school.edu',
            'hire_date': date.today(),
            'date_of_birth': date.today() - relativedelta(years=35),
        })
        
        self.assertEqual(teacher.age, 35,
                        f"Age should be 35, got {teacher.age}")
    
    # =========================================================================
    # Constraint Tests
    # =========================================================================
    
    def test_07_future_hire_date_constraint(self):
        """Test that hire_date cannot be in the future."""
        with self.assertRaises(Exception):
            self.Teacher.create({
                'name': 'Future Teacher',
                'email': 'future@school.edu',
                'hire_date': date.today() + relativedelta(days=30),
            })
    
    def test_08_negative_experience_constraint(self):
        """Test that experience_years cannot be negative."""
        with self.assertRaises(Exception):
            self.Teacher.create({
                'name': 'Invalid Teacher',
                'email': 'invalid@school.edu',
                'hire_date': date.today(),
                'experience_years': -5,
            })
    
    # =========================================================================
    # Related Fields Tests
    # =========================================================================
    
    def test_09_company_name_related(self):
        """Test company_name related field."""
        teacher = self.Teacher.create({
            'name': 'Company Teacher',
            'email': 'company@school.edu',
            'hire_date': date.today(),
        })
        
        if teacher.company_id:
            self.assertEqual(teacher.company_name, teacher.company_id.name)
    
    # =========================================================================
    # Business Methods Tests
    # =========================================================================
    
    def test_10_get_courses_summary(self):
        """Test get_courses_summary method."""
        teacher = self.Teacher.create({
            'name': 'Summary Teacher',
            'email': 'summary@school.edu',
            'hire_date': date.today(),
        })
        
        summary = teacher.get_courses_summary()
        
        self.assertIsInstance(summary, dict)
        self.assertIn('total_courses', summary)
        self.assertIn('total_students', summary)
    
    # =========================================================================
    # Form Tests
    # =========================================================================
    
    def test_11_form_create(self):
        """Test creating teacher through form."""
        with Form(self.Teacher) as form:
            form.name = 'Form Teacher'
            form.email = 'form.teacher@school.edu'
            form.hire_date = date.today()
            form.department = 'mathematics'
            
            teacher = form.save()
        
        self.assertTrue(teacher.id)
        self.assertEqual(teacher.department, 'mathematics')
