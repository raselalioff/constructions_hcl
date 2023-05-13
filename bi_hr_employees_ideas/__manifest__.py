# -*- coding: utf-8 -*-
# Part of Browseinfo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Share Employee Ideas in Odoo',
    'version': '14.0.0.1',
    'category': 'human resources',
    'summary': 'Apps for Employee Share Ideas HR employee share ideas HR share ideas Employee Idea Request Form Employee can create and post the idea for approval HR IDEA approval REQUEST Employee idea request and approval',
    'description': """Employee Ideas (Human Resource)
	employee idea 
This module allow employees in the company to raise and create ideas and after approval of ideas other employees in departments can vote for that idea. 
Menus:

Ideas
Ideas/Configurations
idea from employees 
Ideas/Configurations/Idea Types
Ideas/Employee Ideas
Ideas/Employee Ideas/Ideas
Idea Request Form
Employee can create and post the idea for approval. """,
    'author': 'BrowseInfo',
    'website': 'https://www.browseinfo.in',
    "price": 10,
    "currency": 'EUR',
    'depends': ['base','hr'],
    'data': ['security/ir.model.access.csv',
            'wizard/vote_wizard_views.xml',
            'views/ideas_view.xml',
            'views/idea_type_view.xml',
            'report/employee_idea_report.xml',
            'report/report_views.xml',
            ],
    'installable': True,
    'auto_install': False,
    'application': True,
    "live_test_url":'https://youtu.be/jFV1Brs2gKA',
    "images":["static/description/banner.png"],
}
