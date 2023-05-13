# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime, timedelta, date, time
from odoo.tools.misc import xlwt
import io
import base64
from xlwt import easyxf

from operator import itemgetter

from dateutil.relativedelta import relativedelta
from pytz import timezone
from odoo.tools.float_utils import float_round
import pytz
import math
import logging

_logger = logging.getLogger(__name__)

def float_to_time(hours, moment='am'):
    """ Convert a number of hours into a time object. """
    if hours == 12.0 and moment == 'pm':
        return time.max
    fractional, integral = math.modf(hours)
    if moment == 'pm':
        integral -= 12
    print("===========\n\n",integral,"  ",fractional)
    return time(int(integral), int(float_round(60 * fractional, precision_digits=0)), 0)

class AttendanceReport(models.TransientModel):
    _name = 'attendance.report'
    _description = "Attendance Report Wizard"

    month = fields.Selection([
                ('1', 'January'),
                ('2', 'February'),
                ('3', 'March'),
                ('4', 'April'),
                ('5', 'May'),
                ('6', 'June'),
                ('7', 'July'),
                ('8', 'Auguest'),
                ('9', 'September'),
                ('10', 'October'),
                ('11', 'November'),
                ('12', 'December')
            ], string="Month",required=1, default=lambda x: str(datetime.now().month))

    to_month = fields.Selection([
                ('1', 'January'),
                ('2', 'February'),
                ('3', 'March'),
                ('4', 'April'),
                ('5', 'May'),
                ('6', 'June'),
                ('7', 'July'),
                ('8', 'Auguest'),
                ('9', 'September'),
                ('10', 'October'),
                ('11', 'November'),
                ('12', 'December')
            ], string="Month",required=1, default=lambda x: str(datetime.now().month))

    def _get_selection(self):
        current_year = datetime.now().year
        return [(str(i), i) for i in range(current_year - 5, current_year + 5)]

    year = fields.Selection(
        selection='_get_selection', string='Year',required=1,
        default=lambda x: str(datetime.now().year))

    to_year = fields.Selection(
        selection='_get_selection', string='Year',required=1,
        default=lambda x: str(datetime.now().year))

    date_type_selection = fields.Selection([('1to31',"1-31"),('26to25','26-25')],default='26to25',string="Date Type")

    employee_ids = fields.Many2many('hr.employee', string="Employee")
    employee_id = fields.Many2one('hr.employee', string="Employee")
    department_id = fields.Many2many('hr.department', string="Department")

    report_type = fields.Selection([('department','Department Summary'),
                                ('details','Individual Attendance Report'),
                                ('evaluation','Attendance Evaluation')
                                ], string="Report Type", default="evaluation")


    def _compute_late_checkin_min(self, attendance):
        late_checkin_min = 0
        if attendance.check_in:
            attendance_date = attendance.check_in.date()
            attendance_day = datetime.strptime(str(attendance_date), '%Y-%m-%d').strftime('%a').upper()
            day_no = ''
            if attendance_day == 'SAT':
                day_no = '5'
            elif attendance_day == 'SUN':
                day_no = '6'
            elif attendance_day == 'MON':
                day_no = '0'
            elif attendance_day == 'TUE':
                day_no = '1'
            elif attendance_day == 'WED':
                day_no = '2'
            elif attendance_day == 'THU':
                day_no = '3'
            elif attendance_day == 'FRI':
                day_no = '4'

            from_hour_s = 0
            to_hour_s = 0
            employee_att_days = attendance.employee_id.resource_calendar_id.attendance_ids.filtered(
                lambda line: line.dayofweek == day_no)
            for rec in employee_att_days:
                hour_from = rec.hour_from
                day_period = rec.day_period
                if day_period == 'morning':
                    from_hour_s = hour_from
                elif day_period == 'afternoon':
                    to_hour_s = hour_from
            if from_hour_s == 0:
                from_hour_s = to_hour_s

            att_dt = attendance_date.strftime('%Y-%m-%d %H:%M:%S')
            start_time = datetime.strptime(att_dt, '%Y-%m-%d %H:%M:%S') + timedelta(
                hours=from_hour_s) - timedelta(hours=6)


            if start_time < attendance.check_in:
                late_checkin_time = attendance.check_in - start_time
                late_checkin_second = late_checkin_time.seconds
                late_checkin_min = late_checkin_second / 60

        return late_checkin_min

    def _compute_early_checkout_min(self, attendance):
        early_checkout_min = 0
        if attendance.check_out:
            attendance_date = attendance.check_out.date()
            attendance_day = datetime.strptime(str(attendance_date), '%Y-%m-%d').strftime('%a').upper()
            day_no = ''
            if attendance_day == 'SAT':
                day_no = '5'
            elif attendance_day == 'SUN':
                day_no = '6'
            elif attendance_day == 'MON':
                day_no = '0'
            elif attendance_day == 'TUE':
                day_no = '1'
            elif attendance_day == 'WED':
                day_no = '2'
            elif attendance_day == 'THU':
                day_no = '3'
            elif attendance_day == 'FRI':
                day_no = '4'

            from_hour_e = 0
            to_hour_e = 0
            employee_att_days = attendance.employee_id.resource_calendar_id.attendance_ids.filtered(
                lambda line: line.dayofweek == day_no)
            for rec in employee_att_days:
                hour_to = rec.hour_to
                day_period = rec.day_period
                if day_period == 'morning':
                    from_hour_e = hour_to
                elif day_period == 'afternoon':
                    to_hour_e = hour_to
            if to_hour_e == 0:
                to_hour_e = from_hour_e

            att_dt = attendance_date.strftime('%Y-%m-%d %H:%M:%S')
            end_time = datetime.strptime(att_dt, '%Y-%m-%d %H:%M:%S') + timedelta(
                hours=to_hour_e) - timedelta(hours=6)

            if end_time > attendance.check_out:
                early_checkout_time = end_time - attendance.check_out
                early_checkout_second = early_checkout_time.seconds
                early_checkout_min = early_checkout_second / 60
        return early_checkout_min


    def _get_attendance_employee_tz(self, date=None):
        tz = self.env.user.partner_id.tz
        if not date:
            return False
        time_zone = pytz.timezone(tz or "UTC")
        attendance_tz_dt = pytz.UTC.localize(date)
        attendance_tz_dt = attendance_tz_dt.astimezone(time_zone)
        return attendance_tz_dt

    def print_report(self):
        if self.date_type_selection == '26to25':
            date_end = datetime.strptime('{0}-{1}-25'.format(self.year,self.month), '%Y-%m-%d').date()
            date_start = date_end - relativedelta(months=1)
            date_start = date_start + relativedelta(days=1)
        else:
            date_start = datetime.strptime('{0}-{1}-01'.format(self.year,self.month), '%Y-%m-%d').date()
            date_end = date_start + relativedelta(months=1)
            date_end = date_end - relativedelta(days=1)

        print("============")
        print(date_start," == ", date_end)
        domain = []
        datas = []
        hr_attendance_objs_list = []
        
        if self.report_type == 'details':
            employee = self.employee_id
            resource_calendar_id = employee.resource_calendar_id or self.env.company.resource_calendar_id
            present = 0
            absent = 0
            tz = timezone(resource_calendar_id.tz)
            date_from = tz.localize(datetime.combine(fields.Datetime.from_string(str(date_start)), time.min))
            date_to = tz.localize(datetime.combine(fields.Datetime.from_string(str(date_end)), time.max))
            intervals = employee.list_work_time_per_day(date_from, date_to, calendar=resource_calendar_id)

            office_days = list()
            for item in intervals:
                # office_days.append("{}-{}-{}".format(item[0].year,item[0].month,item[0].day))
                office_days.append(item[0].strftime('%Y-%m-%d'))
            week_days = resource_calendar_id.attendance_ids.mapped('dayofweek')
            leave_days = list()
            holidays = list()
            leaves = employee.list_leaves(date_from, date_to, calendar=resource_calendar_id)
            for item in leaves:
                if str((int(item[0].strftime('%w'))-1)%7) in week_days:
                    if item[2].resource_id:
                        leave_days.append(item[0].strftime('%Y-%m-%d'))
                    else:
                        holidays.append(item[0].strftime('%Y-%m-%d'))
            

            total_working_time = 0
            while(date_from<=date_to):
                day = str((int(date_from.strftime('%w'))-1)%7)
                if day not in week_days:
                    hr_attendances = [{
                            'schedule_in': "",
                            'schedule_out': "",
                            'description': "WEEKEND",
                            'check_in': "",
                            'check_out': "",                            
                            'worked_hours': "00:00",
                            'attendance_date': date_from.strftime('%d %b %Y %a'),
                            'late_check_in': "",
                            'early_check_out': "",
                            'note': "",
                        }]
                    hr_attendance_objs_list.append(hr_attendances)
                elif str(date_from.date()) in office_days:
                    idx = office_days.index(str(date_from.date()))
                    rec = intervals[idx]
                    attendances = self.env["hr.attendance"].search(
                        [('employee_id', '=', employee.id), ('check_in', '>=', rec[0]),
                         ('check_in', '<=', rec[0])], order='check_in')
                    shift_lines = resource_calendar_id.attendance_ids.filtered(lambda x: x.dayofweek == day)
                    shift_start = float_to_time(shift_lines[0].hour_from)
                    shift_end = float_to_time(shift_lines[len(shift_lines)-1].hour_to, 'pm')

                    if attendances:
                        for item in attendances:
                            g = float("{:.2f}".format(item.worked_hours))
                            total_working_time += item.worked_hours
                            late_check_in = self._compute_late_checkin_min(item)>0 and 'Y' or 'N'
                            early_check_out = self._compute_early_checkout_min(item)>0 and 'Y' or 'N'

                            hr_attendances = [{
                                'schedule_in': "{} AM".format(shift_start),
                                'schedule_out': "{} PM".format(shift_end),
                                'description': "LATE: {}, EARLY: {}".format(late_check_in, early_check_out),
                                'check_in': self._get_attendance_employee_tz(item.check_in).strftime('%I:%M:%S %p'),
                                'check_out': item.check_out and self._get_attendance_employee_tz(item.check_out).strftime('%I:%M:%S %p') or "",                            
                                'worked_hours': g,
                                'attendance_date': date_from.strftime('%d %b %Y %a'),
                                'late_check_in': self._compute_late_checkin_min(item)>0 and 'Y' or 'N',
                                'early_check_out': self._compute_early_checkout_min(item)>0 and 'Y' or 'N',
                                'note': item.comment,
                            }]
                            hr_attendance_objs_list.append(hr_attendances)
                        present += 1
                    else:
                        absent += 1
                        hr_attendances = [{
                            'schedule_in': "{} AM".format(shift_start),
                            'schedule_out': "{} PM".format(shift_end),
                            'description': "ABSENT",
                            'check_in': "",
                            'check_out': "",                            
                            'worked_hours': "00:00",
                            'attendance_date': date_from.strftime('%d %b %Y %a'),
                            'late_check_in': "",
                            'early_check_out': "",
                            'note': "",
                        }]
                        hr_attendance_objs_list.append(hr_attendances)

                    
                elif str(date_from.date()) in leave_days:
                    hr_attendances = [{
                            'schedule_in': "",
                            'schedule_out': "",
                            'description': "LEAVE",
                            'check_in': "",
                            'check_out': "",                            
                            'worked_hours': "00:00",
                            'attendance_date': date_from.strftime('%d %b %Y %a'),
                            'late_check_in': "",
                            'early_check_out': "",
                            'note': "",
                        }]
                    hr_attendance_objs_list.append(hr_attendances)

                elif str(date_from.date()) in holidays:
                    hr_attendances = [{
                            'schedule_in': "",
                            'schedule_out': "",
                            'description': "Holiday",
                            'check_in': "",
                            'check_out': "",                            
                            'worked_hours': "00:00",
                            'attendance_date': date_from.strftime('%d %b %Y %a'),
                            'late_check_in': "",
                            'early_check_out': "",
                            'note': "",
                        }]
                    hr_attendance_objs_list.append(hr_attendances)

                date_from = date_from + timedelta(days=1)


            
            count = len(hr_attendance_objs_list)

            res = {
                'employee_name': employee.employee_id+" "+employee.name,
                'department': employee.department_id.name,
                'designation': employee.job_title,
                'present': present,
                'absent': absent,
                'month': dict(self._fields['month'].selection).get(self.month),
                'year': self.year,
                'total_working_time': float("{:.2f}".format(total_working_time)),
                'average_working_time': float("{:.2f}".format((len(intervals)>0 and (total_working_time / len(intervals)) or 0)))
            }
            data = {
                'form': res,
                'lists': hr_attendance_objs_list,
                'count': count
            }
            return self.env.ref('aam_attendance_report.report_hr_attendance').report_action([], data=data)
        elif self.report_type == 'department':
            self.env.cr.execute(""" TRUNCATE TABLE employee_attendance_summary; """)
            for department in self.department_id:
                domain = [('department_id','child_of',department.id)]
                attendace_vals = {
                    'department': 'yes',
                    'employee_name': department.name,
                    'employee_id': "Department",
                    'designation': "",
                    'total_days': "",
                    'total_holiday': "",
                    'total_weekend': "",
                    'total_leave': "",
                    'total_office_day': "",
                    'present': "",
                    'absent': "",
                    'shift': "",
                    'late_check_in': "",
                    'early_check_out': "",
                    'month': "",
                    'year': "",
                    'total_working_time': "",
                    'average_working_time': ""
                }
                self.env['employee.attendance.summary'].create(attendace_vals)
                employee_ids = self.env['hr.employee'].search(domain)
                for employee in employee_ids:
                    resource_calendar_id = employee.resource_calendar_id or self.env.company.resource_calendar_id
                    present = 0
                    absent = 0
                    tz = timezone(resource_calendar_id.tz)
                    date_from = tz.localize(datetime.combine(fields.Datetime.from_string(str(date_start)), time.min))
                    date_to = tz.localize(datetime.combine(fields.Datetime.from_string(str(date_end)), time.max))
                    intervals = employee.list_work_time_per_day(date_from, date_to, calendar=resource_calendar_id)
                    leaves = employee.list_leaves(date_from, date_to, calendar=resource_calendar_id)
                    print("leaves == \n",intervals)
                    print("leaves == \n",leaves)
                    total_leave = 0
                    total_holiday = 0
                    for item in leaves:
                        if item[2].resource_id:
                            total_leave += 1
                        else:
                            total_holiday += 1
                    total_working_time = 0
                    late_check_in = 0
                    early_check_out = 0
                    for rec in intervals:
                        attendances = self.env["hr.attendance"].search(
                            [('employee_id', '=', employee.id), ('check_in', '>=', rec[0]),
                             ('check_in', '<=', rec[0])], order='check_in')

                        if attendances:
                            for item in attendances:
                                total_working_time += item.worked_hours
                                if self._compute_late_checkin_min(item)>0:
                                    late_check_in += 1
                                if self._compute_early_checkout_min(item)>0:
                                    early_check_out += 1
                                
                            present += 1
                        else:
                            absent += 1
                    
                    count = len(hr_attendance_objs_list)

                    total_weekend = 0
                    week_days = resource_calendar_id.attendance_ids.mapped('dayofweek')
                    while(date_from<=date_to):
                        day = str((int(date_from.strftime('%w'))-1)%7)
                        if day not in week_days:
                            total_weekend += 1
                        date_from = date_from + timedelta(days=1)

                    shift_lines = resource_calendar_id.attendance_ids
                    shift_start = float_to_time(shift_lines[0].hour_from)
                    shift_end = float_to_time(shift_lines[len(shift_lines)-1].hour_to, 'pm')
                    attendace_vals = {
                        'department': 'no',
                        'employee_name': employee.name,
                        'employee_id': employee.employee_id,
                        'designation': employee.job_title,
                        'total_days': date_end.day,
                        'total_holiday': total_holiday,
                        'total_weekend': total_weekend,
                        'total_leave': total_leave,
                        'total_office_day': len(intervals),
                        'present': present,
                        'absent': absent,
                        'shift': "{:.2f}AM-{:.2f}PM".format(shift_start,shift_end),
                        'late_check_in': late_check_in,
                        'early_check_out': early_check_out,
                        'month': dict(self._fields['month'].selection).get(self.month),
                        'year': self.year,
                        'total_working_time': float("{:.2f}".format(total_working_time)),
                        'average_working_time': float("{:.2f}".format((len(intervals)>0 and (total_working_time / len(intervals)) or 0)))
                    }
                    self.env['employee.attendance.summary'].create(attendace_vals)
            
            docids = self.env['employee.attendance.summary'].search([])
            if len(docids)>0:
                _logger.info(docids)
                return self.env.ref('aam_attendance_report.report_hr_attendance_summary').report_action(docids)
            else:
                raise UserError("No Data Found")
        elif self.report_type == 'evaluation':
            self.env.cr.execute(""" TRUNCATE TABLE employee_attendance_summary; """)
            
            employee = self.employee_id
            resource_calendar_id = employee.resource_calendar_id or self.env.company.resource_calendar_id
            
            month = int(self.month)
            year = int(self.year)
            month_start = int(self.month)
            month_end = (int(self.to_year) - int(self.year))*12 + int(self.to_month)

            while(month_start <= month_end):
                print(month_start,"===",month_end)
                present = 0
                absent = 0
                tz = timezone(resource_calendar_id.tz)
                date_from = tz.localize(datetime.combine(fields.Datetime.from_string(str(date_start)), time.min))
                date_to = tz.localize(datetime.combine(fields.Datetime.from_string(str(date_end)), time.max))
                intervals = employee.list_work_time_per_day(date_from, date_to, calendar=resource_calendar_id)
                leaves = employee.list_leaves(date_from, date_to, calendar=resource_calendar_id)
                print("leaves == \n",intervals)
                print("leaves == \n",leaves)
                total_leave = 0
                total_holiday = 0
                for item in leaves:
                    if item[2].resource_id:
                        total_leave += 1
                    else:
                        total_holiday += 1
                total_working_time = 0
                late_check_in = 0
                early_check_out = 0
                for rec in intervals:
                    attendances = self.env["hr.attendance"].search(
                        [('employee_id', '=', employee.id), ('check_in', '>=', rec[0]),
                         ('check_in', '<=', rec[0])], order='check_in')

                    if attendances:
                        for item in attendances:
                            total_working_time += item.worked_hours
                            if self._compute_late_checkin_min(item)>0:
                                late_check_in += 1
                            if self._compute_early_checkout_min(item)>0:
                                early_check_out += 1
                            
                        present += 1
                    else:
                        absent += 1
                
                count = len(hr_attendance_objs_list)

                total_weekend = 0
                week_days = resource_calendar_id.attendance_ids.mapped('dayofweek')
                while(date_from<=date_to):
                    day = str((int(date_from.strftime('%w'))-1)%7)
                    if day not in week_days:
                        total_weekend += 1
                    date_from = date_from + timedelta(days=1)

                shift_lines = resource_calendar_id.attendance_ids
                shift_start = shift_lines[0].hour_from
                shift_end = shift_lines[len(shift_lines)-1].hour_to
                attendace_vals = {
                    'department': employee.department_id.name,
                    'employee_name': employee.name,
                    'employee_id': employee.employee_id,
                    'designation': employee.job_title,
                    'total_days': date_end.day,
                    'total_holiday': total_holiday,
                    'total_weekend': total_weekend,
                    'total_leave': total_leave,
                    'total_office_day': len(intervals),
                    'present': present,
                    'absent': absent,
                    'shift': "{:.2f}AM-{:.2f}PM".format(shift_start,shift_end),
                    'late_check_in': late_check_in,
                    'early_check_out': early_check_out,
                    'month': dict(self._fields['month'].selection).get(str(month)),
                    'year': year,
                    'total_working_time': float("{:.2f}".format(total_working_time)),
                    'average_working_time': float("{:.2f}".format((len(intervals)>0 and (total_working_time / len(intervals)) or 0)))
                }
                self.env['employee.attendance.summary'].create(attendace_vals)

                month += 1
                if month>12:
                    month = month - 12
                    year += 1

                if self.date_type_selection == '26to25':
                    date_end = datetime.strptime('{0}-{1}-25'.format(year,month), '%Y-%m-%d').date()
                    date_start = date_end - relativedelta(months=1)
                    date_start = date_start + relativedelta(days=1)
                else:
                    date_start = datetime.strptime('{0}-{1}-01'.format(year,month), '%Y-%m-%d').date()
                    date_end = date_start + relativedelta(months=1)
                    date_end = date_end - relativedelta(days=1)


                
                print("============")
                print(date_start," == ", date_end)
                month_start += 1

            docids = self.env['employee.attendance.summary'].search([])
            if len(docids)>0:
                _logger.info(docids)
                return self.env.ref('aam_attendance_report.report_hr_attendance_summary_evaluation').report_action(docids)
            else:
                raise UserError("No Data Found")





class employeeattendancesummary(models.TransientModel):
    _name = 'employee.attendance.summary'


    employee_name = fields.Char(string="employee_name")
    employee_id = fields.Char(string="employee_id")
    designation = fields.Char(string="designation")
    department = fields.Char(string="department")
    shift = fields.Char(string="shift")
    late_check_in = fields.Integer(string="late_check_in")
    early_check_out = fields.Integer(string="early_check_out")
    month = fields.Char(string="month")
    year = fields.Char(string="year")
    total_working_time = fields.Float(string="total_working_time")
    average_working_time = fields.Float(string="average_working_time")
    total_days = fields.Integer(string="total_days")
    total_holiday = fields.Integer(string="total_holiday")
    total_leave = fields.Integer(string="total_leave")
    total_weekend = fields.Integer(string="total_weekend")
    total_office_day = fields.Integer(string="total_office_day")
    present = fields.Integer(string="present")
    absent = fields.Integer(string="absent")
