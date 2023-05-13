# -*- coding: utf-8 -*-
# Part of Browseinfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
import datetime



class Expenss_advance(models.Model) :
    _name = "advance.expense"


    name = fields.Char('Name',readonly=True)
    employee_id = fields.Many2one('hr.employee',string="Employee" ,required=True)
    department_id = fields.Many2one('hr.department',string="Department")
    req_date = fields.Date(string="Request Date")
    req_user_id = fields.Many2one('res.users',string="Requested User", default = lambda self : self.env.user.id) 
    req_amount = fields.Monetary(string="Requested Amount",compute="_compute_req_amount")
    currency_id = fields.Many2one('res.currency',string="Currency",default = lambda self : self.env.user.company_id.currency_id.id,readonly=True)

    job_id = fields.Many2one('hr.job',string="Job Position",required=True)
    confirm_by =  fields.Many2one('res.users',string="Confirmed By")
    confirm_date = fields.Date(string="Confirm Date")
    approve_by =  fields.Many2one('res.users',string="Approved By")
    approve_date = fields.Date(string="Approved Date")
    paid_by = fields.Many2one('res.users',string="Paid By")
    paid_date = fields.Date(string="Paid Date")
    expense_ids = fields.One2many('hr.expense','advance_expence_id',string="Expenses")

    state = fields.Selection([('draft','Draft'),('confirmed','Confirmed'),('approve','Approved'),('paid','Paid'),('done','Done')],string="state",default="draft")


    partner_id = fields.Many2one('res.partner',string='Employee Account')
    payment_method_id = fields.Many2one('account.journal',string="Payment Method")
    employee_account_id = fields.Many2one('account.account',string="Asset Account")
    account_move_id = fields.Many2one('account.move',string="Journal",readonly=True)
    paid_ammount = fields.Float('Paid Amount')

    reason = fields.Text()
    comment = fields.Text()

    @api.onchange('employee_id')
    def onchange_employee(self):
        self.department_id = self.employee_id.department_id.id
        self.job_id = self.employee_id.job_id

        return


    def action_jounral(self):
        return {
            'name': 'Journal',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'context': {},
            'res_model': 'account.move',
            'domain': [('id','=',self.account_move_id.id)],   
        }


    def action_pay(self):
        res = self.env['account.move']


        debit_line = [0,0,{'account_id' : self.employee_account_id.id,
                            'partner_id' : self.partner_id.id,
                            'name' : self.name,
                            'debit' : self.req_amount,
                            'credit' : 0.0
                            }]


        credit_line = [0,0,{'account_id' : self.payment_method_id.default_account_id.id,
                            'partner_id' : self.partner_id.id,
                            'name' : self.name,
                            'debit' : 0.0,
                            'credit' : self.req_amount
                            }]

        move_line = [debit_line,credit_line]

        jounral = res.create({'date': fields.datetime.now(),
                    'journal_id' :self.payment_method_id.id,
                    'ref' : self.name ,
                    'line_ids' : move_line})


        
        self.write({'state':'paid','account_move_id':jounral.id,'paid_by': self.env.user.id,'paid_date':fields.datetime.now(),'paid_ammount':self.req_amount})


        

    @api.depends('expense_ids.total_amount')
    def _compute_req_amount(self):
        for sheet in self:
            sheet.req_amount = sum(sheet.expense_ids.mapped('total_amount'))

            
    @api.model
    def create(self, vals):

        seq = self.env['ir.sequence'].next_by_code('advance.expense') or '/'
        vals['name'] = seq
        vals['req_date'] = fields.datetime.now()
        if vals.get('req_user_id'):
            vals['req_user_id'] = vals.get('req_user_id')
        else:
            vals['req_user_id'] = self.env.user.id
        return super(Expenss_advance, self).create(vals)

    def action_confirm(self):
        self.write({'state':'confirmed','confirm_by':self.env.user.id,'confirm_date' : fields.datetime.now()})

    def action_approve(self):
        self.write({'state':'approve','approve_by':self.env.user.id,'approve_date' : fields.datetime.now()})

    def action_done(self):
        self.write({'state':'done'})


class HrExpense(models.Model):

    _inherit = "hr.expense"

    advance_expence_id = fields.Many2one('advance.expense')
    expence_advance_id = fields.Many2one('advance.expense',string = "Advance Expences",domain=[('state','=','done')])
    advance_amount = fields.Monetary('Advance Amount')


    @api.onchange('expence_advance_id')
    def onchange_employee(self):
        self.advance_amount = self.expence_advance_id.paid_ammount  
        

        return
    

