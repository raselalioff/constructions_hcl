from odoo import fields, models, api
import datetime, time
from datetime import timedelta, date, datetime
from pytz import timezone
import pytz
from odoo.tools import format_datetime

class InheritedHrAttendance(models.Model):
    _inherit = "hr.attendance"

    late_checkin_min = fields.Integer(string='Late Check-In', compute='_compute_late_checkin_min', store=True)
    early_checkout_min = fields.Integer(string='Early Check-Out', compute='_compute_early_checkout_min',
                                        store=True)

    attendance_date = fields.Date(string='Attendance Date', compute='_compute_attendance_date',
                                  store=True)

    less_worked_hours = fields.Float("Less Worked Hours", compute='_compute_less_worked_hours',
                                     store=True)

    @api.depends('check_in')
    def _compute_attendance_date(self):
        for attendance in self:
            if attendance.check_in:
                attendance.attendance_date = attendance.check_in.date()

    @api.depends('check_in')
    def _compute_late_checkin_min(self):
        for attendance in self:
            if attendance.check_in:
                # getting attendance date
                attendance_date = attendance.check_in.date()
                attendance_day = datetime.strptime(str(attendance_date), '%Y-%m-%d').strftime('%a').upper()
                # employee_id = attendance.employee_id
                # ---------- for dynamic hour
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
                # from_hour_e = 0
                to_hour_s = 0
                # to_hour_e = 0
                employee_att_days = attendance.employee_id.resource_calendar_id.attendance_ids.filtered(
                    lambda line: line.dayofweek == day_no)
                for rec in employee_att_days:
                    hour_from = rec.hour_from
                    # hour_to = rec.hour_to
                    day_period = rec.day_period
                    if day_period == 'morning':
                        from_hour_s = hour_from
                        # from_hour_e = hour_to
                    elif day_period == 'afternoon':
                        to_hour_s = hour_from
                        # to_hour_e = hour_to
                if from_hour_s == 0:
                    from_hour_s = to_hour_s
                #                 if to_hour_e == 0:
                #                     to_hour_e = from_hour_e

                att_dt = attendance_date.strftime('%Y-%m-%d %H:%M:%S')
                start_time = datetime.strptime(att_dt, '%Y-%m-%d %H:%M:%S') + timedelta(
                    hours=from_hour_s) - timedelta(hours=6)

                late_checkin_min = 0

                if start_time < attendance.check_in:
                    late_checkin_time = attendance.check_in - start_time
                    late_checkin_second = late_checkin_time.seconds
                    late_checkin_min = late_checkin_second / 60

                attendance.late_checkin_min = int(late_checkin_min)

    @api.depends('check_out')
    def _compute_early_checkout_min(self):
        for attendance in self:
            if attendance.check_out:
                attendance_date = attendance.check_out.date()
                attendance_day = datetime.strptime(str(attendance_date), '%Y-%m-%d').strftime('%a').upper()
                # employee_id = attendance.employee_id
                # ---------- for dynamic hour
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

                # from_hour_s = 0
                from_hour_e = 0
                # to_hour_s = 0
                to_hour_e = 0
                employee_att_days = attendance.employee_id.resource_calendar_id.attendance_ids.filtered(
                    lambda line: line.dayofweek == day_no)
                for rec in employee_att_days:
                    # hour_from = rec.hour_from
                    hour_to = rec.hour_to
                    day_period = rec.day_period
                    if day_period == 'morning':
                        # from_hour_s = hour_from
                        from_hour_e = hour_to
                    elif day_period == 'afternoon':
                        # to_hour_s = hour_from
                        to_hour_e = hour_to
                #                 if from_hour_s == 0:
                #                     from_hour_s = to_hour_s
                if to_hour_e == 0:
                    to_hour_e = from_hour_e

                att_dt = attendance_date.strftime('%Y-%m-%d %H:%M:%S')
                end_time = datetime.strptime(att_dt, '%Y-%m-%d %H:%M:%S') + timedelta(
                    hours=to_hour_e) - timedelta(hours=6)

                early_checkout_min = 0

                # end_time_2 = str(attendance.check_out)[0:10] + ' 13:00:00'  # 7pm
                # end_time = datetime.strptime(end_time_2, '%Y-%m-%d %H:%M:%S')
                if end_time > attendance.check_out:
                    early_checkout_time = end_time - attendance.check_out
                    early_checkout_second = early_checkout_time.seconds
                    early_checkout_min = early_checkout_second / 60
                attendance.early_checkout_min = int(early_checkout_min)

    @api.depends('worked_hours')
    def _compute_less_worked_hours(self):
        for attendance in self:
            if attendance.worked_hours and attendance.check_in and attendance.check_out:

                hours_per_day = attendance.employee_id.resource_calendar_id.hours_per_day
                attendance.less_worked_hours = hours_per_day - attendance.worked_hours


    @api.model
    def auto_update_attendance_record(self):

        today = fields.Datetime.now()
        attendances = self.env['hr.attendance'].search([('check_in','!=',False),('check_out','=',False)])
        for attendance in attendances:
            shift_lines = attendance.employee_id.resource_calendar_id.attendance_ids.filtered(lambda x: x.dayofweek=='0')
            shift_end = shift_lines[len(shift_lines)-1].hour_to

            close_time = "{:.2f}".format(shift_end) 
            time_zone = timezone(attendance.employee_id.resource_calendar_id.tz)
            local_check_in = pytz.utc.localize(datetime.strptime(str(attendance.check_in), "%Y-%m-%d %H:%M:%S")).astimezone(time_zone)
            checkout_time = local_check_in.strftime('%Y-%m-%d {}:{}:00'.format(close_time[:2],close_time[3:5]))
            
            naive = datetime.strptime(str(checkout_time), "%Y-%m-%d %H:%M:%S")
            local_dt = time_zone.localize(naive, is_dst=None)
            checkout_time = local_dt.astimezone(pytz.utc)
            checkout_time = checkout_time.replace(tzinfo=None)
            attendance.write({'check_out':checkout_time})
        pass
