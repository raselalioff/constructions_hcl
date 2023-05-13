# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, except_orm, UserError
import calendar
import math
import re


class NoteNote(models.Model):
    _inherit = "note.note"
    _description = 'Notes'

    office_employee_id = fields.Char(string='Employee ID', related="responsible_user.employee_id.employee_id", store=True)

