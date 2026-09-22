# -*- coding: utf-8 -*-
# =============================================================================
# COURSE MODEL TESTS
# =============================================================================

from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

from odoo.tests import TransactionCase, tagged, Form
from odoo.exceptions import ValidationError, UserError


@tagged('post_install', '-at_install', 'school', 'course')
class TestSchoolCourse(TransactionCase):
    """Test cases for the school.course model."""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Course = cls.env['school.course']
        cls.Teacher = cls.env['school.teacher']
        
        cls.teacher = cls.Teacher.create({
            'name': 'Test Teacher',
            'email': 'teacher@test.com',
            'hire_date': date.today(),
        })
    
    # =========================================================================
    # Basic Tests
    # =========================================================================
    
    def test_01_course_creation(self):
        """Test basic course creation."""
        course = self.Course.create({
            'code': 'TEST101',
            'name': 'Test Course',
        })
        
        self.assertTrue(course.id, "Course should be created")
        self.assertEqual(course.code, 'TEST101')
    
    def test_02_unique_code_constraint(self):
        """Test that course codes must be unique."""
        self.Course.create({
            'code': 'UNIQUE01',
            'name': 'First Course',
        })
        
        with self.assertRaises(Exception):
            self.Course.create({
                'code': 'UNIQUE01',
                'name': 'Second Course',
            })
    
    def test_03_default_state_draft(self):
        """Test default state is draft."""
        course = self.Course.create({
            'code': 'STATE01',
            'name': 'State Test Course',
        })
        
        self.assertEqual(course.state, 'draft')
    
    def test_04_default_credits(self):
        """Test default credits value."""
        course = self.Course.create({
            'code': 'CRED01',
            'name': 'Credits Test',
        })
        
        self.assertEqual(course.credits, 3, "Default credits should be 3")
    
    def test_05_default_max_students(self):
        """Test default max_students value."""
        course = self.Course.create({
            'code': 'MAX01',
            'name': 'Max Students Test',
        })
        
        self.assertEqual(course.max_students, 30, "Default max_students should be 30")
    
    # =========================================================================
    # Computed Fields Tests
    # =========================================================================
    
    def test_06_enrolled_count_empty(self):
        """Test enrolled_count with no enrollments."""
        course = self.Course.create({
            'code': 'ENRL01',
            'name': 'Enrollment Count Test',
        })
        
        self.assertEqual(course.enrolled_count, 0)
    
    def test_07_available_seats_computed(self):
        """Test available_seats computation."""
        course = self.Course.create({
            'code': 'SEAT01',
            'name': 'Seats Test',
            'max_students': 30,
        })
        
        self.assertEqual(course.available_seats, 30,
                        "Available seats should equal max_students initially")
    
    def test_08_is_full_computed(self):
        """Test is_full computation."""
        course = self.Course.create({
            'code': 'FULL01',
            'name': 'Full Course Test',
            'max_students': 30,
        })
        
        self.assertFalse(course.is_full,
                        "Course should not be full initially")
    
    # =========================================================================
    # Constraint Tests
    # =========================================================================
    
    def test_09_credits_range_constraint(self):
        """Test credits must be between 1 and 10."""
        with self.assertRaises(Exception):
            self.Course.create({
                'code': 'CRED02',
                'name': 'Invalid Credits',
                'credits': 15,
            })
    
    def test_10_credits_minimum_constraint(self):
        """Test credits minimum value."""
        with self.assertRaises(Exception):
            self.Course.create({
                'code': 'CRED03',
                'name': 'Zero Credits',
                'credits': 0,
            })
    
    def test_11_max_students_positive_constraint(self):
        """Test max_students must be positive."""
        with self.assertRaises(Exception):
            self.Course.create({
                'code': 'MAX02',
                'name': 'Negative Max',
                'max_students': -5,
            })
    
    def test_12_date_range_constraint(self):
        """Test end_date must be after start_date."""
        with self.assertRaises(Exception):
            self.Course.create({
                'code': 'DATE01',
                'name': 'Invalid Dates',
                'start_date': date.today(),
                'end_date': date.today() - timedelta(days=30),
            })
    
    def test_13_min_max_students_constraint(self):
        """Test min_students must be less than max_students."""
        with self.assertRaises(Exception):
            self.Course.create({
                'code': 'MINMAX',
                'name': 'Invalid Min/Max',
                'min_students': 50,
                'max_students': 30,
            })
    
    # =========================================================================
    # State Transition Tests
    # =========================================================================
    
    def test_14_action_plan_requires_teacher(self):
        """Test action_plan requires a teacher."""
        course = self.Course.create({
            'code': 'PLAN01',
            'name': 'Plan Test',
            'state': 'draft',
        })
        
        with self.assertRaises(UserError):
            course.action_plan()
    
    def test_15_action_plan_success(self):
        """Test successful planning with teacher."""
        course = self.Course.create({
            'code': 'PLAN02',
            'name': 'Plan Success',
            'state': 'draft',
            'teacher_id': self.teacher.id,
        })
        
        course.action_plan()
        
        self.assertEqual(course.state, 'planned')
    
    def test_16_action_cancel(self):
        """Test cancellation action."""
        course = self.Course.create({
            'code': 'CANCEL',
            'name': 'Cancel Test',
            'state': 'planned',
            'teacher_id': self.teacher.id,
        })
        
        course.action_cancel()
        
        self.assertEqual(course.state, 'cancelled')
    
    # =========================================================================
    # Prerequisite Tests
    # =========================================================================
    
    def test_17_prerequisite_not_self(self):
        """Test course cannot be its own prerequisite."""
        course = self.Course.create({
            'code': 'PREREQ',
            'name': 'Prerequisite Test',
        })
        
        with self.assertRaises(Exception):
            course.write({'prerequisite_ids': [(4, course.id)]})
    
    # =========================================================================
    # Business Methods Tests
    # =========================================================================
    
    def test_18_get_eligible_students(self):
        """Test get_eligible_students method."""
        course = self.Course.create({
            'code': 'ELIG01',
            'name': 'Eligibility Test',
        })
        
        eligible = course.get_eligible_students()
        
        # Should return a recordset (even if empty)
        self.assertEqual(eligible._name, 'school.student')
    
    # =========================================================================
    # Form Tests
    # =========================================================================
    
    def test_19_form_create(self):
        """Test creating course through form."""
        with Form(self.Course) as form:
            form.code = 'FORM01'
            form.name = 'Form Course'
            form.credits = 4
            form.level = 'intermediate'
            
            course = form.save()
        
        self.assertTrue(course.id)
        self.assertEqual(course.credits, 4)
        self.assertEqual(course.level, 'intermediate')


@tagged('post_install', '-at_install', 'school', 'course_category')
class TestSchoolCourseCategory(TransactionCase):
    """Test cases for course categories."""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Category = cls.env['school.course.category']
    
    def test_01_category_creation(self):
        """Test basic category creation."""
        category = self.Category.create({
            'name': 'Test Category',
        })
        
        self.assertTrue(category.id)
    
    def test_02_parent_child_hierarchy(self):
        """Test parent-child relationship."""
        parent = self.Category.create({'name': 'Parent'})
        child = self.Category.create({
            'name': 'Child',
            'parent_id': parent.id,
        })
        
        self.assertEqual(child.parent_id, parent)
        self.assertIn(child, parent.child_ids)
    
    def test_03_complete_name_computed(self):
        """Test complete_name computation."""
        parent = self.Category.create({'name': 'Parent'})
        child = self.Category.create({
            'name': 'Child',
            'parent_id': parent.id,
        })
        
        expected = 'Parent / Child'
        self.assertEqual(child.complete_name, expected,
                        f"Complete name should be '{expected}', got '{child.complete_name}'")


@tagged('post_install', '-at_install', 'school', 'course_tag')
class TestSchoolCourseTag(TransactionCase):
    """Test cases for course tags."""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Tag = cls.env['school.course.tag']
    
    def test_01_tag_creation(self):
        """Test basic tag creation."""
        tag = self.Tag.create({
            'name': 'Test Tag',
            'color': 1,
        })
        
        self.assertTrue(tag.id)
        self.assertEqual(tag.color, 1)
