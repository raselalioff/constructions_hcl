# -*- coding: utf-8 -*-
# Part of Browseinfo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Timesheet Incomplete Report Employees in Odoo',
    'version': '14.0.0.0',
    'category': 'human resources',
    'summary': 'Apps for Print Employee Timesheet Incomplete Report for Employee print timesheet report for incomplete timesheet of employees Timesheet Status Report Print Timesheet Status employee attendance report Timesheet Incomplete Report timesheet report',
    'description': """
	Timesheet Incomplete Report Employees
This module allow management to print timesheet report for incomplete timesheet of employees.

Created Menus: Timesheets/Reporting/Timesheet Status Report

Defined Reports: Print Timesheet Status
employee timesheet status report 
employee attandance report
Timesheet Incomplete Report
timesheet report
timesheet status reports
timesheet status report
Print Timesheet Status report



Timesheet Incomplete Report Employees


	 """,
	 
    'author': 'BrowseInfo',
    "price": 30,
    "currency": 'EUR',
    'website': 'https://www.browseinfo.in',
    'depends': ['base','hr','hr_timesheet'],
    'data': ['security/ir.model.access.csv',
            'views/res_company_inherit_view.xml',
            'wizard/employee_timesheet_view.xml',
            'views/mail_template_timesheet.xml',
            'data/cron_email.xml',
            'report/incomplete_timesheet_report.xml',
            'report/report_views.xml',],
    'installable': True,
    'auto_install': False,
    'application': True,
    "live_test_url":'https://youtu.be/4_3vcRJ27Qs',
    "images":["static/description/Banner.png"],
}
