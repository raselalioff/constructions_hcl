# -*- coding: utf-8 -*-
# Part of Browseinfo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, _
import datetime

class Company(models.Model):
    _inherit = "res.company"

    res_users_ids = fields.Many2many('res.users','rel_company_to_users',string = "Timesheet Status Followers")
	    