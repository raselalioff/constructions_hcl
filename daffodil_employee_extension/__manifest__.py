# -*- coding: utf-8 -*-
{
    'name': 'Employee Extension',
    'summary': """Employee Extension""",
    'description': """
Employee Extension
==================
Additional fields and functionality for employee.
    """,
    'version': '13.0.1.0',
    'author': 'Jeshad Khan',
    'company': 'Daffodil Software Limited',
    'website': 'https://github.com/JeshadKhan',
    'category': 'Employees',
    'sequence': 1,
    'depends': [
        'base',
        'contacts',
        'hr',
        'hr_contract',
        'project',
    ],
    'data': [
        ## View
        'views/res_partner_view.xml',
        'views/hr_employee_view.xml',
        'views/hr_contract_view.xml',
        'views/project_task_view.xml',
        'views/hr_department_view.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
    'icon': "/daffodil_employee_extension/static/description/icon.png",
    "images": ["/static/description/banner.png"],
    "license": "OPL-1",
    "price": 0,
    "currency": "EUR",
}
