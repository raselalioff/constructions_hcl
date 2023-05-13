from odoo import models, fields, api
from odoo.exceptions import Warning
from odoo.tools.translate import _


class purchaseConsumption(models.Model):
    _name = 'purchase.consumption'
    _description = 'Purchase Consumption'

    @api.model
    def _default_stage(self):
        st_id = self.env['stage.master'].search([('draft', '=', True)])
        if st_id:
            return st_id.id

    is_use = fields.Boolean('Use')
    name = fields.Char('consumption No.')
    group_id = fields.Many2one('project.task', 'Task Group')
    task_id = fields.Many2one('project.task', 'Task')
    flag = fields.Boolean('Flag', default=False)
    material_id = fields.Many2one('product.product', 'Material')
    consumption_date = fields.Date(
        'Date', default=fields.date.today(), required=True)
    requirement_date = fields.Date('Requirement Date')
    procurement_date = fields.Date('Procurement Date')
    quantity = fields.Integer(' Quantity')
    specification = fields.Char('Specification')
    remark = fields.Char('Remark')
    model = fields.Char('Related Document Model', index=1)
    mesge_ids = fields.One2many('mail.messages', 'res_id', string='Massage',
                                domain=lambda self: [('model', '=', self._name)], auto_join=True, readonly=True)
    # previous quantity fields
    total_approved_qty = fields.Float('Approved Qty', readonly=True)
    total_ordered_qty = fields.Float('Ordered Qty', readonly=True)
    consumption_qty = fields.Float('consumption Qty')
    balance_qty = fields.Float('Balance Qty', compute='get_balanced_qty')

    # latest as suggested on 26/12/16 quantity fields
    estimated_qty = fields.Float('Estimated Qty')
    consumption_as_on_date = fields.Float('Consumption as on date')
    current_consum_qty = fields.Float('Current consumption Qty')
    consumption_ids = fields.One2many(
        'purchase.consumption.line', 'order_id')
    status = fields.Selection(
        [('active', 'Active'), ('inactive', 'Inactive')], 'Status')
    priority = fields.Selection([('high', 'High'), ('low', 'Low')], 'Priority')
    brand_id = fields.Many2one('brand.brand', 'Brand')
    consumption_type = fields.Selection(
        [('estimated', 'Estimated'), ('non_estimated', 'Non Estimated')], 'Type')
    unit = fields.Many2one('uom.uom', 'Unit', required=True)
    rate = fields.Float('Rate')
    procurement_type = fields.Selection([('New Purchase from Supplier', 'New Purchase from Supplier'),
                                         ('Cash Purchase ', 'Cash Purchase '),
                                         ('IST from other sites', 'IST from other sites'), ], "Procurement Type")
    warehouse_id = fields.Char('Procurement Type', readonly=True)
    product_location_id = fields.Many2one('stock.location', "Location")
    purchase_ids = fields.Many2many(
        'purchase.order', 'po_consumption_rel1', 'consumption_id', 'purchase_id', string='Purchase Orders')
    consumption_fulfill = fields.Boolean(
        'Req fulfill', compute='is_consumption_fulfill')
    stage_id = fields.Many2one(
        'stage.master', 'Stage', default=_default_stage, readonly=True, copy=False, track_visibility='onchange')
    project_wbs = fields.Many2one('project.task', 'project WBS', domain=[
        ('is_wbs', '=', True), ('is_task', '=', False)])
    project_id = fields.Many2one('project.project', 'Project')

    sub_project = fields.Many2one('sub.project', 'Sub Project')
    estimation_id = fields.Many2one('task.material.line', 'Estimate No.')

    material_category = fields.Many2one(
        'product.category', string='Material Category', related='material_id.categ_id', store=True)
    related_task_category = fields.Many2one(
        'task.category', related='task_id.category_id', store=True)
    task_category = fields.Many2many(
        'task.category', 'purchase_cons_req_task_cat_rel', 'purchase_req_id', 'task_category_id', string='Task Category')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
    ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')
    me_sequence = fields.Char(readonly=True)
    counter = 0

    @api.depends('current_consum_qty', 'total_ordered_qty')
    def get_balanced_qty(self):
        for id in self:
            id.balance_qty = id.quantity - \
                (id.current_consum_qty + id.consumption_as_on_date)

    @api.depends('current_consum_qty')
    @api.onchange('current_consum_qty')
    def validate_req_qty(self):
        self.balance_qty = self.quantity - \
            (self.total_ordered_qty + self.current_consum_qty)
        if self.balance_qty < 0.0:
            raise Warning(_('Invalid Current consumption Qty'))

#     @api.multi
#     def unlink(self):
#         ids = []
#         for line in self:
#             ids.append(line.id)
#         Purchase_order_obj = self.env['po.consumption'].search(
#             [('consumption_id', 'in', ids)])
#         if Purchase_order_obj:
#             raise Warning(
#                 _('You cannot delete consumption which is used in Purchase Order .'))

    # @api.model
    # def is_consumption_fulfill(self):
    #     total_qty = 0
    #     po_line_obj = self.env['purchase.order.line'].search(
    #         [('consumption_id', '=', self.id)])
    #     for line in po_line_obj:
    #         total_qty = +line.product_qty
    #     if total_qty > self.quantity_consumption:
    #         res = self.update({'requsition_fulfill': True})
    #         return True

    def change_state(self, context={}):
        if self.counter == 0:
            self.counter = self.counter + 1
            if context.get('copy'):
                self.write({'state': 'confirm'})
                if self.product_location_id:
                    reference = "COSUM" + str(self.id)
                    stock_move = self.env['stock.move.line'].search([('product_uom_qty', '=', self.current_consum_qty), (
                        'location_id', '=', self.product_location_id.id), ('reference', '=', reference)])
                    if stock_move:
                        stock_move.write(
                            {'state': 'done', 'qty_done': stock_move.product_uom_qty})
                    location_ids = self.env['stock.quant'].search(
                        [('product_id.id', '=', self.material_id.id),
                         ('location_id', '=', self.product_location_id.id)])
                    # location_ids.reserved_quantity=0
                    # reserved_quantity=location_ids.reserved_quantity
                    for id in location_ids:
                        id.sudo().reserved_quantity = id.reserved_quantity - \
                            (self.current_consum_qty)
                        id.sudo().quantity = id.quantity - self.current_consum_qty

            """Updating consumption till date in estimation table"""

#             requisition_till_date = self.estimation_id.requisition_till_date + \
#                                     self.current_consum_qty
            requisition_till_date = self.current_consum_qty
            if requisition_till_date <= self.estimation_id.material_uom_qty:
                #                 self.estimation_id.requisition_till_date = self.estimation_id.requisition_till_date + \
                #                                                            self.current_consum_qty
                self.name = self.env['ir.sequence'].next_by_code(
                    'purchase.consumption') or '/'
                self.flag_consumption = 1

            else:
                self.flag_consumption = 0
                raise Warning(
                    _('Sorry you cannot approve consumption greater then available quantity !'))
            # if self.product_location_id:
            #     location_ids = self.env['stock.quant'].search(
            #         [('product_id.id', '=', self.material_id.id), ('location_id', '=', self.product_location_id.id)])
            #     # location_ids.reserved_quantity=0
            #     # reserved_quantity=location_ids.reserved_quantity
            #     location_ids.reserved_quantity = location_ids.reserved_quantity-(self.current_consum_qty)
            #     location_ids.quantity=location_ids.quantity-self.current_consum_qty

            view_id = self.env.ref(
                'pragtech_purchase.approval_wizard_form_view_purchase').id
            return {

                'type': 'ir.actions.act_window',
                'key2': 'client_action_multi',
                'res_model': "approval.wizard",
                'multi': "True",
                'target': 'new',
                'views': [[view_id, 'form']],
            }


class PurchaseConsumptionLine(models.Model):
    _name = 'purchase.consumption.line'
    material_id = fields.Many2one('product.product', 'Material')
    unit = fields.Many2one('uom.uom', 'Unit', required=True)
    rate = fields.Float('Rate')
    quantity = fields.Integer('Quantity')
    total_ordered_qty = fields.Float('Ordered Qty', readonly=True)
    balance_qty = fields.Float('Balance Qty', compute='get_balanced_qty')
    consumption_as_on_date = fields.Float('Consumption as on date')
    current_consum_qty = fields.Float('Current consumption Qty')
    order_id = fields.Many2one(
        'purchase.consumption', 'consumption_ids')

    @api.depends('current_consum_qty', 'total_ordered_qty')
    def get_balanced_qty(self):
        self.balance_qty = self.order_id.current_consum_qty - \
            self.order_id.total_ordered_qty
        self.current_consum_qty = self.order_id.current_consum_qty
        self.total_ordered_qty = self.order_id.total_ordered_qty
