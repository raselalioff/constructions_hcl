# -*- coding: utf-8 -*-
# Part of Browseinfo. See LICENSE file for full copyright and licensing details.
{
    'name': 'HR employee Advance Expense Request in Odoo',
    'version': '14.0.0.0',
    'category': 'Human Resources',
    'summary': 'Expense Advance Request of Employee Expense request Advance Expense Request of Employee Expense Multiple Request Expense Request Approve by Manager Employee Expense with Accounting Entry hr Expense Advance Request human resources Advance Expense Request',
    'description': """This app allows your employees to create advance request for expenses. This app will work with multi currency.
	
	Expense Advance Request - Employee
	Expense Advance Request hr 
	 hr Expense Advance Request
	 human resource Expense Advance Request
	 human resources Advance Expense Request
	 
This module allow your employees to create advance request for expenses. This module will work with multi currency.

Note: We have not changed any accounting entries for expense or expense sheet, we are just showing advance taken for that expense by employee.

Created Menus :
employee Advance Expense Request
employee Expense Request
employee expenses request

Expenses/Expense Advances
Expenses/Expense Advances/Expense Advance Requests
Expenses/Expense Advances/Advance to Approve
Expenses/Expense Advances/Advance to Pay
Defined Reports
employee Expense Multiple Request.
Expense Request Approve by HR Manager.
Integrated with Expense and Accounting Entry.

Print Advance Expense
	
	
	 """,
    
	
	
	'author': 'BrowseInfo',
    "price": 15,
    "currency": 'EUR',
    'website': 'https://www.browseinfo.in',
    'depends': ['base','account','hr_expense','hr'],
    'data': ['security/ir.model.access.csv',
            'security/groups.xml',
            'views/advance_expense_views.xml',
            'views/expence_inherit_view.xml',
            'report/report_views.xml',
            'report/advance_expence_report.xml',],
    'installable': True,
    'auto_install': False,
    'application': True,
    'live_test_url': 'https://youtu.be/18MNZMwmmFM',
    "images":['static/description/Banner.png'],
}
