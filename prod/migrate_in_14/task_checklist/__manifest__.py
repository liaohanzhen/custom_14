# -*- coding: utf-8 -*-
{
    "name": "Task Check List and Approval Process",
    "version": "14.0.2.0",
    "category": "Project",
    "author": "Odoo Tools",
    "website": "https://odootools.com/apps/12.0/task-check-list-and-approval-process-137",
    "license": "Other proprietary",
    "application": True,
    "installable": True,
    "auto_install": False,
    "depends": [
        "project"
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/project_task_type.xml",
        "views/project_task.xml",
        "views/check_list.xml",
        "data/data.xml"
    ],
    "qweb": [
        
    ],
    "js": [
        
    ],
    "demo": [
        
    ],
    "external_dependencies": {},
    "summary": "The tool to make sure required jobs are carefully done on this task stage",
    "description": """
    When you define project stages, you consider some requirements a task should satisfy to be there and to be moved forward. Those requirements are of high importance to make project running smoothly. Missing of any step might lead to a long-run troubles. To avoid those troubles use this tool. The app provides a check list for each task stage to control over requirements' fulfilment, and to make sure that each action is fully approved by responsible users.

    Check lists are assigned per each task stage. Set of check list points is up to you. Check list fulfilment is shown on task kanban and form views to easily control progress
    As soon as a task is moved to a certain stage, its check list is updated to a topical one from this stage. For example, actions for 'draft' and 'in progress' stages should be different, shouldn't they?
    To move a task forward through your project pipeline, a check list should be fully confirmed. By 'moving forward' any change of stage with lesser sequence to a bigger sequence is implied
    Confirmation might assume involvement of different user roles. Certain check list points might be approved only by top-level employees. For example, cost calculations are confirmed by Financial managers. In such a case just assign a user group for this check list item 
    Check list actions are saved in the task history. In case a task is moved back, already done check list items would be recovered. However, in case the 'not saved' option is set for the item up, the point should be approved each time from scratch
    The tool let you grant users with the super check list rights right on a user form. In such a case, such users are able (a) to confirm any check points disregarding defined user groups; (b) move any task further without fulfilling check lists

    For certain situations you do not need a check list fulfilment even a new stage is further. For example, for the 'Cancelled' stage. In such a case just mark this stage as 'No need for checklist'
    Task check list per stages
    Task stage check lists
    Check list to be confirmed before moving a task further
    Approval process distributed by various user roles
    Tasks check list progress kanban view
    The super rights to approve any check items and move tasks
    Check list tree view
""",
    "images": [
        "static/description/main.png"
    ],
    "price": "28.0",
    "currency": "EUR",
}