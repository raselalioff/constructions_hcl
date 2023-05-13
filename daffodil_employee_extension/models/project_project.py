# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, except_orm, UserError
import calendar
import math
import re


class ProjectProject(models.Model):
    _inherit = "project.project"
    _description = 'Projects'

    office_employee_id = fields.Char(string='Employee ID', related="user_id.employee_id.employee_id", store=True)
    department_id = fields.Many2one(string='Department', related="user_id.employee_id.department_id", store=True)

