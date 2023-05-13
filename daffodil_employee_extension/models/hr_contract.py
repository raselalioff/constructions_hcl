# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, except_orm, UserError
import calendar
import math
import re


class HrContract(models.Model):
    _inherit = "hr.contract"
    _description = 'Contracts'

    office_employee_id = fields.Char(string='Employee ID', related="employee_id.employee_id", store=True)