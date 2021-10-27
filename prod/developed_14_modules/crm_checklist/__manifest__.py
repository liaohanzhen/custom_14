# -*- encoding: utf-8 -*-
###########################################################################
#    Copyright (C) 2016 - Almighty Consulting Services. <http://www.almightycs.com>
#
#    @author Almighty Consulting Services <info@almightycs.com>
###########################################################################

{
    'name': 'CRM Checklist',
    'version': '1.0',
    'author': 'Nikunj Antala',
    'support': '',
    'category': 'CRM',
    'summary': 'CRM Checklist',
    'description': """Manage Checklist on CRM
    
Making a customer from an opportunity is the only goal of CRM pipeline. To achieve that goal sales staff needs to undertake a specific sequence of actions. Each of those actions is important on a definite funnel stage. Efficient companies know that missing of any step might result in a long-run failure. This is the tool to make sure such a failure will not happen. The app provides a check list for each pipeline stage to control over requirements' fulfilment, and make sure that each action is fully approved by responsible users.

- Check lists are assigned per each opportunity stage. Set of check list points is up to you
- As soon as an opportunity is moved to a certain stage, its check list is updated to a topical one from this stage. For instance, actions for 'new' and 'proposition' stages must be different, don't they?
- To move a CRM lead forward in your funnel, a check list should be fully confirmed. By 'moving forward' any change of stage with lesser sequence to a bigger sequence is implied
- Confirmation might assume involvement of different user roles. Certain check list points might be approved only by top-level employees, for example. In such a case just assign a user group for this check list item
- For some situations you do not need a check list fulfilment even a new stage is further. For example, for the 'Cancelled' stage. In such a case just mark this stage as 'No need for checklist'
    """,
    'depends': ['crm','sale_crm'],
    'website': 'http://sheliyainfotech.com',
    'data': [
        "security/ir.model.access.csv",
        "views/crm_view.xml",
        "views/crm_stage_view.xml",
    ],
    'images': [
        'static/description/project_checklist_cover_almightycs.jpg',
    ],
    'application': False,
    'sequence': 1,
}
