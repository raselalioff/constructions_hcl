from odoo import fields, api, models


class Regular(models.Model):
    _inherit = 'hr.attendance'

    regularization = fields.Boolean(string="Regularization")
    comment = fields.Char('Comments')

