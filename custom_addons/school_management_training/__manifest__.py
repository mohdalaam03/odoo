# -*- coding: utf-8 -*-
# =============================================================================
# SCHOOL MANAGEMENT TRAINING MODULE
# =============================================================================
# This module is designed for training new Odoo developers.
# Complete all TODO items and run the tests to verify your implementation.
#
# See INSTRUCTIONS.md for detailed guidance on completing this module.
# =============================================================================

{
    'name': 'School Management Training',
    'version': '18.0.1.0.0',
    'category': 'Training',
    'summary': 'A training module to learn Odoo development concepts',
    'description': """
School Management Training Module
=================================

This module is designed to train new Odoo developers by implementing
a complete school management system.

Features to implement:
- Student management
- Teacher management  
- Course management
- Enrollment system
- Grading system
- Attendance tracking
- Report generation

Complete all TODO items and run the automated tests to verify your work.

Running Tests:
    ./odoo-bin -c <config> -d <database> --test-enable -u school_management_training --stop-after-init

See INSTRUCTIONS.md for detailed guidance.
    """,
    'author': 'Training Team',
    'website': 'https://www.odoo.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'mail',
        'portal',
    ],
    'data': [
        # Security
        'security/school_security.xml',
        'security/ir.model.access.csv',
        
        # Data
        'data/sequence_data.xml',
        'data/school_data.xml',
        
        # Views
        'views/school_student_views.xml',
        'views/school_teacher_views.xml',
        'views/school_course_views.xml',
        'views/school_enrollment_views.xml',
        'views/school_grade_views.xml',
        'views/school_attendance_views.xml',
        'views/school_menu.xml',
        
        # Reports
        'report/student_report_templates.xml',
        'report/student_reports.xml',
        
        # Wizards
        'wizard/enrollment_wizard_views.xml',
    ],
    'demo': [
        'demo/demo_data.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
