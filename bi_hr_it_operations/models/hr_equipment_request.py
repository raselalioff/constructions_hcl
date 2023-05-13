# -*- coding: utf-8 -*-
# Part of Browseinfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError

import datetime

class my_equipment_request(models.Model):
	_name = "my.equipment.request"
	_inherit = ['mail.thread', 'mail.activity.mixin']

	request_for = fields.Selection([('hardware','Hardware'),('software','Software')],string="Request For",required=True)
	employee_id = fields.Many2one('hr.employee',string="Employee" ,required=True)
	job_id = fields.Many2one('hr.job',string="Job Position",required=True)
	user_id = fields.Many2one('res.users',string="User", tracking=True, default=lambda self: self.env.user)
	department_id = fields.Many2one('hr.department',string="Department")
	damage = fields.Boolean(string="Damage")
	cpmpany_id = fields.Many2one('res.company',string="Company",default=lambda self: self.env.user.company_id)
	request_equipment_ids = fields.One2many('equipment.request','equipment_id',string="Request Equipments")
	description = fields.Text()
	damage_details_ids = fields.One2many('damage.details','equipment_id',string="Damage Details")
	expense_ids = fields.One2many('hr.expense','equipment_id',string="Expenses",readonly=True)
	state = fields.Selection([('draft','Draft'),('waiting_approve','Waitng For Approval'),('dept_approve','Approved By Department')
			,('hr_approve','Approved By HR'),('assigned','Equipment Assigned'),('refused','Refused'),('reject','Rejected')],default="draft", tracking=True)
	expense_created = fields.Boolean('Expense Created',)
	picking_ids = fields.One2many('stock.picking','equipment_id',string="Internal Transfar",readonly=True)

	create_date = fields.Datetime(string="Create Date")
	modified_date = fields.Datetime(string="Modified Date")
	validate_date = fields.Datetime(string="Validate Date")
	approved_date = fields.Datetime(string="Approved Date")

	rejected_date = fields.Datetime(string="Rejected Date")
	refused_date = fields.Datetime(string="Refused Date")

	create_by_id = fields.Many2one('res.users',string = "Created By")
	modified_by_id = fields.Many2one('res.users',string = "Modified By")
	validate_by_id = fields.Many2one('res.users',string = "Validate By")
	approved_by_id = fields.Many2one('res.users',string = "Approved By")
	location_id = fields.Many2one('stock.location',string="Source Location")

	rejected_by_id = fields.Many2one('res.users',string = "Rejected By")
	refused_by_id = fields.Many2one('res.users',string = "Refused By")

	@api.onchange('damage_details_ids')
	def onchange_damage_details_ids(self):
		if len(self.damage_details_ids) > 0:
			if len(self.expense_ids) != len(self.damage_details_ids):
				self.expense_created = False
			if not len(self.expense_ids) != len(self.damage_details_ids):
				self.expense_created = True


	def write(self, vals):
		total = 0
		for e_id in self.expense_ids:
			total += e_id.total_amount
		if total > 0 and self.env.context.get('is_damage_ids'):
			msg = "expense created of total amount is " + str(total)
			self.message_post(body=msg)
		return super(my_equipment_request, self).write(vals)

	@api.onchange('employee_id')
	def onchange_employee(self):
		self.department_id = self.employee_id.department_id.id
		self.job_id = self.employee_id.job_id


	@api.depends('employee_id','request_for')
	def name_get(self):
		result=[]
		for line in self:	
			name =line.employee_id.name + '-' + line.request_for + '-' + str(self.create_date.date())	
			result.append((line.id,name))
		return result

	def action_confirm(self):
		self.write({'state':'waiting_approve',
			'create_date':fields.datetime.now(),
			'create_by_id': self.env.user.id})
		return

	def action_set_to_draft(self):
		for rec in self.expense_ids:
			rec.state = 'draft'
		self.write({'state': 'draft'})
		return

	def action_refused(self):
		for rec in self.expense_ids:
			rec.state = 'refused'
		self.write({'state':'refused','refused_date':fields.datetime.now(),
			'refused_by_id': self.env.user.id})
		return

	def action_reject(self):
		self.write({'state':'reject','rejected_date':fields.datetime.now(),
			'rejected_by_id': self.env.user.id})
		return

	def action_approve_dept(self):
		self.write({'state':'dept_approve','validate_date':fields.datetime.now(),
			'validate_by_id': self.env.user.id})
		return

	def action_approve_hr(self):
		self.write({'state':'hr_approve','modified_date':fields.datetime.now(),
			'modified_by_id': self.env.user.id})
		return

	def create_internal_transfer(self):
		picking_obj = self.env['stock.picking']

		type_obj = self.env['stock.picking.type']
		company_id = self.env.context.get('company_id') or self.env.user.company_id.id
		types = type_obj.search([('code', '=', 'incoming'), ('warehouse_id.company_id', '=', company_id)],limit=1)
		vals =[]
		for line in self.request_equipment_ids :
			vals.append([0,0,{'product_id':line.product_id.id,
							'name':line.product_id.name,
							'product_uom_qty' : line.product_qty,
							'product_uom': line.product_unit.id,
							'location_dest_id': types.default_location_dest_id.id,
								'location_id':self.location_id.id}])
		
		stock = picking_obj.create({'picking_type_id':types.id,'location_id':self.location_id.id,
			'location_dest_id' : types.default_location_dest_id.id,
			'move_ids_without_package': vals
			})
		self.picking_ids = [[6,0,[stock.id]]]
		self.write({'state':'assigned','approved_date':fields.datetime.now(),
			'approved_by_id': self.env.user.id})
		return

	def action_view_expenses(self):
		return {
			'name': 'Expenses',
			'type': 'ir.actions.act_window',
			'view_type': 'form',
			'view_mode': 'tree,form',
			'context': {},
			'res_model': 'hr.expense',
			'domain': [('id','in',self.expense_ids.ids)],	
		}

	def action_view_picking(self):
		return {
			'name': 'Transfer',
			'type': 'ir.actions.act_window',
			'view_type': 'form',
			'view_mode': 'tree,form',
			'context': {},
			'res_model': 'stock.picking',
			'domain': [('id','in',self.picking_ids.ids)],	
		}

	def action_expence(self):
		val = []
		for line in self.damage_details_ids :
			if not line.expense_line_created:
				line.expense_line_created = True
				val.append([0,0,{'name' : self.request_for,
								 'product_id' : line.product_id.id,
								 'unit_amount' :line.unit_price,
								 'quantity':line.product_qty,
								 'product_uom_id':line.product_id.uom_id.id,
								 'employee_id':self.employee_id.id}])
		if val:
			self.expense_ids = val
			self.write({'expense_created' : True})
		else:
			raise UserError('Expense Line Are Empty OR All Expense Are Created.')
		return

class HrExpense(models.Model):
	_inherit = "hr.expense"

	equipment_id = fields.Many2one('my.equipment.request')

class Damage_Details(models.Model):  
	_name = 'damage.details'

	product_id = fields.Many2one('product.product',string="Product",domain=[('can_be_expensed','=',True)],required=True)
	unit_price = fields.Float(string = "Unit Price",required=True)
	product_qty = fields.Float(string="Quantity",required=True, default=1)
	note = fields.Char(string="Expense Note")
	equipment_id = fields.Many2one('my.equipment.request')
	expense_line_created = fields.Boolean(string="Expense Line Created", default=False)

	def unlink(self):
		for dd in self:
			if dd.expense_line_created:
				raise UserError(_('Sorry !!! You can not delete a record because its expense is already generated .'))
		self.equipment_id.onchange_damage_details_ids()
		return super(Damage_Details, self).unlink()

	@api.onchange('product_id')
	def onchange_damage_details_ids(self):
		for rec in self:
			rec.unit_price = rec.product_id.list_price

class equipment_request(models.Model):  
	_name = 'equipment.request'

	name = fields.Char(string="Description")
	product_id = fields.Many2one('product.product',string="Product")
	product_unit = fields.Many2one('uom.uom',string="Product Unit of Measure")
	product_qty = fields.Float(string="Product Quantity", default=1)
	equipment_id = fields.Many2one('my.equipment.request')

	@api.onchange('product_id')
	def onchange_product(self):
		self.name =self.product_id.name
		self.product_unit = self.product_id.uom_id.id

class Picking_Inherit(models.Model):
	_inherit = "stock.picking"

	equipment_id = fields.Many2one('my.equipment.request')


	
	
