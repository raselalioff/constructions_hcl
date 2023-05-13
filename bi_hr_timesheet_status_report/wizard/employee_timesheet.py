# -*- coding: utf-8 -*-
# Part of Browseinfo. See LICENSE file for full copyright and licensing details.


from odoo import models, fields, api, _
from datetime import date, timedelta
from odoo.exceptions import UserError
import base64


class Employees_Timesheet_Reports(models.TransientModel):
    _name = "employee.timesheet.report"
    
    
    def incomplete_sheets_cron(self):
        end_date = fields.datetime.now() 
        start_date = end_date - timedelta(7)

        
        employees = self.env['hr.employee'].search([])
        a = self.env['employee.timesheet.report'].create({'start_date' :start_date ,
                                                     'end_date' : end_date ,
                                                    
                                                    'employee_ids' : [(6,0,employees.ids)]} )
        
        
        company_obj = self.env['res.users'].browse(self.env['res.users']._context['uid']).company_id
        send_to_list = []

        for i in company_obj.res_users_ids :
            send_to_list.append(i.login)
        a._compute_incomplete_sheets_cron(a)

        emal_to = ','.join(send_to_list)
       
        result = self.env.ref('bi_hr_timesheet_status_report.report_employee_timesheet_print')._render_qweb_pdf([a.id], data={'report_type': 'pdf'})[0]
        data = base64.b64encode(result)
        
        attachment_obj = self.env['ir.attachment']

        attachment = attachment_obj.create({'name' : "Timesheet Reports",
                                            'type' : 'binary',
                                            'datas' : data})

        

        template_id = self.env.ref('bi_hr_timesheet_status_report.incompalete_timesheet_email_template')
        email_template_obj = self.env['mail.template'].browse(template_id.id)
        values = email_template_obj.generate_email(self.id, fields=['subject', 'body_html', 'email_from', 'email_to', 'partner_to', 'email_cc', 'reply_to', 'scheduled_date'])
        values['email_from'] = self.env['res.users'].browse(self.env['res.users']._context['uid']).partner_id.email
        values['email_to'] = str(emal_to)
        values['res_id'] = self.id
        values['attachment_ids'] = [(6,0,[attachment.id])]
        values['author_id'] = self.env['res.users'].browse(self.env['res.users']._context['uid']).partner_id.id
        values['body_html'] = 'Hello , Please find the attached timesheet report. \n Thank You,'

             
        mail_mail_obj = self.env['mail.mail']       
        msg_id = mail_mail_obj.sudo().create(values)
        
        if msg_id:
            mail_mail_obj.send([msg_id])
            msg_id.send()
                                                     
        return True



    def _compute_incomplete_sheets_cron(self,res):
        data = []
        incomplete_list = []
        for employee in res.employee_ids :
            per_day_hour = employee.resource_calendar_id.hours_per_day
            delta = res.end_date - res.start_date
            days = 0
            for i in range(delta.days + 1):
                date1 = res.start_date + timedelta(i)
                if date1.weekday()<5:
                    days=days+1
                else:
                    pass
            work_hour = days*per_day_hour
            
            domain_1 = [('date','>=',res.start_date),('date','<=',res.end_date),('employee_id','=',employee.id)]
            timesheet_obj = self.env['account.analytic.line'].search(domain_1)
            
            total = 0.0
            for i in timesheet_obj :
                total = total + i.unit_amount
                            
            incomplete_obj = self.env['incomplete.timesheet']
            if work_hour > total :
                
                a= incomplete_obj.create({'employee_id':employee.id,
                                'timesheet_id' : res.id,
                                'manager_id' : employee.department_id.manager_id.id,
                                'working_hours' : str(work_hour),
                                'timesheet_hours' : str(total),
                                'missing_hours' :str(work_hour - total)})

                
                incomplete_list.append(a.id)


        res.incomplete_ids = [(6,0,incomplete_list)]
        
        return



    
    def _compute_incomplete_sheets(self):
        data = []
        incomplete_list = []
        for employee in self.employee_ids :
            per_day_hour = employee.resource_calendar_id.hours_per_day
            delta = self.end_date - self.start_date
            days = 0
            for i in range(delta.days + 1):
                date1 = self.start_date + timedelta(i)
                if date1.weekday()<5:
                    days=days+1
                else:
                    pass
            work_hour = days*per_day_hour
            
            domain_1 = [('date','>=',self.start_date),('date','<=',self.end_date),('employee_id','=',employee.id)]
            timesheet_obj = self.env['account.analytic.line'].search(domain_1)
            
            total = 0.0
            for i in timesheet_obj :
                total = total + i.unit_amount
                
                
            incomplete_obj = self.env['incomplete.timesheet']
            if work_hour > total :
                
                a= incomplete_obj.create({'employee_id':employee.id,
                                'timesheet_id' : self.id,
                                'manager_id' : employee.department_id.manager_id.id,
                                'working_hours' : str(work_hour),
                                'timesheet_hours' : str(total),
                                'missing_hours' :str(work_hour - total)})

                
                incomplete_list.append(a.id)


        self.incomplete_ids = [(6,0,incomplete_list)]
        return

    start_date = fields.Datetime(string="Start Date",required=True)
    end_date = fields.Datetime(string="End Date",required=True)
    partner_id = fields.Many2one('res.partner')

    employee_ids = fields.Many2many('hr.employee','rel_multiple_employee_ids',string="Employees")
    incomplete_ids = fields.One2many('incomplete.timesheet','timesheet_id',string="Incomplete Timesheet")


    def print_pdf_report(self):
        self._compute_incomplete_sheets()
        return self.env.ref('bi_hr_timesheet_status_report.report_employee_timesheet_print').report_action(self)

class Employee_incomplete_timesheet(models.TransientModel):
    _name = 'incomplete.timesheet'


    timesheet_id = fields.Many2one('employee.timesheet.report')
    employee_id  = fields.Many2one('hr.employee',string="Employee")
    manager_id = fields.Many2one('hr.employee',string="Manager")
    working_hours = fields.Char(string="Working Hours")
    timesheet_hours = fields.Char(string="Timesheet Hours")
    missing_hours = fields.Char(string="Missing Hours")