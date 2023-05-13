from datetime import datetime
import time

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.exceptions import Warning
from odoo.tools.translate import _
import json
from odoo.http import request


class ApprovalWizard(models.TransientModel):
    _name = 'wizard.gantt'
    _description = 'Project selection for gantt'

    project_id = model = fields.Many2one('project.project', 'Project')
    child_list = []  # Important- used in recursive function
    note = fields.Text('Note', default='Note:Please select project to view Gantt Chart and ensure debug mode is off.')

    # @api.multi
    def open_gantt_view_action(self):
        request.params['session_pr_id'] = self.project_id.id
        request.session['project_id_wizard'] = self.project_id.id
        return {
            'name': 'Gantt Chart',
            'type': 'ir.actions.client',
            'tag': 'gantt_chart',
            'params': {'project_id': self.project_id.id},
            'context': {'project_id': self.project_id.id},
        }

    @api.model
    def get_data(self, project):
        if project:
            gantt_project = project
            task_list = []
            seq = 1
            project = self.env['project.project'].browse(gantt_project)  # must be browse,don't change
            from datetime import datetime
            startdate = fields.Datetime.to_string(project.start_date)
            timestamp = time.mktime(datetime.strptime(startdate, "%Y-%m-%d %H:%M:%S").timetuple())

            enddate = fields.Datetime.to_string(project.finish_date)
            timeftamp = time.mktime(datetime.strptime(enddate, "%Y-%m-%d %H:%M:%S").timetuple())

            d_in_ms = int(timestamp) * 1000
            e_in_ms = int(timeftamp) * 1000
            d1 = fields.Date.from_string(startdate)
            d2 = fields.Date.from_string(enddate)
            d3 = (d2 - d1)

            for line in project:
                now = line.start_date

                vals = {'model': 'project.project', 'shortcut': 'a', 'seq':seq, 'id': -1, "name": line.name,
                        "level": 0, 'depends': "", "progress": '0', "progressByWorklog": False,
                        "relevance": '0', "type": "", "typeId": "", "description": "",
                        "code": "", "status": "STATUS_ACTIVE", "canWrite": True,
                        "start": d_in_ms, "duration": d3.days, "end": e_in_ms,
                        "startIsMilestone": False, "endIsMilestone": False, "canWrite": True,
                        "collapsed": False, "depends": "", "assigs": [], "hasChild": True,
                        "dbid": line.id, 'is_project': True, }

                task_list.append(vals)
            sub_projects = self.env['sub.project'].search([('project_id', '=', project.id)])
            length = len(sub_projects)
            
            all_task_list = []
            for line in sub_projects:
                sub_list = []
                seq = seq + 1
                startdate = fields.Datetime.to_string(line.start_date)
                timestamp = time.mktime(datetime.strptime(startdate, "%Y-%m-%d %H:%M:%S").timetuple())

                enddate = fields.Datetime.to_string(line.end_date)
                timeftamp = time.mktime(datetime.strptime(enddate, "%Y-%m-%d %H:%M:%S").timetuple())

                d_in_ms = int(timestamp) * 1000
                e_in_ms = int(timeftamp) * 1000
                d1 = fields.Date.from_string(startdate)
                d2 = fields.Date.from_string(enddate)
                d3 = (d2 - d1)

                project_id = str(line.project_id.id)
                vals = {'model': 'sub.project', 'seq':seq, 'shortcut': 'b', 'is_subproject': True,
                        "dbid": line.id, "name": line.name, 'depends': "1", "level": 1,
                        "progress": '0', "progressByWorklog": False, "relevance": '0',
                        "type": "", "typeId": "", "description": "", "code": "",
                        "status": "STATUS_ACTIVE", "canWrite": True, "start": d_in_ms,
                        "duration": d3.days, "end": e_in_ms, "startIsMilestone": False,
                        "endIsMilestone": False, "canWrite": True, "collapsed": False,
                        "depends": "", "assigs": [], "hasChild": True}
# 
                sub_list.append(vals)
                data = self.env['project.task'].search([('is_wbs','=',True),('sub_project','=',line.id)])
                if data and sub_list:
#                     wbs_list = self.get_wbs_list(data)
                    out_list = self.get_task_list(data, sub_list, seq)
                    sorted_list = sorted(out_list, key = lambda i: i['seq'])
                    for line in sorted_list:
                        if line.get('dbid') not in all_task_list:
                            task_list.append(line)
                            all_task_list.append(line.get('dbid'))
            
            id = 0
            for dict in task_list:
                id = id + 1
                dict.update({'id': -id, })
        return json.dumps(task_list)
    
    def get_childs(self, task_obj):
        if not task_obj.is_wbs:
            self.child_list.append(task_obj)
        else:
            self.child_list.append(task_obj)
            
        task_obj=self.env['project.task'].search([('parent_id','=',task_obj.id)])
        for line in task_obj:
            self.get_childs(line)
        else:
            return list(set(self.child_list))
        
    def get_task_list(self, data, task_list, seq):
        for line in data:
            seq = seq + 1
            planed_start_date = fields.Datetime.to_string(line.planed_start_date)
            timestamp = time.mktime(datetime.strptime(planed_start_date, "%Y-%m-%d %H:%M:%S").timetuple())

            planed_end_date = fields.Datetime.to_string(line.planned_finish_date)
            timeftamp = time.mktime(datetime.strptime(planed_end_date, "%Y-%m-%d %H:%M:%S").timetuple())

            wbs_s_date = int(timestamp) * 1000
            wbs_e_date = int(timeftamp) * 1000
            d1 = fields.Date.from_string(planed_start_date)
            d2 = fields.Date.from_string(planed_end_date)
            d3 = (d2 - d1)
            vals = {'model':'project.task', 'shortcut': 'c', 'is_wbs': True,'seq':seq,
                        "dbid": line.id, "name": line.name, 'depends': "1", "level": 2,
                        "progress": '0', "progressByWorklog": False, "relevance": '0',
                        "type": "", "typeId": "", "description": "", "code": "",
                        "status": "STATUS_ACTIVE", "canWrite": True, "start": wbs_s_date,
                        "duration": d3.days, "end": wbs_e_date, "startIsMilestone": False,
                        "endIsMilestone": False, "canWrite": True, "collapsed": False,
                        "depends": "", "assigs": [], "hasChild": True}
# 
# 
            task_list.append(vals)
            
            for tsk_grp in line.wbs_task_ids:
                seq = seq + 1
                startdate = fields.Datetime.to_string(tsk_grp.planed_start_date)
                timestamp = time.mktime(datetime.strptime(startdate, "%Y-%m-%d %H:%M:%S").timetuple())
                 
                enddate = fields.Datetime.to_string(tsk_grp.planned_finish_date)
                timeftamp = time.mktime(datetime.strptime(enddate, "%Y-%m-%d %H:%M:%S").timetuple())
                
                d_in_ms = int(timestamp) * 1000
                e_in_ms = int(timeftamp) * 1000
                d1 = fields.Date.from_string(startdate)
                d2 = fields.Date.from_string(enddate)
                d3 = (d2 - d1)
                
                vals={'model':'project.task','shortcut':'d','is_task':True,'seq':seq,
                      "dbid": tsk_grp.id, "name": tsk_grp.name,  "progress": '0',
                      "progressByWorklog": False, "relevance": '0', "type": "",
                      "typeId": "", "description": "", "code": "e_in_ms",
                      "status": "STATUS_ACTIVE",  "canWrite": True,
                      "start": d_in_ms, "duration": d3.days, "end": e_in_ms,
                      "startIsMilestone": False, "endIsMilestone": False,
                      "canWrite": True, "collapsed": False,"depends": "",
                      "assigs": [], "hasChild": False, 'level':3}
                task_list.append(vals)
                for task in tsk_grp.task_ids:
                    if not task.planed_start_date:
                        raise Warning("Please define start date of %s"%(task.name))
                    seq = seq + 1
                    if task.planed_start_date:
                        startdate = fields.Datetime.to_string(task.planed_start_date)
                        timestamp = time.mktime(datetime.strptime(startdate, "%Y-%m-%d %H:%M:%S").timetuple())
                         
                        enddate = fields.Datetime.to_string(task.planned_finish_date)
                        timeftamp = time.mktime(datetime.strptime(enddate, "%Y-%m-%d %H:%M:%S").timetuple())
         
                        d_in_ms = int(timestamp) * 1000
                        e_in_ms = int(timeftamp) * 1000
                        d1 = fields.Date.from_string(startdate)
                        d2 = fields.Date.from_string(enddate)
                        d3 = (d2 - d1)
                        
                        vals={'model':'project.task','shortcut':'e','is_task':True,'seq':seq,
                              "dbid": task.id, "name": task.name,  "progress": '0',
                              "progressByWorklog": False, "relevance": '0', "type": "",
                              "typeId": "", "description": "", "code": "e_in_ms",
                              "status": "STATUS_ACTIVE",  "canWrite": True,
                              "start": d_in_ms, "duration": d3.days, "end": e_in_ms,
                              "startIsMilestone": False, "endIsMilestone": False,
                              "canWrite": True, "collapsed": False,"depends": "",
                              "assigs": [], "hasChild": False, 'level':4}
                        task_list.append(vals)
        return task_list
                        
               
                
                
#             task_group_list_sorted = []
#             old_list = []
#             new_list = []
#             previous_child = []
#             if line.wbs_task_ids:
#                 previous_child = self.child_list
#                 task_group_list = self.get_childs(line)
#                 present_child = task_group_list
#             else:
#                 task_group_list.append(line)
            
#         for task in task_group_list:
#             task_group_list_sorted.append(task.id)
#         for task in list(sorted(task_group_list_sorted)):
#             
#             task = self.env['project.task'].browse(task)
#             if task.is_task:
#                 if not task.planed_start_date:
#                     raise Warning("Please define start date of %s"%(task.name))
#                 if task.planed_start_date:
#                     startdate = fields.Datetime.to_string(task.planed_start_date)
#                     timestamp = time.mktime(datetime.strptime(startdate, "%Y-%m-%d %H:%M:%S").timetuple())
# 
#                     enddate = fields.Datetime.to_string(task.planned_finish_date)
#                     timeftamp = time.mktime(datetime.strptime(enddate, "%Y-%m-%d %H:%M:%S").timetuple())
# 
#                     d_ms = int(timestamp) * 1000
#                     e_in_ms = int(timeftamp) * 1000
#                     d1 = fields.Date.from_string(startdate)
#                     d2 = fields.Date.from_string(enddate)
#                     d3 = (d2 - d1)
# 
#                     vals={'model':'project.task','shortcut':'d','is_task':True,
#                           "dbid": task.id, "name": task.name,  "progress": '0',
#                           "progressByWorklog": False, "relevance": '0', "type": "",
#                           "typeId": "", "description": "", "code": "",
#                           "status": "STATUS_ACTIVE",  "canWrite": True,
#                           "start": d_ms, "duration":d3.days, "end": e_in_ms,
#                           "startIsMilestone": False, "endIsMilestone": False,
#                           "canWrite": True, "collapsed": False,"depends": "",
#                           "assigs": [], "hasChild": False,'level':4}
# #                     task_list.append(vals)
#             else:
#                 if not task.planed_start_date:
#                     raise Warning("Please define start date of %s"%(task.name))
#                 if task.planed_start_date:
#                     startdate = fields.Datetime.to_string(task.planed_start_date)
#                     timestamp = time.mktime(datetime.strptime(startdate, "%Y-%m-%d %H:%M:%S").timetuple())
#                     
#                     enddate = fields.Datetime.to_string(task.planned_finish_date)
#                     timeftamp = time.mktime(datetime.strptime(enddate, "%Y-%m-%d %H:%M:%S").timetuple())
#     
#                     d_in_ms = int(timestamp) * 1000
#                     e_in_ms = int(timeftamp) * 1000
#                     d1 = fields.Date.from_string(startdate)
#                     d2 = fields.Date.from_string(enddate)
#                     d3 = (d2 - d1)
#     
#                     vals={'model':'project.task','shortcut':'e','is_task':True,
#                           "dbid": task.id, "name": task.name,  "progress": '0',
#                           "progressByWorklog": False, "relevance": '0', "type": "",
#                           "typeId": "", "description": "", "code": "e_in_ms",
#                           "status": "STATUS_ACTIVE",  "canWrite": True,
#                           "start": d_in_ms, "duration": d3.days, "end": e_in_ms,
#                           "startIsMilestone": False, "endIsMilestone": False,
#                           "canWrite": True, "collapsed": False,"depends": "",
#                           "assigs": [], "hasChild": False}
#                     if task.parent_id.is_wbs:
#                         vals.update({'level':3})
#                     else:
#                         vals.update({'level':2})
#                     task_list.append(vals)
#         return task_list