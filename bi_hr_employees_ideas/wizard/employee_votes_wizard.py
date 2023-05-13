# -*- coding: utf-8 -*-
# Part of Browseinfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

class employee_votes_wizard(models.TransientModel):
	_name = "employee.votes.wizard"

	
	employee_id = fields.Many2one('res.users',string="Employee",default=lambda self : self.env.user.id)
	department_id = fields.Many2one('hr.department',string="Department")
	comments = fields.Text(string="Comments",required=True)
	rating = fields.Selection([('bad','Bad'),('avg','Average'),('good','Good'),('very good','Very Good'),('excellent','Excellent')],string="Rateing")

	def save_vote(self):
		self.ensure_one()
		res = self.env['employee.idea'].browse(self._context.get('active_id'))		
		vals = [[0,0,{'department_id': self.department_id.id,'comments':self.comments,'rating':self.rating,'employee_id':self.env.user.id}]]
		res.employee_votes_ids = vals
		return 
