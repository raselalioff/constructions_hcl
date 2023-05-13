from datetime import datetime
from odoo import api, fields, models
from odoo.exceptions import Warning
from odoo.tools.translate import _
 
 
class Res_User(models.Model):
    _inherit = 'res.users'
    _description = 'Res User'
     
     
#    project_id = fields.Many2one('project.project', 'Project')
    
    project_id = fields.Many2many('project.project','user_project_rel','project_id','user_id',string="Projects")
    task_ids = fields.Many2many('project.task','user_project_task_rel','task_id','user_id',string="Tasks")
    task_category_ids = fields.Many2many('task.category','user_category_rel','category_id','user_id',string="Task Categories")