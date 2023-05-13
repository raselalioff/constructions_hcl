from odoo import models, fields, api
from odoo.exceptions import Warning


class PO_Bill_Summary_Wizard(models.TransientModel):
    _name = 'po.bill.summary.wizard'
    _description = 'PO Bill Summary'

    project_id = fields.Many2one('project.project', 'Project')
#     sub_project = fields.Many2one('sub.project', 'Sub Project')
    project_wbs_id = fields.Many2one('project.task', 'Project WBS', domain=[
        ('is_wbs', '=', True), ('is_task', '=', False)])
    invoice_id = fields.Many2one('account.invoice', 'Bill Number')
    partner_id = fields.Many2one('res.partner', 'Vendor')
    stage_id = fields.Many2one('stage.master', 'Stage')
    from_date = fields.Date('From Date')
    to_date = fields.Date('To Date')
    order_line = fields.One2many(
        'po.bill.summary.lines.wizard', 'order_id', string='Order Lines', copy=True, ondelete='cascade')

    @api.onchange('project_id')
    def onchange_project_id(self):
        if self.project_id:
            return {'domain': {'project_wbs_id': [('project_id', '=', self.project_id.id), ('is_wbs', '=', True), ('is_task', '=', False), ('is_group', '=', False)],
                               'purchase_order_id': [('project_id', '=', self.project_id.id)], }}

    @api.onchange('project_wbs_id')
    def onchange_project_wbs_id(self):
        if self.project_wbs_id:
            return {'domain': {'puchase_order_id': [('project_wbs', '=', self.project_wbs_id.id)], }}

    def compute_purchase_orders(self):
        self.order_line.unlink()
        if self.from_date > self.to_date:
            raise Warning("From Date should be lesser than To Date")
        domain = []
        if self.project_id:
            domain.append(('project_id', '=', self.project_id.id))
        if self.project_wbs_id:
            domain.append(('project_wbs_id', '=', self.project_wbs_id.id))
        if self.invoice_id:
            domain.append(('id', '=', self.invoice_id.id))
        if self.partner_id:
            domain.append(('partner_id', '=', self.partner_id.id))
        if self.stage_id:
            domain.append(('stage_id', '=', self.stage_id.id))
        if self.from_date:
            domain.append(('date_invoice', '>=', self.from_date))
        if self.to_date:
            domain.append(('date_invoice', '<=', self.to_date))
        if domain == []:
            domain = ([])
        acc_obj = self.env['account.move'].search(domain)
        vals = {}
        for rec in acc_obj:
            for line in rec.invoice_line_ids:
                vals = {
                    'project_id': rec.project_id.id,
                    'project_wbs_id': rec.project_wbs_id.id,
                    'invoice_id': rec.id,
                    'challan_no': line.picking_id.challan_no,
                    'challan_date': line.picking_id.challan_date,
                    'purchase_id': line.picking_id.po_id.id,
                    'partner_id': rec.partner_id.id,
                    'date_invoice': rec.date,
                    'stage_id': rec.stage_id.id,
                    'product_id': line.product_id.id,
                    'quantity': line.quantity,
                    'price_unit': line.price_unit,
                    'total': line.price_subtotal,
                    'amount_tax': rec.amount_tax,
                    'order_id': self.id,
                }
                value = self.order_line.create(vals)
        view_id = self.env.ref(
            'pragtech_purchase.purchase_order_bill_summary_wizard_form_view').id
        return {
            'context': self.env.context,
            # 'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'po.bill.summary.wizard',
            'res_id': self.id,
            'view_id': view_id,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }


class PO_Bill_SummaryLines_Wizard(models.TransientModel):
    _name = 'po.bill.summary.lines.wizard'
    _description = 'PO Bill Summary Lines'

    project_id = fields.Many2one('project.project', 'Project')
    project_wbs_id = fields.Many2one('project.task', 'Project WBS', domain=[
        ('is_wbs', '=', True), ('is_task', '=', False)])
    invoice_id = fields.Many2one('account.invoice', 'Bill No.')
    challan_no = fields.Char("Challan No.")
    challan_date = fields.Datetime('Challan Date')
    product_id = fields.Many2one("product.product", "Product")
    quantity = fields.Integer("Quantity")
    purchase_id = fields.Many2one('purchase.order', 'Purchase Order')
    partner_id = fields.Many2one('res.partner', 'Vendor')
    stage_id = fields.Many2one('stage.master', 'Status')
    date_invoice = fields.Datetime('Bill Date')
    price_unit = fields.Float(string='Unit Price')
    amount_tax = fields.Float(string='Taxes')
    total = fields.Float(string='Total')
    order_id = fields.Many2one(
        'po.bill.summary.wizard', string='Order Reference', ondelete='cascade')
