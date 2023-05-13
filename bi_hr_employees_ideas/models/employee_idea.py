# -*- coding: utf-8 -*-
# Part of Browseinfo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, _
from odoo.exceptions import UserError

class employee_idea(models.Model):
	_name = "employee.idea"

	name = fields.Char('Title',required=True)
	idea_seq = fields.Char(string="Idea No", readonly=True, copy=False)
	employee_id = fields.Many2one('res.users',string="Employee")
	department_id = fields.Many2one('hr.department',string="Department")
	create_date = fields.Date(string="Create Date")
	deadline_date = fields.Date(string="Deadline",required=True)
	company_id = fields.Many2one('res.company',string="Company")
	idea_type_id = fields.Many2one('idea.type',string="Idea Type")
	details = fields.Text(string="Details",required=True)
	state = fields.Selection([('new','New'),('waiting','Waiting For Approval'),('approved','Approved'),('close','Closed')],string="States",default="new")
	employee_votes_ids = fields.One2many('employee.votes','idea_id',string="Employee Votes",readonly=True)
	count_votes = fields.Integer(string = "Vote Counts" ,compute="_compute_count_votes",store=True)


	@api.constrains('create_date','deadline_date')
	def check_deadline(self):

		if self.create_date > self.deadline_date :
			raise	UserError(_('Deadline must be after create date'))

	@api.depends('employee_votes_ids')
	def _compute_count_votes(self):
		for res in self :
			votes = 0
			for line in self.employee_votes_ids :
				if line.rating :
					votes = votes + 1
			res['count_votes'] = votes
		return

	@api.model
	def create(self, vals):

		seq = self.env['ir.sequence'].next_by_code('employee.idea') or '/'
		vals['idea_seq'] = seq
		return super(employee_idea, self).create(vals)

	
	def post_idea(self):
		self.write({'state': 'waiting'})
		return

	def close_idea(self):
		self.write({'state': 'close'})
		return


	def approve_idea(self):
		self.write({'state': 'approved'})
		return

	def refuse_idea(self):
		self.write({'state': 'new'})
		return

	def action_votes(self):
		return {
			'name': 'Employee Votes',
			'type': 'ir.actions.act_window',
			'view_mode': 'tree,form',
			'context': {},
			'res_model': 'employee.votes',
			'domain': [('idea_id','=',self.id),('rating','in',['bad','avg','good','very good','excellent'])],	
		}

		pass

class idea_type(models.Model):
	_name = "idea.type"

	name = fields.Char('Name')
	minimum_votes = fields.Integer(string="Minimum Votes",default = 0,compute="_compute_total_ideas")
	maximum_votes = fields.Integer(string="Maximum Votes",default = 0,compute="_compute_total_ideas")

	total_ideas = fields.Integer(string="Total Idea",compute="_compute_total_ideas")
	department_ids = fields.Many2many('hr.department','idea_type_rel',string="Departments")

	employee_idea_ids = fields.One2many('employee.idea','idea_type_id',string="Ideas",compute="_compute_total_ideas")


	def _compute_total_ideas(self):
		for rec in self:
			res = self.env['employee.idea'].search([('idea_type_id','=',rec.id)])
			vote_list = []
			idea_count = 0
			for i in res :
				vote_list.append(i.count_votes)
				idea_count = idea_count + 1
			if len(vote_list) > 0:
				rec.minimum_votes = min(vote_list)
				rec.maximum_votes = max(vote_list)
			else:
				rec.minimum_votes = 0
				rec.maximum_votes = 0
			rec.total_ideas = idea_count
			rec.employee_idea_ids = [(6,0,res.ids)]


class employee_votes(models.Model):
	_name = "employee.votes"

	idea_id = fields.Many2one('employee.idea')
	employee_id = fields.Many2one('res.users',string="Employee")
	department_id = fields.Many2one('hr.department',string="Department")
	comments = fields.Text(string="Comments")
	rating = fields.Selection([('bad','Bad'),('avg','Average'),('good','Good'),('very good','Very Good'),('excellent','Excellent')],string="Rateing")







	


    