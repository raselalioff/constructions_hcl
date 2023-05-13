# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, except_orm, UserError
import calendar
import math
import re


class ResPartner(models.Model):
    _inherit = "res.partner"
    _description = 'Partners'

    employee_id_id = fields.Char(string='Employee ID', readonly=True)

