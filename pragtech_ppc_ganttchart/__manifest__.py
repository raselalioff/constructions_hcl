# -*- coding: utf-8 -*-
{
    'name': "Project Planning and Gantt Chart",
    'version': '14.3',
    'author': 'Pragmatic TechSoft Pvt Ltd.',
    'website': "www.pragtech.co.in",
    'category': 'Construction',
    'summary': "Created Gantt chart based on hierarchy of project,subproject,wbs,task groups and tasks gantt chart project planning construction gantt chart project controlling project planning in odoo gantt chart in odoo construction",
    'description': """
Project Planning and Gantt Chart
================================
Created Gantt chart based on hierarchy of project,subproject,wbs,task groups and tasks
<keywords>
gantt chart
project planning
construction gantt chart
project controlling
project planning in odoo
gantt chart in odoo 
construction
odoo construction
    """,
    'depends': ['web', 'base', 'pragtech_ppc'],
    'data': [
        'security/ir.model.access.csv',
        'views/assets.xml',
#         'views/project_view.xml',
        'wizard/wizard_gantt_view.xml',
    ],
    'qweb': ['static/src/xml/base.xml'],
    'demo': ['demo/demo.xml', ],
    'images': ['images/Animated-Construction-gantchart.gif'],
    'live_test_url': 'https://www.pragtech.co.in/company/proposal-form.html?id=103&name=gantt-chart',
    'license': 'OPL-1',
    'price': 194.60,
    'currency': 'USD',
    'installable': True,
    'auto_install': False,
}
