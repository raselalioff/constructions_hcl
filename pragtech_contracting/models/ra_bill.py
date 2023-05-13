from odoo.exceptions import Warning
from odoo.tools.translate import _
from odoo import api, fields, models, _
from datetime import datetime
import time


class AccountInvoiceTax(models.Model):

    # account.invoice.tax to account.tax
    _inherit = "account.tax"
    rabill_id = fields.Many2one('ra.bill', 'Bill')


class RABill(models.Model):
    _name = 'ra.bill'
    _description = 'RA Bill'

    @api.model
    def _default_stage(self):
        st_id = self.env['stage.master'].search([('draft', '=', True)])
        if st_id:
            return st_id.id

    name = fields.Char('Bill No.')
    stage_id = fields.Many2one(
        'stage.master', 'Stage', default=_default_stage, readonly=True)
    task_id = fields.Many2one('project.task', 'Task')
    remark = fields.Char('Remark')
    project_id = fields.Many2one(
        'project.project', string='Project', required=True)
    sub_project = fields.Many2one(
        'sub.project', string='Sub Project', required=True)
    project_wbs = fields.Many2one('project.task', string='Project Wbs')
    workorder_id = fields.Many2one('work.order', 'Work Order', required=True)
    workorder_line_id = fields.Many2one('work.order.line', 'WO Detail No')
    contractor_id = fields.Many2one('res.partner', 'Contractor')
    wo_line_id = fields.Integer('WO Detail No.')
    work_completion_sequence = fields.Many2one(
        'work.completion', 'Completion No')
    work_completion_line_sequence = fields.Integer('Completion Detail No')
    labour_id = fields.Many2one('labour.master', string='Labour')
    labour_uom = fields.Many2one('uom.uom', string='Unit of Measure')
    quantity = fields.Integer('Quantity')
    rate = fields.Float('Rate')
    group_id = fields.Many2one(
        'project.task', related='task_id.parent_task_id', store=True, string='Group')
    category_id = fields.Many2one('task.category')
    currency_id = fields.Many2one('res.currency', 'Currency')
    completion_percent = fields.Float('Completion %')
    amount_paid = fields.Float('Amount')
    state = fields.Selection(
        [('draft', 'Draft'), ('paid', 'Billed')], default='draft')

    rabill_line_ids = fields.One2many('ra.bill.line', 'rabill_id')
    advance_recovery_ids = fields.One2many('advance.recovery.line', 'bill_id')
    debit_note_ids = fields.One2many('debit.recovery.line', 'bill_id')
    credit_note_ids = fields.One2many('credit.recovery.line', 'bill_id')

    total_advance_recovery_amt = fields.Float(
        'Total Adv recovery',  store=True)
    total_debit_recovery_amt = fields.Float(
        'Total Debit Recovery',  store=True)
    total_credit_amt = fields.Float(
        'Total Credit',  store=True)

    total_advance_recovery_amt_for_current_wo = fields.Float(
        'advance recovery of wo',  store=True, help='advance recovery amount for current wo')
    total_debit_recovery_amt_for_current_wo = fields.Float(
        'debit recovery of wo',  store=True, help='debit recovery amount for current wo')
    total_credit_recovery_amt_for_current_wo = fields.Float(
        'credit recovery of wo',  store=True, help='credit recovery amount for current wo')

    total_payable_amt = fields.Float(
        'Basic Amt', help='This is total payable excluding debit,credit,advance',  store=True)
    final_total_payable = fields.Float(
        'Total Payable', help='This is total payable incuding debit,credit,advance', compute='get_total_payable_amt', store=True)
    wo_total_amt = fields.Float(
        'Work Order Amt', compute='get_wo_total_amt', store=True)
    wo_balance_advance = fields.Float(
        'WO Balance Advance', compute='get_balance', help='Balance advance amount', store=True)
    wo_balance_debit = fields.Float(
        'WO Balance Debit', compute='get_balance', help='Balance debit amount', store=True)
    till_date_billed = fields.Float(
        'Till Date Billed', compute='get_till_date_billed', store=True)
    balanced_amt = fields.Float(
        'Balanced Amount', compute='get_balanced_amt', store=True)

    pan_no = fields.Char('PAN NO', compute='get_wo_total_amt')
    service_tax_no = fields.Integer(
        'Service tax No.', compute='get_wo_total_amt', store=True)
    contact_person_id = fields.Many2one(
        'res.partner', 'Contact Person', compute='get_wo_total_amt')
    mobile = fields.Char(compute='get_wo_total_amt')
    retention_percent = fields.Integer(
        'Retention(%)', compute='get_wo_total_amt', store=True)
    retention_amount = fields.Float('Retention', help="Retention amount of workorder=(retn *100)/untaxed amt", compute='get_wo_retension_amt')

    # account.invoice.tax to account.tax
    tax_line_ids = fields.One2many('account.tax', 'rabill_id', string='Tax Lines', oldname='tax_line',
                                   readonly=True, states={'draft': [('readonly', False)]}, copy=True)

    mesge_ids = fields.One2many(
        'mail.messages', 'res_id', string='Massage', domain=lambda self: [('model', '=', self._name)])

    # invoice to move===============
    account_invoice_id = fields.Many2one('account.move', 'Invoice')
    counter = 0
    hold_retention = fields.Boolean('Hold Retention?')
    retention_held_in_any_bill = fields.Boolean('Retention held?', store=True)

    @api.depends('workorder_id')
    def if_retention_held_in_any_bill(self):
        self.retention_held_in_any_bill = self.workorder_id.retention_held_in_any_bill
        return self.workorder_id.retention_held_in_any_bill

    @api.depends('workorder_id')
    def get_balance(self):
        transaction = self.env['transaction.transaction'].search(
            [('work_order_id', '=', self.workorder_id.id), ('flag', '=', True)])
        debit_balance = 0
        advance_balance = 0
        for line in transaction:
            if line.transaction_type == 'debit_note':
                debit_balance = debit_balance + line.balance_amount
            if line.transaction_type == 'advance':
                advance_balance = advance_balance + line.balance_amount
        self.wo_balance_advance = advance_balance
        self.wo_balance_debit = debit_balance

    @api.depends('hold_retention', 'workorder_id', 'rabill_line_ids', 'advance_recovery_ids.this_bill_recovery', 'debit_note_ids.this_bill_recovery', 'credit_note_ids.this_bill_recovery')
    def get_wo_retension_amt(self):
        retention_to_hold = 0
        wo_obj = self.env['work.order'].browse(self.workorder_id.id)
        if wo_obj.retention:
            total_retention_amount = (wo_obj.retention * wo_obj.amount_untaxed) / 100
            retention_to_hold = (total_retention_amount / self.workorder_id.amount_untaxed) * self.total_payable_amt
            print("retention_to_hold,total_retention_amount---------------------------", retention_to_hold, total_retention_amount)
#             if self.hold_retention and not self.retention_held_in_any_bill:
            self.retention_amount = retention_to_hold
#             else:
#                 print("setting some zerpppp")
#                 self.retention_amount = 0.0

    @api.depends('workorder_id')
    def get_wo_total_amt(self):
        for this in self:
            wo_obj = self.env['work.order'].browse(this.workorder_id.id)
            this.wo_total_amt = wo_obj.amount_total
            this.service_tax_no = wo_obj.partner_id.service_tax_no
            this.pan_no = wo_obj.partner_id.pan_no
            this.retention_percent = wo_obj.retention

            for contact in wo_obj.partner_id.child_ids:
                this.contact_person_id = contact.id
                this.mobile = contact.mobile
            return wo_obj.amount_total

    @api.depends('workorder_id')
    def get_till_date_billed(self):
        self.till_date_billed = self.workorder_id.billed_amount
        return self.workorder_id.billed_amount

    @api.depends('till_date_billed', 'wo_total_amt')
    def get_balanced_amt(self):
        for this in self:
            this.balanced_amt = this.wo_total_amt - this.till_date_billed

#     def payble_amount(self, project_id, subproject_id, project_wbs, workorder_id, task_id,completion_percent):
#         final_payble = 0
#         domain = []
#         if self.project_id:
#             domain.append(('project_id', '=', self.project_id.id))
#         if self.project_wbs:
#             domain.append(('project_wbs', '=', self.project_wbs.id))
#         if self.sub_project:
#             domain.append(('sub_project', '=', self.sub_project.id))
#         if self.workorder_id:
#             domain.append(('id', '=', self.workorder_id.id))
#         workorders = self.env['work.order'].search(domain)
#         for wo in workorders:
#             for wo_line in wo.order_line:
#                 for payment in wo_line.payment_schedule_line_ids:
#                     if payment.task_id.id == task_id:
#                         """Get percentage task(work) completed"""
#                         if completion_percent <= payment.amount_to_release:
#                             percentage_completion=(completion_percent/payment.amount_to_release)*100
#                             final_payble=(percentage_completion/100)*wo_line.price_total
#                         else:
#                             final_payble=wo_line.price_total
#         return final_payble
    @api.depends('rabill_line_ids', 'advance_recovery_ids.this_bill_recovery',
                 'debit_note_ids.this_bill_recovery', 'credit_note_ids.this_bill_recovery', 'hold_retention')
    def get_total_payable_amt(self):
        total = 0
        for this in self:
            for line in this.rabill_line_ids:
                total += line.this_bill_amount
            this.total_payable_amt = total

        adv_rec_total = 0
        adv_rec_for_wo = 0
        for this in self:
            for line in this.advance_recovery_ids:
                adv_rec_total += line.this_bill_recovery
                if line.advance_id.work_order_id == self.workorder_id:
                    adv_rec_for_wo += line.this_bill_recovery
            this.total_advance_recovery_amt = adv_rec_total
            this.total_advance_recovery_amt_for_current_wo = adv_rec_for_wo

        debit_rec_total = 0
        debit_rec_for_wo = 0
        for this in self:
            for line in this.debit_note_ids:
                debit_rec_total += line.this_bill_recovery
                if line.debit_id.work_order_id == self.workorder_id:
                    debit_rec_for_wo += line.this_bill_recovery
            this.total_debit_recovery_amt = debit_rec_total
            this.total_debit_recovery_amt_for_current_wo = debit_rec_for_wo

        total_credit = 0
        credit_rec_for_wo = 0
        for this in self:
            for line in this.credit_note_ids:
                total_credit += line.this_bill_recovery
                if line.credit_id.work_order_id == self.workorder_id:
                    credit_rec_for_wo += line.this_bill_recovery
            this.total_credit_amt = total_credit
            this.total_credit_recovery_amt_for_current_wo = credit_rec_for_wo

#             if self.hold_retention and not self.retention_held_in_any_bill:
            this.final_total_payable = total - this.retention_amount - \
                adv_rec_total - debit_rec_total + total_credit

#             else:
#                 this.final_total_payable = total - \
#                     adv_rec_total - debit_rec_total + total_credit

    def get_advance_recovery(self, partner, wizard_id, workorder):
        lst = []
        dict = {}
        st_id = self.env['stage.master'].search([('approved', '=', True)])
        trascations = self.env['transaction.transaction'].search(
            [('transaction_type', '=', 'advance'), ('project_id', '=', self.project_id.id), ('stage_id', '=', st_id.id)])
        recovered_till_date = 0
        for line in trascations:
            bill_list = []
            rec_list = []
            if line.balance_amount > 0:
                dict = {'advance_amount': line.amount,
                        'recovered_till_date': line.recovered_till_date,
                        'balance_amount': line.balance_amount,
                        'ra_bill_wizard_id': wizard_id,
                        'advance_id': line.id,

                        }
                rec_obj = self.env['advance.recovery.line'].search(
                    [('advance_id', '=', line.id)])
                for rec_line in rec_obj:
                    if rec_line.bill_id.stage_id == st_id:
                        bill_list.append(rec_line.bill_id.id)
                    if rec_line.advance_recovery_line_id.stage_id == st_id:
                        rec_list.append(rec_line.advance_recovery_line_id.id)
                dict.update(
                    {'bill_ids': [(6, 0, bill_list)], 'adv_recoveries': [(6, 0, rec_list)]})
                lst.append(dict)
        return lst

    def get_credit_note(self, partner, wizard_id, workorder):
        dict = {}
        lst = []
        st_id = self.env['stage.master'].search([('approved', '=', True)])
        trascations = self.env['transaction.transaction'].search(
            [('transaction_type', '=', 'credit_note'), ('project_id', '=', self.project_id.id), ('stage_id', '=', st_id.id)])
        recovered_till_date = 0
        for line in trascations:
            if line.balance_amount > 0:
                dict = {'credit_note_amount': line.amount,
                        'credit_id': line.id,
                        'recovered_till_date': line.recovered_till_date,
                        'balance_amount': line.balance_amount,
                        'ra_bill_wizard_id': wizard_id,
                        }
                lst.append(dict)
        return lst

    def get_debit_note(self, partner, wizard_id, workorder):
        lst = []
        dict = {}
        st_id = self.env['stage.master'].search([('approved', '=', True)])
        trascations = self.env['transaction.transaction'].search(
            [('transaction_type', '=', 'debit_note'), ('project_id', '=', self.project_id.id), ('stage_id', '=', st_id.id)])
        for line in trascations:
            if line.balance_amount > 0:
                dict = {'debit_note_amount': line.amount,
                        'recovered_till_date': line.recovered_till_date,
                        'balance_amount': line.balance_amount,
                        'wizard_id': wizard_id,
                        'debit_id': line.id
                        }
                lst.append(dict)
        return lst

    #     def payble_amount(self, workorder_id,wo_line, task_id,total_completion_percent,line_completion_percent):
#         for wo_line in self.workorder_id.order_line:
#             for payment in wo_line.payment_schedule_line_ids:
#                 if payment.task_id.id == task_id:
#                     """Get percentage of task(work) completed"""
#                     if line_completion_percent <= payment.amount_to_release:
#                         #print "in if completion less = than ps"
#                         percentage_completion=(line_completion_percent/payment.amount_to_release)*100
#                         #print "percentage_completion------------------",percentage_completion
#                         final_payble=(percentage_completion/100)*wo_line.price_total
#                     else:
#                         #print "in else completion greater than ps"
#                         final_payble=wo_line.price_total
#         return final_payble

    def payble_amount(self, workorder_id, wo_line, task_id, total_completion_percent, line_completion_percent, wo_line_basic_amt):
        # print
        # "wo_line,task_id,total_completion_percent,line_completion_percent-------",wo_line,task_id,total_completion_percent,line_completion_percent
        final_payble = 0
        try:
            final_payble = (line_completion_percent / 100) * wo_line_basic_amt
        except:
            pass


#         for payment in wo_line.payment_schedule_line_ids:
#             if payment.task_id.id == task_id:
#                 """Get percentage of task(work) completed"""
#                 if total_completion_percent == 100:
#                     final_payble = (payment.amount_to_release / 100) * wo_line.price_total
#                 else:
#                     amt_on_full_completion = (payment.amount_to_release / 100) * wo_line.price_total
#                     final_payble = amt_on_full_completion * \
#                         (line_completion_percent / 100)
        return final_payble

    def get_ra_bill_lines(self, workorder):
        lst = []
        wo_sum = 0
        amt_to_release_percent = 0
        st_id = self.env['stage.master'].search([('approved', '=', True)])
        for wo_line in workorder.order_line:
            for task_line in wo_line.payment_schedule_line_ids:
                # print
                # "task_id------------------------------",task_line.task_id.id,self.workorder_id.id,self.workorder_line_id
                compl_obj = self.env['work.completion'].search([('task_id', '=', task_line.task_id.id), (
                    'total_percent', '>', 0), ('workorder_id', '=', self.workorder_id.id), ('workorder_line_id', '=', wo_line.id)])
#                 compl_obj = self.env['work.completion'].search([('task_id', '=', task_line.task_id.id), ('total_percent', '>', 0)])
                for completed_task in compl_obj:
                    for line in completed_task.order_line:
                        if not line.bill and line.stage_id == st_id:

                            taxes = wo_line.work_tax
                            invoice_line_tax_ids = workorder.fiscal_position_id.map_tax(
                                taxes)
                            tax_list = []
                            for tax_id in invoice_line_tax_ids:
                                tax_list.append(tax_id.id)

                            """"completion_percent calculation added recently"""
                            try:
                                amt_to_release_percent = (completed_task.amt_to_release / 100) * line.completion_percent
                            except:
                                pass

                            payble_amt = self.payble_amount(completed_task.workorder_id.id, wo_line, completed_task.task_id.id,
                                                            completed_task.total_percent, amt_to_release_percent, wo_line.basic_amount)
                            vals = {'work_completion_sequence': completed_task.id,
                                    'work_completion_line_sequence': line.sequence,
                                    'workorder_line_id': wo_line.id,
                                    'this_bill_amount': payble_amt,
                                    'retention': wo_line.retention,
                                    'completion_percent': line.completion_percent,
                                    'completed_qty': line.completion_qty, 'estimated_qty': completed_task.estimated_qty,
                                    'project_id': completed_task.project_id.id,
                                    'sub_project': completed_task.sub_project.id,
                                    'project_wbs': completed_task.project_wbs.id,
                                    'workorder_id': completed_task.workorder_id.id,
                                    'basic_amount': wo_line.basic_amount, 'taxed_amount': wo_line.price_tax,
                                    'contractor_id': completed_task.workorder_id.partner_id.id,
                                    'labour_id': wo_line.labour_id.id, 'task_id': completed_task.task_id.id,
                                    'tax_ids': invoice_line_tax_ids.ids,
                                    'amt_to_release': completed_task.amt_to_release,
                                    }
                            wo_sum = wo_sum + payble_amt
                            lst.append(vals)
        return lst, wo_sum

    def compute_data(self):
        self.name = self.env['ir.sequence'].next_by_code('ra.bill.code') or '/'

        self.get_wo_retension_amt()
        ra_bill_lines, wo_sum = self.get_ra_bill_lines(self.workorder_id)
        self.total_payable_amt = wo_sum
        advance = self.get_advance_recovery(
            self.workorder_id.partner_id, self.id, self.workorder_id.id)
        credit_note = self.get_credit_note(
            self.workorder_id.partner_id, self.id, self.workorder_id.id)
        debit_note = self.get_debit_note(
            self.workorder_id.partner_id, self.id, self.workorder_id.id)

        if not self.rabill_line_ids:
            self.rabill_line_ids = ra_bill_lines
        if not self.debit_note_ids:
            self.debit_note_ids = debit_note
        if not self.credit_note_ids:
            self.credit_note_ids = credit_note
        if not self.advance_recovery_ids:
            self.advance_recovery_ids = advance

    def get_taxes_values(self):
        tax_grouped = {}
        for line in self.rabill_line_ids:
            wo_line = self.env['work.order.line'].search(
                [('order_id', '=', line.workorder_id.id), ('wo_line_no', '=', line.workorder_line_id.id)])
            price_unit = wo_line.rate * (1 - (0.0) / 100.0)
            taxes = line.tax_ids.compute_all(
                price_unit, self.currency_id, wo_line.quantity, line.task_id, self.contractor_id)['taxes']
            for tax in taxes:
                val = {
                    'bill_id': self.id,
                    'name': tax['name'],
                    'tax_id': tax['id'],
                    'amount': tax['amount'],
                    'manual': False,
                    'sequence': tax['sequence'],
                    'account_analytic_id': tax['analytic'] and line.account_analytic_id.id or False,
                    'account_id': tax['account_id'],
                    'base_amount': price_unit
                }

                key = tax['id']
                if key not in tax_grouped:
                    tax_grouped[key] = val
                else:
                    tax_grouped[key]['amount'] += val['amount']
        return tax_grouped

    @api.onchange('rabill_line_ids')
    def _onchange_rabill_line_ids(self):
        taxes_grouped = self.get_taxes_values()
        tax_lines = self.tax_line_ids.browse([])
        for tax in taxes_grouped.values():
            tax_lines += tax_lines.new(tax)
        self.tax_line_ids = tax_lines
        return

    @api.model
    def create(self, vals):
        res = super(RABill, self).create(vals)
        res.get_total_payable_amt()
#         Validation

        for adv in self.advance_recovery_ids:
            adv_obj = self.env['transaction.transaction'].browse(
                adv.advance_id.id)
            if(adv.this_bill_recovery <= adv.balance_amount):
                None
#                 adv_obj.recovered_till_date=adv_obj.recovered_till_date+adv.this_bill_recovery
            else:
                raise Warning(
                    _('This Bill recovery cannot be greater then balance amount'))

        for debit in self.debit_note_ids:
            debit_obj = self.env['transaction.transaction'].browse(
                debit.debit_id.id)
            if(debit.this_bill_recovery <= debit.balance_amount):
                None
#                 debit_obj.recovered_till_date=debit_obj.recovered_till_date+debit.this_bill_recovery
            else:
                raise Warning(
                    _('This Bill recovery cannot be greater then balance amount'))

        for credit in self.credit_note_ids:
            credit_obj = self.env['transaction.transaction'].browse(
                credit.credit_id.id)
            if(credit.this_bill_recovery <= credit.balance_amount):
                None
#                 credit_obj.recovered_till_date=credit_obj.recovered_till_date+credit.this_bill_recovery
            else:
                raise Warning(
                    _('This Bill recovery cannot be greater then balance amount'))
        if self.final_total_payable < 0 and self.final_total_payable < (self.wo_balance_advance + self.wo_balance_debit + self.till_date_billed):
            raise Warning(_('Invalid payable amount'))
        st_id = self.env['stage.master'].search([('draft', '=', True)])

        vals = {
            'date': datetime.now(),
            'from_stage': st_id.id,
            'to_stage': st_id.id,
            'remark': 'Created by ' + (self.env['res.users'].browse(self._context.get('uid'))).name,
            'model': 'ra.bill',
            'res_id': res.id,
        }
        re = self.env['mail.messages'].create(vals)

        return res

    def write(self, vals):
        res = super(RABill, self).write(vals)
        for line in self.rabill_line_ids:
            if not line.workorder_id == self.workorder_id:
                line.unlink()

#         Validation
        for adv in self.advance_recovery_ids:
            if(adv.this_bill_recovery <= adv.balance_amount):
                None
            else:
                raise Warning(
                    _('This Bill recovery cannot be greater then balance amount'))

        for debit in self.debit_note_ids:
            if(debit.this_bill_recovery <= debit.balance_amount):
                None
            else:
                raise Warning(
                    _('This Bill recovery cannot be greater then balance amount'))

        for credit in self.credit_note_ids:
            if(credit.this_bill_recovery <= credit.balance_amount):
                None
            else:
                raise Warning(
                    _('This Bill recovery cannot be greater then balance amount'))

        if self.final_total_payable < 0:
            raise Warning(_('Invalid payable amount'))
        return res

    def unlink(self):
        for this in self:
            if this.state == 'paid':
                raise Warning('You cant delete paid Bills')
        return models.Model.unlink(self)

    def change_state(self, context={}):
        if self.retention_percent and self.hold_retention:
            self.workorder_id.retention_held_in_any_bill = True

        if self.final_total_payable < 0:
            raise Warning('There is no invoiceable line.')

        if self.counter == 0:
            self.counter = self.counter + 1
            if context.get('copy') == True:
                self.state = 'paid'

                """ Update till date billed amount in work order"""
                till_billed_for_wo = self.total_payable_amt - self.retention_amount - self.total_advance_recovery_amt_for_current_wo - \
                    self.total_credit_recovery_amt_for_current_wo - \
                    self.total_debit_recovery_amt_for_current_wo
                self.workorder_id.billed_amount = till_billed_for_wo

                """ Update Bill id on completion record"""
                for bill_line in self.rabill_line_ids:
                    completion_line = self.env['work.completion.line'].search(
                        [('order_id', '=', bill_line.work_completion_sequence.id), ('sequence', '=', bill_line.work_completion_line_sequence)])
                    for cmp_line in completion_line:
                        cmp_line.bill = self.id

                for adv in self.advance_recovery_ids:
                    adv_obj = self.env['transaction.transaction'].browse(
                        adv.advance_id.id)
                    if(adv.this_bill_recovery <= adv.balance_amount):
                        adv_obj.recovered_till_date = adv_obj.recovered_till_date + \
                            adv.this_bill_recovery
                    else:
                        raise Warning(
                            _('This Bill recovery cannot be greater then balance amount'))
                    if adv.this_bill_recovery == 0:
                        adv.unlink()

                for debit in self.debit_note_ids:
                    # #print "debit loop-------------------",debit
                    debit_obj = self.env['transaction.transaction'].browse(
                        debit.debit_id.id)
                    if(debit.this_bill_recovery <= debit.balance_amount):
                        recovered = debit_obj.recovered_till_date
                        debit_obj.recovered_till_date = recovered + \
                            debit.this_bill_recovery
                    else:
                        raise Warning(
                            _('This Bill recovery cannot be greater then balance amount'))
                    if debit.this_bill_recovery == 0:
                        debit.unlink()
                for credit in self.credit_note_ids:
                    credit_obj = self.env['transaction.transaction'].browse(
                        credit.credit_id.id)
                    if(credit.this_bill_recovery <= credit.balance_amount):
                        credit_obj.recovered_till_date = credit_obj.recovered_till_date + \
                            credit.this_bill_recovery
                    else:
                        raise Warning(
                            _('This Bill recovery cannot be greater then balance amount'))
                    if credit.this_bill_recovery == 0:
                        credit.unlink()
                """Validation"""
                if self.final_total_payable < 0 and self.final_total_payable < (self.wo_balance_advance + self.wo_balance_debit + self.till_date_billed):
                    raise Warning(_('Invalid payable amount'))

#                 """adds Record in journal for passed RaBill"""
#                 move_lines=[]
#                 a_id=self.env['account.account'].search([('name','=','Cash')],limit=1)
#                 credit_id=self.env['account.account'].search([('name','=','Creditors')],limit=1)
# #                 print a_id,credit_id
#                 for rec in self.rabill_line_ids :
#                     move_lines.append((0,0,{
#                           'partner_id':self.contractor_id.id,
#                           'account_id': a_id.id,
#                           'name': rec.labour_id.name,
#                           'debit':rec.this_bill_amount,
#                           'credit':0.0,
#                           }))
#                 """credit balancing"""
#                 move_lines.append((0,0,{
#                           'partner_id':self.contractor_id.id,
#                           'account_id': credit_id.id,
#                           'name': '/',
#                           'debit':0.0,
#                           'credit':self.total_payable_amt,
#                           }))
#
#                 j_id=self.env['account.journal'].search([('name','=','Cash')],limit=1)
#                 code = self.env['ir.sequence'].next_by_code('journal.name.contractor')
#                 vals1 = {
#                         'name' : code,
#                         'journal_id': j_id.id,
#                         'date': time.strftime("%m/%d/%Y"),
#                         'partner_id':self.contractor_id.id,
#                         'line_ids':move_lines,
#                         'state': 'posted',
#                       }
#                 print ("vals1===============",vals1)
#                 self.env['account.move'].create(vals1)
            """Create vendor bill (in account.invoice) for ra bill"""

            if not self.account_invoice_id:
                self.create_ra_bill_invoice()

            view_id = self.env.ref('pragtech_contracting.approval_wizard_form_view_contracting').id
            return {

                'type': 'ir.actions.act_window',
                'key2': 'client_action_multi',
                'res_model': 'approval.wizard',
                'multi': 'True',
                'target': 'new',
                'views': [[view_id, 'form']],
            }

    def create_ra_bill_invoice(self):
        product_obj = self.env['product.product']

        # invoice to move===============
        invoice_obj = self.env['account.move']

        credit_sum = sum([line.this_bill_recovery for line in self.credit_note_ids])
        recovery_sum = sum([line.this_bill_recovery for line in self.advance_recovery_ids]) + \
            sum([line.this_bill_recovery for line in self.debit_note_ids])

        invoice_obj = invoice_obj.create({'name': 'RA Bill',
                                          'origin': 'RA BILL' + ' ' + str(self.name),
                                          'type': 'in_invoice',
                                          'reference': False,
                                          'account_id': self.workorder_id.partner_id.property_account_receivable_id.id,
                                          'partner_id': self.workorder_id.partner_id.id,
                                          'ra_bill_invoice': True,
                                          'recovery_sum': recovery_sum,
                                          'credit_sum': credit_sum,
                                          'retention_amt': self.retention_amount,
                                          'project_id': self.workorder_id.project_id.id,
                                          'project_wbs_id': self.workorder_id.project_wbs.id
                                          })

        for line in self.rabill_line_ids:
            product_obj = product_obj.search([('name', '=', line.labour_id.name), ('is_labour', '=', True)])
            if not product_obj:
                product_obj = product_obj.create({'name': line.labour_id.name, 'is_labour': True})
            if product_obj.property_account_income_id:
                account_id = product_obj.property_account_income_id.id
            else:
                account_id = product_obj.categ_id.property_account_income_categ_id.id

            invoice_obj.invoice_line_ids.create({
                'name': product_obj.name,
                'origin': 'RA BILL' + ' ' + str(self.name),
                'account_id': account_id,
                'price_unit': line.this_bill_amount,
                'quantity': 1.0,
                'discount': 0.0,
                'uom_id': product_obj.uom_id.id,
                'product_id': product_obj.id,
                'invoice_id': invoice_obj.id,
            })

        self.account_invoice_id = invoice_obj.id
        return invoice_obj

    def view_ra_bill(self):
        view_id = self.env.ref('account.invoice_supplier_form').id,

        # invoice to move===============
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'form',
            # 'view_type': 'form',
            'res_id': self.account_invoice_id.id,
            'views': [(view_id, 'form')],
        }


class RABillLine(models.Model):
    _name = 'ra.bill.line'
    _description = 'RA Bill Line'

    task_id = fields.Many2one('project.task', 'Task')
    remark = fields.Char('Remark')
    rabill_id = fields.Many2one('ra.bill', 'RA Bill')
    is_use = fields.Boolean(' ')
    project_id = fields.Many2one('project.project', string='Project')
    sub_project = fields.Many2one('sub.project', string='Sub Project')
    project_wbs = fields.Many2one('project.task', string='Project Wbs')
    workorder_id = fields.Many2one('work.order', 'Work Order')
    contractor_id = fields.Many2one('res.partner', 'Contractor')
    workorder_line_id = fields.Many2one('work.order.line', 'WO Detail No')
    work_completion_sequence = fields.Many2one(
        'work.completion', 'Completion No')
    work_completion_line_sequence = fields.Integer('Completion Detail No')
    completed_qty = fields.Float('Completed Qty')
    estimated_qty = fields.Float('Estimated Qty')
    basic_amount = fields.Float('Basic Amount')
    taxed_amount = fields.Float('Taxed Amount')

    labour_id = fields.Many2one('labour.master', string='Labour')
    labour_uom = fields.Many2one('uom.uom', string='Unit of Measure')
    quantity = fields.Integer('Quantity')
    rate = fields.Float('Rate')
    group_id = fields.Many2one(
        'project.task', related='task_id.parent_task_id', store=True, string='Group')
#     category_id = fields.Many2one('task.category')
    category_id = fields.Many2one('task.category', related='task_id.category_id', store=True, string='Task Category')
    is_use = fields.Boolean(' ')
    completion_percent = fields.Float('Completion %')
    this_bill_amount = fields.Float('This Bill Amount')

    retention = fields.Float('Retention')
    bill_ids = fields.Many2many('ra.bill')
    tax_ids = fields.Many2many('account.tax', 'bill_line_tax', 'bill_id', 'tax_id', string='Taxes', domain=[
                               ('type_tax_use', '!=', 'none'), '|', ('active', '=', False), ('active', '=', True)])
    amt_to_release = fields.Float(string='Amount to release',
                                  help='This is amount to release after completion of task which is specified in payment schedule.')


class CreditNote(models.Model):
    _name = 'credit.note'
    name = fields.Char(' ')
    amount = fields.Float('Credited Amount')
    recovered_till_date = fields.Float('Adjusted Till Date')
    balance_amount = fields.Float('Balance Amount')
    bill_id = fields.Many2one('ra.bill', 'Bill')
    is_use = fields.Boolean(' ')


class accountInvoiceTax(models.Model):

    # account.invoice.tax to account.tax
    _inherit = 'account.tax'
    _description = 'Account Invoice Tax'

    base_amount = fields.Float('Base amount')
