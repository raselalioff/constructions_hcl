from datetime import datetime, timedelta
import time
from odoo.tools.float_utils import float_is_zero, float_compare
import odoo.addons.decimal_precision as dp
from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError
import threading
from odoo.exceptions import Warning
from odoo.tools.translate import _
from odoo.exceptions import except_orm, Warning, RedirectWarning
from datetime import datetime


class WizardWOSummary(models.TransientModel):
    _name = 'wizard.wo.summary'
    _description = 'WO Summary'

    project_id = fields.Many2one('project.project', 'Project')
    sub_project = fields.Many2one('sub.project', 'Sub Project')
    workorder_id = fields.Many2one('work.order', 'WorkOrder')
    project_wbs = fields.Many2one('project.task', 'Project WBS', domain=[
                                  ('is_wbs', '=', True), ('is_task', '=', False)])
    from_date = fields.Date('From Date')
    to_date = fields.Date('To Date')
    order_line = fields.One2many(
        'wizard.wo.summary.lines', 'order_id', string='Order Lines', copy=True, ondelete='cascade')

    partner_id = fields.Many2one('res.partner', string='Contractor')
    stage_id = fields.Many2one('stage.master', 'Stage')

    @api.onchange('project_id')
    def on_change_project(self):
        if self.project_id:
            return {'domain': {'sub_project': [('project_id', '=', self.project_id.id)],
                               'project_wbs': [('project_id', '=', self.project_id.id), ('is_wbs', '=', True), ('is_task', '=', False), ('is_group', '=', False)],
                               'workorder_id': [('project_id', '=', self.project_id.id)], }}

    @api.onchange('sub_project')
    def on_change_subproject(self):
        if self.sub_project:
            return {'domain': {'project_wbs': [('sub_project', '=', self.sub_project.id), ('is_wbs', '=', True), ('is_task', '=', False), ('is_group', '=', False)],
                               'workorder_id': [('sub_project', '=', self.sub_project.id)], }}

    @api.onchange('project_wbs')
    def on_change_projectwbs(self):
        if self.project_wbs:
            return {'domain': {'workorder_id': [('project_wbs', '=', self.project_wbs.id)], }}

    def compute_workorders(self):
        self.order_line.unlink()
        domain = []
        if self.from_date > self.to_date:
            raise Warning("From Date should be lesser than To Date")

        if self.project_id:
            domain.append(('project_id', '=', self.project_id.id))
        if self.sub_project:
            domain.append(('sub_project', '=', self.sub_project.id))
        if self.project_wbs:
            domain.append(('project_wbs', '=', self.project_wbs.id))
        if self.workorder_id:
            domain.append(('id', '=', self.workorder_id.id))
        if self.from_date:
            domain.append(('date_order', '>=', self.from_date))
        if self.to_date:
            domain.append(('date_order', '<=', self.to_date))
        if self.stage_id:
            domain.append(('stage_id', '=', self.stage_id.id))
        if self.partner_id:
            domain.append(('partner_id', '=', self.partner_id.id))
        wo_obj = self.env['work.order'].search(domain)
        vals = {}
        for wo in wo_obj:
            for lines in wo.order_line:
                vals = {

                    'name': wo.id,
                    'date_order': wo.date_order,
                    'partner_id': wo.partner_id.id,
                    'project_id': wo.project_id.id,
                    'sub_project': wo.sub_project.id,
                    'project_wbs': wo.project_wbs.id,
                    'stage_id': wo.stage_id.id,
                    'untaxed_amount': wo.amount_untaxed,
                    'taxes': wo.amount_tax,
                    'total': wo.amount_total,
                    'order_id': self.id,

                }
            value = self.order_line.create(vals)
        view_id = self.env.ref(
            'pragtech_contracting.workorder_summary_wizard_form_view').id
        return {
            'context': self.env.context,
            # 'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'wizard.wo.summary',
            'res_id': self.id,
            'view_id': view_id,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    def check_condition(self, val1, val2):
        return val1 == val2


class WizardWOSummaryLines(models.TransientModel):
    _name = 'wizard.wo.summary.lines'
    _description = 'WO Summary Lines'

    name = fields.Many2one('work.order', 'WorkOrder')
    project_id = fields.Many2one('project.project', 'Project')
    sub_project = fields.Many2one('sub.project', 'Sub Project')
    workorder_id = fields.Many2one('work.order', 'WorkOrder')
#    work_order_line_detail =  fields.Char('order line detail')
    project_wbs = fields.Many2one('project.task', 'Project WBS', domain=[
                                  ('is_wbs', '=', True), ('is_task', '=', False)])
    order_id = fields.Many2one('wizard.wo.summary', string='Order Reference', ondelete='cascade')
    date_order = fields.Datetime('Order Date')
    partner_id = fields.Many2one('res.partner', string='Contractor')
#    labour_id = fields.Many2one('labour.master', 'Labour')
#    quantity = fields.Integer('Estimated Quantity')
#    rate = fields.Float('Rate')
#    discount = fields.Float(
#        string='Discount (%)', digits=dp.get_precision('Discount'), default=0.0)
#    task_id = fields.Many2one('project.task', 'Task')
    subtotal = fields.Integer('Subtotal')
    total = fields.Integer('Total')
    untaxed_amount = fields.Integer('Untaxed Amount')
    taxes = fields.Integer('Taxes')
#    requisition_qty = fields.Integer('Requisition Quantity')
#    category_id = fields.Many2one('labour.category', 'Category')
#    state = fields.Selection([
#        ('draft', 'Draft'),
#        ('confirm', 'Confirm')])
    stage_id = fields.Many2one('stage.master', 'Stage')


#    task_category = fields.Many2one(
#        'task.category', 'Task Category', related='task_id.category_id')
