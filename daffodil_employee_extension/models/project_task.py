# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, except_orm, UserError
import calendar
import math
import re


class ProjectTask(models.Model):
    _inherit = "project.task"
    _description = 'Project Tasks'

    office_employee_id = fields.Char(string='Employee ID', related="user_id.employee_id.employee_id", store=True)

