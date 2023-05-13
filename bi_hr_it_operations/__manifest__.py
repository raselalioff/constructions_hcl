# -*- coding: utf-8 -*-
# Part of Browseinfo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Equipment Request & IT Operations Odoo App',
    'version': '14.0.0.4',
    'category': 'human resources',
    'summary': 'This app allow employees to send requests to HR department for equipment hardware and software Equipment Request & IT Operations Request HR item request HR stationery Request office HR Request HR Employee IT Operations and employee Equipment Requests',
    'description': """This app allow employees to send requests to HR department for equipment hardware and software Equipment Request & IT Operations Request HR item request HR stationery Request office HR Request HR Employee IT Operations and employee Equipment Requests"
	This module allow employees to send requests to HR department for equipments type of hardware and software.

Available Features:
  * Allow employee to request for hardware/software resource to HR department.
  * Allow employee to request for damage hardware and expense integrated with HR expenses.
  * Integrated with Warehouse.
  * Print PDF report of Equipments.
  * HR can generate expense for damages.
  * Stock user can generate internal transfer for equipment requess.
Workflow:

      * Draft->Waiting for Approval->Approved by Department->Approved by HR->Equipment Assigned->Refused->Rejected

Menus Available:
Equipments Management
Equipments/Equipments
Equipments/Equipments/My Equipment Requests
Equipments/Equipments/Department Equipment Requests to Approve
Equipments/Equipments/HR Equipment Requests to Approve
Equipments/Equipments/Stock Equipment Requests to Approve
Equipment Requests

	""",
    'author': 'BrowseInfo',
    'website': 'https://www.browseinfo.in',
    "price": 35,
    "currency": 'EUR',
    'depends': ['base','hr','hr_expense','stock'],
    'data': [   'security/ir.model.access.csv',
                'security/groups.xml',
                'views/my_equipment_views.xml',
                'report/report_equipment.xml',
                'report/report_views.xml'],
    'installable': True,
    'auto_install': False,
    'application': True,
    'live_test_url':'https://youtu.be/4muK5NBToZI',
    "images":["static/description/banner.png"],
}
