{
    'name' : "Activity One & Two",
    'author' : "Mohammed Hassan",
    'category' : '',
    'version' : '18.0.1.0.0',
    'license': 'LGPL-3',
    'depends' : [ 
        'base'
     ],
    'data': [
        #Security
        'security/security_groups.xml',
        'security/ir.model.access.csv',
        'security/security.xml',

        #Data
        'data/sequences.xml',

        #Views
        'views/location_views.xml',
        'views/room_views.xml',
        'views/teacher_views.xml',
        'views/course_views.xml',
        'views/registration_views.xml',
        'views/main_menu.xml',

        #reports
        'reports/registration_report.xml',
     ],
    'application': True,
}