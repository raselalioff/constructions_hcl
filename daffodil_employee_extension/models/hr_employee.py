# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, except_orm, UserError
import calendar
import math
import re


class HrEmployee(models.Model):
    _inherit = "hr.employee"
    # _rec_name = "employee_id"
    _description = 'Employees'

    employee_id = fields.Char(string='Employee ID')

    sql_constraints = [
        ('employee_id_unique', 'unique(employee_id)', 'Employee ID already exists!')
    ]


    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        """ This method will find Customer names according to its mobile,
        phone, city, email and its job position."""
        if name and not self.env.context.get('import_file'):
            args = args if args else []
            args.extend(['|', ['name', 'ilike', name],
                         '|', ['work_email', 'ilike', name],
                         '|', ['work_phone', 'ilike', name],
                         '|', ['employee_id', 'ilike', name],
                         '|', ['department_id', 'ilike', name],
                         ['job_id', 'ilike', name]])
            name = ''
        return super(HrEmployee, self).name_search(
            name=name, args=args, operator=operator, limit=limit)


    def write(self, vals):
        res = super(HrEmployee, self).write(vals)
        try:
            if 'employee_id' in vals.keys():
                if self.user_id:
                    self.user_id.partner_id.sudo().write({ 'ref': vals['employee_id'] })
        except:
            pass
        return res

    
    def action_assign_employee_id_to_partner(self):
        employees = self.env['hr.employee'].search([])
        for employee in employees:
            if employee.user_id:
                employee.user_id.partner_id.sudo().write({ 'ref': employee.employee_id })
        
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

