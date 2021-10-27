# -*- encoding: utf-8 -*-
{
    'name': 'Project Portal Attachment',
    'version': '14.0',
    'author': 'Nilesh Sheliya',
    'support': 'sheliyanilesh@gmail.com',
    'category': 'Project Management',
    'summary': 'Show attachments in portal Project',
    'description': """
        User can see project attachments from its portal access.
    """,
    'depends': ['project', 'portal_documents'],
    'website': '',
    'data': [
        "security/security.xml",
        "views/project_view.xml",
        "views/project_task_view.xml",
        "views/project_portal_template.xml",
    ],
    
    'application': False,
    'sequence': 1,
}
