# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, except_orm, UserError
import calendar
import math
import re


class HrDepartment(models.Model):
    _inherit = "hr.department"
    _description = 'Departments'

    total_employees = fields.Integer(string='Total Employees', compute="_get_department_employee_count")


    def _get_department_employee_count(self):
        for line in self:
            line.total_employees = self.env['hr.employee'].sudo().search_count([('department_id','=',line.id)])


