# -*- coding: utf-8 -*-
# =============================================================================
# GRADE MODEL TESTS
# =============================================================================

from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

from odoo.tests import TransactionCase, tagged, Form
from odoo.exceptions import ValidationError


@tagged('post_install', '-at_install', 'school', 'grade')
class TestSchoolGrade(TransactionCase):
    """Test cases for the school.grade model."""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Student = cls.env['school.student']
        cls.Course = cls.env['school.course']
        cls.Enrollment = cls.env['school.enrollment']
        cls.Grade = cls.env['school.grade']
        
        cls.student = cls.Student.create({
            'name': 'Test',
            'last_name': 'Student',
            'date_of_birth': date.today() - relativedelta(years=18),
        })
        
        cls.course = cls.Course.create({
            'code': 'GRADE01',
            'name': 'Grade Test Course',
        })
        
        # Create enrollment for the student
        cls.enrollment = cls.Enrollment.create({
            'student_id': cls.student.id,
            'course_id': cls.course.id,
            'state': 'confirmed',
        })
    
    # =========================================================================
    # Basic Tests
    # =========================================================================
    
    def test_01_grade_creation(self):
        """Test basic grade creation."""
        grade = self.Grade.create({
            'student_id': self.student.id,
            'course_id': self.course.id,
            'score': 85,
            'max_score': 100,
            'grade_type': 'exam',
        })
        
        self.assertTrue(grade.id)
        self.assertEqual(grade.score, 85)
        self.assertEqual(grade.max_score, 100)
    
    def test_02_default_date_today(self):
        """Test default date is today."""
        grade = self.Grade.create({
            'student_id': self.student.id,
            'course_id': self.course.id,
            'score': 80,
            'max_score': 100,
        })
        
        self.assertEqual(grade.date, date.today())
    
    def test_03_default_max_score(self):
        """Test default max_score is 100."""
        grade = self.Grade.create({
            'student_id': self.student.id,
            'course_id': self.course.id,
            'score': 75,
        })
        
        self.assertEqual(grade.max_score, 100)
    
    # =========================================================================
    # Computed Fields Tests
    # =========================================================================
    
    def test_04_percentage_computed(self):
        """Test percentage computation."""
        grade = self.Grade.create({
            'student_id': self.student.id,
            'course_id': self.course.id,
            'score': 85,
            'max_score': 100,
        })
        
        self.assertEqual(grade.percentage, 85.0)
    
    def test_05_percentage_different_max(self):
        """Test percentage with different max_score."""
        grade = self.Grade.create({
            'student_id': self.student.id,
            'course_id': self.course.id,
            'score': 18,
            'max_score': 20,
        })
        
        self.assertEqual(grade.percentage, 90.0)
    
    def test_06_letter_grade_A(self):
        """Test letter grade A (>= 90)."""
        grade = self.Grade.create({
            'student_id': self.student.id,
            'course_id': self.course.id,
            'score': 95,
            'max_score': 100,
        })
        
        self.assertEqual(grade.letter_grade, 'A')
    
    def test_07_letter_grade_B(self):
        """Test letter grade B (>= 80, < 90)."""
        grade = self.Grade.create({
            'student_id': self.student.id,
            'course_id': self.course.id,
            'score': 85,
            'max_score': 100,
        })
        
        self.assertEqual(grade.letter_grade, 'B')
    
    def test_08_letter_grade_C(self):
        """Test letter grade C (>= 70, < 80)."""
        grade = self.Grade.create({
            'student_id': self.student.id,
            'course_id': self.course.id,
            'score': 75,
            'max_score': 100,
        })
        
        self.assertEqual(grade.letter_grade, 'C')
    
    def test_09_letter_grade_D(self):
        """Test letter grade D (>= 60, < 70)."""
        grade = self.Grade.create({
            'student_id': self.student.id,
            'course_id': self.course.id,
            'score': 65,
            'max_score': 100,
        })
        
        self.assertEqual(grade.letter_grade, 'D')
    
    def test_10_letter_grade_F(self):
        """Test letter grade F (< 60)."""
        grade = self.Grade.create({
            'student_id': self.student.id,
            'course_id': self.course.id,
            'score': 55,
            'max_score': 100,
        })
        
        self.assertEqual(grade.letter_grade, 'F')
    
    def test_11_is_passing_true(self):
        """Test is_passing is True for >= 60%."""
        grade = self.Grade.create({
            'student_id': self.student.id,
            'course_id': self.course.id,
            'score': 60,
            'max_score': 100,
        })
        
        self.assertTrue(grade.is_passing)
    
    def test_12_is_passing_false(self):
        """Test is_passing is False for < 60%."""
        grade = self.Grade.create({
            'student_id': self.student.id,
            'course_id': self.course.id,
            'score': 55,
            'max_score': 100,
        })
        
        self.assertFalse(grade.is_passing)
    
    def test_13_weighted_score_computed(self):
        """Test weighted_score computation."""
        grade = self.Grade.create({
            'student_id': self.student.id,
            'course_id': self.course.id,
            'score': 80,
            'max_score': 100,
            'weight': 2.0,
        })
        
        self.assertEqual(grade.weighted_score, 160.0)
    
    # =========================================================================
    # Constraint Tests
    # =========================================================================
    
    def test_14_negative_score_constraint(self):
        """Test score cannot be negative."""
        with self.assertRaises(Exception):
            self.Grade.create({
                'student_id': self.student.id,
                'course_id': self.course.id,
                'score': -10,
                'max_score': 100,
            })
    
    def test_15_score_exceeds_max_constraint(self):
        """Test score cannot exceed max_score."""
        with self.assertRaises(Exception):
            self.Grade.create({
                'student_id': self.student.id,
                'course_id': self.course.id,
                'score': 110,
                'max_score': 100,
            })
    
    def test_16_max_score_positive_constraint(self):
        """Test max_score must be positive."""
        with self.assertRaises(Exception):
            self.Grade.create({
                'student_id': self.student.id,
                'course_id': self.course.id,
                'score': 50,
                'max_score': 0,
            })
    
    def test_17_weight_positive_constraint(self):
        """Test weight must be positive."""
        with self.assertRaises(Exception):
            self.Grade.create({
                'student_id': self.student.id,
                'course_id': self.course.id,
                'score': 80,
                'max_score': 100,
                'weight': -1,
            })
    
    def test_18_enrollment_required(self):
        """Test student must be enrolled to receive grade."""
        other_student = self.Student.create({
            'name': 'Not',
            'last_name': 'Enrolled',
            'date_of_birth': date.today() - relativedelta(years=18),
        })
        
        with self.assertRaises(ValidationError):
            self.Grade.create({
                'student_id': other_student.id,
                'course_id': self.course.id,
                'score': 80,
                'max_score': 100,
            })
    
    # =========================================================================
    # Business Methods Tests
    # =========================================================================
    
    def test_19_get_grade_statistics(self):
        """Test get_grade_statistics method."""
        grade = self.Grade.create({
            'student_id': self.student.id,
            'course_id': self.course.id,
            'score': 85,
            'max_score': 100,
        })
        
        stats = grade.get_grade_statistics()
        
        self.assertIsInstance(stats, dict)
        self.assertIn('count', stats)
        self.assertIn('average', stats)
        self.assertIn('min', stats)
        self.assertIn('max', stats)
    
    def test_20_calculate_course_average(self):
        """Test calculate_course_average class method."""
        # Create multiple grades
        self.Grade.create({
            'student_id': self.student.id,
            'course_id': self.course.id,
            'score': 80,
            'max_score': 100,
        })
        self.Grade.create({
            'student_id': self.student.id,
            'course_id': self.course.id,
            'score': 90,
            'max_score': 100,
            'grade_type': 'quiz',
        })
        
        avg = self.Grade.calculate_course_average(self.course.id)
        
        self.assertIsInstance(avg, float)
        self.assertEqual(avg, 85.0)  # (80 + 90) / 2
    
    # =========================================================================
    # Student Average Grade Integration
    # =========================================================================
    
    def test_21_student_average_grade_updated(self):
        """Test that student's average_grade is updated."""
        self.Grade.create({
            'student_id': self.student.id,
            'course_id': self.course.id,
            'score': 80,
            'max_score': 100,
        })
        self.Grade.create({
            'student_id': self.student.id,
            'course_id': self.course.id,
            'score': 90,
            'max_score': 100,
            'grade_type': 'quiz',
        })
        
        # Refresh student
        self.student.invalidate_recordset()
        
        self.assertEqual(self.student.average_grade, 85.0)
    
    # =========================================================================
    # Form Tests
    # =========================================================================
    
    def test_22_form_create(self):
        """Test creating grade through form."""
        with Form(self.Grade) as form:
            form.student_id = self.student
            form.course_id = self.course
            form.score = 88
            form.grade_type = 'assignment'
            form.description = 'Homework 1'
            
            grade = form.save()
        
        self.assertTrue(grade.id)
        self.assertEqual(grade.score, 88)
        self.assertEqual(grade.letter_grade, 'B')
