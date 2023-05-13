from odoo import models, fields, api, _
from odoo.exceptions import UserError
from lxml import etree

class AccountInvoice(models.Model):
    _inherit = "account.move"

    is_lease = fields.Boolean('Is Lease')
    is_sale = fields.Boolean('Is Sale')
    proposal_id = fields.Many2one('land.proposal','Property')
 
class AccountInvoiceLine(models.Model):
    _inherit = "account.move.line"

    is_lease = fields.Boolean('Is Lease')
    is_sale = fields.Boolean('Is Sale')
    proposal_id = fields.Many2one('land.proposal','Property')  
    from_date = fields.Date('From Date')  
    to_date = fields.Date('To date') 
    unit = fields.Char('Unit')











