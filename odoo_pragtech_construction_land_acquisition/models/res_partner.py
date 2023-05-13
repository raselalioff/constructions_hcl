from odoo import models, fields, api, _
from datetime import datetime, date

class Partner(models.Model):
    _inherit = 'res.partner'
    
    is_owner = fields.Boolean('Owner')
    is_agent_consultant = fields.Boolean('Agent/Consultant')
