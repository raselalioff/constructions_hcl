# -*- coding: utf-8 -*-
# Part of Browseinfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import Warning, UserError


class visitors_pass(models.Model):
	_name = "visitor.pass"
	_description = "Visitor Pass"

	name = fields.Char(string="Visitor No.", readonly=True, copy=False)
	visitor_name = fields.Char(string = "Name" ,required= True)
	phone_number = fields.Char(string ="Phone Number")
	reasone =      fields.Char (string="Reason")
	email = fields.Char(string="Email")
	visitor_company = fields.Many2one('res.company',string="Visitor Company")
	time_in = fields.Datetime(string="Date Time In")
	time_out = fields.Datetime(string="Date Time Out")
	employee_id = fields.Many2one('hr.employee',string= "Employee")
	state = fields.Selection([('draft','Draft'),('confirm','Confirm'),('exit','Exit')],string = "States",default="draft")
	department_id =fields.Many2one('hr.department',string = "Department")
	created_by_id = fields.Many2one('res.users',string="Created By")
	company_id = fields.Many2one("res.company",string = "Company")


	@api.constrains('time_in','time_out')
	def check_times(self):
		if self.time_in and self.time_out :
			if self.time_in >= self.time_out :
				raise Warning(_('Date Time Out should be after the Date Time In !!') )
		

	def confirm_visitor(self):
		self.write({'state': 'confirm'})
		return


	def exit_visitor(self):
		self.write({'state': 'exit'})
		return

	def print_report(self):
		return self.env.ref('bi_hr_company_visitors_pass.report_visitor_pass').report_action(self)

	@api.model
	def create(self, vals):

		seq = self.env['ir.sequence'].next_by_code('visitor.pass') or '/'
		vals['name'] = seq
		return super(visitors_pass, self).create(vals)