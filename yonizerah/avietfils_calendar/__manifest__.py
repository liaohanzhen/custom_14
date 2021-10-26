{
    'name': 'Avietfils Calendar',
    'version': '14.0.1.0',
    'summary': 'Enhance Calendar View',
    'description': 'Enhance Calendar View',
    'category': 'Productivity',
    'author': 'Avietfils',
    'license': 'AGPL-3',
    'depends': ['base', 'calendar', ],
    'data': [
        'views/calendar_views.xml',
        'views/template.xml',
    ],
    'qweb': [
        'static/src/xml/web_calendar.xml',
    ],
    'installable': True,
    'auto_install': False,
}