# School Management Training Module - Developer Instructions

## Overview

Welcome to the Odoo Developer Training Program! This module is designed to teach you essential Odoo development concepts through hands-on implementation of a **School Management System**.

You have **5 working days** to complete all tasks. The module includes automated tests that will verify your implementations.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Module Structure](#module-structure)
3. [Day 1: Student Model & Basic Concepts](#day-1-student-model--basic-concepts)
4. [Day 2: Teacher & Course Models](#day-2-teacher--course-models)
5. [Day 3: Enrollment & Grade Models](#day-3-enrollment--grade-models)
6. [Day 4: Attendance & Wizards](#day-4-attendance--wizards)
7. [Day 5: Views, Reports & Polish](#day-5-views-reports--polish)
8. [Running Tests](#running-tests)
9. [Concepts Reference](#concepts-reference)
10. [Common Mistakes to Avoid](#common-mistakes-to-avoid)

---

## Getting Started

### Prerequisites

- Odoo 19 (or 18) development environment
- PostgreSQL database
- Python 3.10+
- Basic Python knowledge

### Installation

1. Copy this module to your Odoo addons path
2. Update the apps list: `Apps > Update Apps List`
3. Install the module: Search for "School Management Training" and install

### First Run

After installation, navigate to **School > Students** to see the module interface.

---

## Module Structure

```
school_management_training/
├── __manifest__.py          # Module metadata (don't modify)
├── __init__.py              # Package imports
├── models/
│   ├── __init__.py
│   ├── school_student.py    # Day 1: Complete the student model
│   ├── school_teacher.py    # Day 2: Complete the teacher model
│   ├── school_course.py     # Day 2: Complete the course model
│   ├── school_enrollment.py # Day 3: Complete the enrollment model
│   ├── school_grade.py      # Day 3: Complete the grade model
│   └── school_attendance.py # Day 4: Complete the attendance model
├── wizard/
│   ├── __init__.py
│   └── enrollment_wizard.py # Day 4: Complete the wizards
├── views/                   # Day 5: Complete the XML views
├── security/                # Review and understand security rules
├── data/                    # Data files (pre-configured)
├── demo/                    # Demo data
├── report/                  # Day 5: Complete report templates
└── tests/                   # Automated tests (don't modify)
```

---

## Day 1: Student Model & Basic Concepts

### Goals
- Understand Odoo model structure
- Learn field types
- Implement computed fields
- Add constraints
- Override CRUD methods

### Tasks

Open `models/school_student.py` and complete all TODO items:

#### TODO 1: Define Basic Fields
```python
# Fields to add:
name = fields.Char(string='First Name', required=True, tracking=True)
last_name = fields.Char(string='Last Name', required=True)
email = fields.Char(string='Email')
phone = fields.Char(string='Phone')
date_of_birth = fields.Date(string='Date of Birth', required=True)
gender = fields.Selection([
    ('male', 'Male'),
    ('female', 'Female'),
    ('other', 'Other'),
], string='Gender')
address = fields.Text(string='Address')
photo = fields.Binary(string='Photo')
active = fields.Boolean(string='Active', default=True)
notes = fields.Html(string='Notes')
```

#### TODO 2: Define Relational Fields
```python
guardian_id = fields.Many2one('res.partner', string='Guardian')
enrollment_ids = fields.One2many('school.enrollment', 'student_id', string='Enrollments')
course_ids = fields.Many2many('school.course', string='Courses')
grade_ids = fields.One2many('school.grade', 'student_id', string='Grades')
attendance_ids = fields.One2many('school.attendance', 'student_id', string='Attendance')
```

#### TODO 3: Define State Field
```python
state = fields.Selection([
    ('draft', 'Draft'),
    ('enrolled', 'Enrolled'),
    ('graduated', 'Graduated'),
    ('suspended', 'Suspended'),
    ('withdrawn', 'Withdrawn'),
], string='State', default='draft', tracking=True)
```

#### TODO 4: Computed Fields
```python
# Example implementation for age:
age = fields.Integer(string='Age', compute='_compute_age', store=True)

@api.depends('date_of_birth')
def _compute_age(self):
    for record in self:
        if record.date_of_birth:
            today = date.today()
            record.age = today.year - record.date_of_birth.year - (
                (today.month, today.day) < (record.date_of_birth.month, record.date_of_birth.day)
            )
        else:
            record.age = 0
```

### Key Concepts Day 1

| Concept | Description |
|---------|-------------|
| `fields.Char` | Short text (VARCHAR) |
| `fields.Text` | Long text |
| `fields.Html` | Rich HTML content |
| `fields.Selection` | Dropdown with fixed options |
| `fields.Boolean` | True/False |
| `fields.Integer` | Whole numbers |
| `fields.Float` | Decimal numbers |
| `fields.Date` | Date without time |
| `fields.Many2one` | Link to another model (FK) |
| `fields.One2many` | Reverse of Many2one |
| `fields.Many2many` | N:N relationship |
| `@api.depends` | Declares computed field dependencies |
| `@api.constrains` | Python validation |
| `_sql_constraints` | Database-level constraints |

### Run Day 1 Tests

```bash
# Windows PowerShell
python odoo-bin -c odoo.conf -d your_db --test-enable -i school_management_training --stop-after-init --test-tags school,student

# Linux/Mac
./odoo-bin -c odoo.conf -d your_db --test-enable -i school_management_training --stop-after-init --test-tags school,student
```

---

## Day 2: Teacher & Course Models

### Goals
- Learn monetary fields
- Understand related fields
- Implement parent-child hierarchies
- Work with recursive relationships

### Tasks

#### Teacher Model (`school_teacher.py`)
- Add basic fields (name, email, phone, etc.)
- Add monetary field for salary
- Add related fields for company
- Implement computed fields (years_of_service, total_courses)

#### Course Model (`school_course.py`)
- Add basic fields (code, name, credits, etc.)
- Add prerequisites (self-referential Many2many)
- Implement capacity management (enrolled_count, available_seats)
- Add state workflow

#### Course Category (`school_course.py`)
- Implement parent-child hierarchy
- Add `complete_name` computed field (e.g., "Parent / Child")

### Key Concepts Day 2

| Concept | Description |
|---------|-------------|
| `fields.Monetary` | Currency amounts (needs `currency_id`) |
| Related fields | `related='field.subfield'` |
| `_parent_store` | Optimized parent-child queries |
| Self-referential | Many2many to same model |
| Default with lambda | `default=lambda self: ...` |

### Run Day 2 Tests

```bash
python odoo-bin -c odoo.conf -d your_db --test-enable -u school_management_training --stop-after-init --test-tags school,teacher,course
```

---

## Day 3: Enrollment & Grade Models

### Goals
- Handle many-to-many through model (Enrollment)
- Implement unique constraints
- Work with date calculations
- Use read_group for aggregations

### Tasks

#### Enrollment Model (`school_enrollment.py`)
- Link students to courses
- Add state workflow (draft -> pending -> confirmed -> completed)
- Implement duration calculations
- Add prerequisite checking

#### Grade Model (`school_grade.py`)
- Add scoring system
- Implement letter grade calculation from percentage
- Add constraints (score cannot exceed max_score)
- Implement aggregation methods (course average, GPA)

### Key Concepts Day 3

| Concept | Description |
|---------|-------------|
| Unique constraint | `_sql_constraints` with UNIQUE |
| `ensure_one()` | Validates single record |
| `read_group()` | SQL-like aggregation |
| `mapped()` | Extract field values from recordset |
| `filtered()` | Filter recordset by condition |

### Run Day 3 Tests

```bash
python odoo-bin -c odoo.conf -d your_db --test-enable -u school_management_training --stop-after-init --test-tags school,enrollment,grade
```

---

## Day 4: Attendance & Wizards

### Goals
- Work with Datetime fields
- Implement bulk operations
- Create transient models (wizards)
- Handle context in wizards

### Tasks

#### Attendance Model (`school_attendance.py`)
- Track check-in/check-out times
- Implement bulk attendance creation
- Add reporting methods
- Create cron job method

#### Wizards (`wizard/enrollment_wizard.py`)
- Bulk enrollment wizard
- Bulk grade entry wizard
- Bulk attendance wizard
- Handle context (active_ids)

### Key Concepts Day 4

| Concept | Description |
|---------|-------------|
| `fields.Datetime` | Date with time |
| `models.TransientModel` | Temporary data (wizards) |
| `default_get()` | Override for context-based defaults |
| Context | `self.env.context` for passed data |
| `Command` | Create/update/delete in One2many |

### Run Day 4 Tests

```bash
python odoo-bin -c odoo.conf -d your_db --test-enable -u school_management_training --stop-after-init --test-tags school,attendance,wizard
```

---

## Day 5: Views, Reports & Polish

### Goals
- Complete all XML views
- Create PDF reports
- Polish the user experience
- Run all tests and fix issues

### Tasks

#### Views (in `views/` folder)
- Complete form views with proper layout
- Add list views with decorations
- Create kanban views for visual appeal
- Implement search views with filters

**Important Odoo 19 Note**: Use `<list>` instead of `<tree>` for list views!

```xml
<!-- CORRECT for Odoo 19 -->
<list string="Students">
    <field name="name"/>
</list>

<!-- WRONG - deprecated -->
<tree string="Students">
    <field name="name"/>
</tree>
```

#### Reports (in `report/` folder)
- Complete student report card template
- Add course detail report
- Style with Bootstrap classes

### Key View Concepts

| Element | Purpose |
|---------|---------|
| `<form>` | Single record view |
| `<list>` | Multiple records (Odoo 19+) |
| `<kanban>` | Card-based view |
| `<search>` | Filters and grouping |
| `<pivot>` | Pivot table analysis |
| `<graph>` | Charts |
| `<calendar>` | Date-based view |

### Run All Tests

```bash
python odoo-bin -c odoo.conf -d your_db --test-enable -u school_management_training --stop-after-init --test-tags school
```

---

## Running Tests

### Test Commands

```bash
# Run ALL module tests
python odoo-bin -c odoo.conf -d your_db --test-enable -u school_management_training --stop-after-init

# Run specific test tags
python odoo-bin -c odoo.conf -d your_db --test-enable -u school_management_training --stop-after-init --test-tags school,student

# Available tags: school, student, teacher, course, enrollment, grade, attendance, wizard
```

### Understanding Test Output

```
test_01_student_creation_basic ... ok       # Test passed ✓
test_02_student_code_sequence ... FAIL      # Test failed ✗
test_03_default_state_is_draft ... ERROR    # Code error
```

- **ok**: Implementation is correct
- **FAIL**: Logic is incorrect
- **ERROR**: Code syntax error or missing field

### Test Locations

All tests are in the `tests/` folder:
- `test_school_student.py` - 23 tests
- `test_school_teacher.py` - 11 tests
- `test_school_course.py` - 19 tests
- `test_school_enrollment.py` - 18 tests
- `test_school_grade.py` - 22 tests
- `test_school_attendance.py` - 16 tests
- `test_wizards.py` - 9 tests

**Total: ~118 tests**

---

## Concepts Reference

### Field Types Quick Reference

```python
# Basic Types
fields.Char(string='Name', required=True, size=100, translate=True)
fields.Text(string='Description')
fields.Html(string='Content', sanitize=True)
fields.Boolean(string='Active', default=True)
fields.Integer(string='Quantity', default=0)
fields.Float(string='Price', digits=(10, 2))
fields.Date(string='Date', default=fields.Date.today)
fields.Datetime(string='Timestamp', default=fields.Datetime.now)
fields.Selection([('a', 'A'), ('b', 'B')], string='Type', default='a')
fields.Binary(string='File', attachment=True)
fields.Image(string='Photo', max_width=1024, max_height=1024)
fields.Monetary(string='Amount', currency_field='currency_id')

# Relational Types
fields.Many2one('other.model', string='Related', ondelete='cascade')
fields.One2many('other.model', 'inverse_field', string='Lines')
fields.Many2many('other.model', string='Tags')
```

### Decorators

```python
@api.depends('field1', 'field2')      # Computed field dependencies
@api.constrains('field')               # Python validation
@api.onchange('field')                 # UI change handler
@api.model                             # No record context
@api.model_create_multi                # Batch create optimization
```

### Common Patterns

```python
# Iterate records
for record in self:
    record.field = value

# Search records
records = self.env['model'].search([('field', '=', value)])

# Create records
record = self.env['model'].create({'field': value})

# Update records
record.write({'field': new_value})

# Delete records
record.unlink()

# Aggregate
result = self.env['model'].read_group(
    domain=[],
    fields=['field:sum'],
    groupby=['group_field']
)
```

---

## Common Mistakes to Avoid

### 1. Forgetting to iterate
```python
# WRONG - self could be multiple records
self.field = value

# CORRECT
for record in self:
    record.field = value
```

### 2. Missing @api.depends
```python
# WRONG - field won't update
def _compute_total(self):
    ...

# CORRECT
@api.depends('line_ids.amount')
def _compute_total(self):
    ...
```

### 3. Using `<tree>` in Odoo 19
```xml
<!-- WRONG for Odoo 19 -->
<tree>...</tree>

<!-- CORRECT -->
<list>...</list>
```

### 4. Constraint that doesn't iterate
```python
# WRONG
@api.constrains('field')
def _check_field(self):
    if self.field < 0:  # Only checks first record
        raise ValidationError("...")

# CORRECT
@api.constrains('field')
def _check_field(self):
    for record in self:
        if record.field < 0:
            raise ValidationError("...")
```

### 5. Forgetting store=True for searchable computed fields
```python
# WRONG - can't search or group by this field
total = fields.Float(compute='_compute_total')

# CORRECT
total = fields.Float(compute='_compute_total', store=True)
```

---

## Need Help?

1. Check the Odoo documentation: https://www.odoo.com/documentation/
2. Review similar implementations in standard Odoo modules
3. Read the test file to understand expected behavior
4. Use `import pdb; pdb.set_trace()` for debugging

**Good luck! 🎓**
