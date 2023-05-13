# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, except_orm, UserError
import calendar
import math
import re


class HrEmployeeDocument(models.Model):
    _inherit = "hr.employee.document"
    _description = 'Employee Documents'

    office_employee_id = fields.Char(string='Employee ID', related="employee_ref.employee_id", store=True)
    department_id = fields.Many2one(string='Department', related="employee_ref.department_id", store=True)

