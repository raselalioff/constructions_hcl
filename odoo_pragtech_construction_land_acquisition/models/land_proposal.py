from odoo import models, fields, api, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta

class LandProposal(models.Model):
    _name = "land.proposal"
    _description = "Land Proposal"
    
    name = fields.Char('Name',default='New')
    acquisition_id = fields.Many2one('land.acquisition','Land Property')
    partner_id = fields.Many2one('res.partner','Customer')
    is_lease = fields.Boolean('Is Lease',related='acquisition_id.is_lease')
    lease_cost = fields.Float('Lease Cost')
    is_sale = fields.Boolean('Is Sale',related='acquisition_id.is_sale')
    sale_cost = fields.Float('Sale Cost')
    rent_type = fields.Selection([('day', 'Days'), ('week', 'Weeks'), ('month', 'Months'), ('year', 'Year')],
                                'Rent Type')
    start_date = fields.Date('Start Date', help='Sale Date of the Property.')
    end_date = fields.Date('End Date')
    state = fields.Selection([('draft', 'Draft'),('book', 'Booked'),('sold', 'Sold'),('cancel', 'Cancel')],'State', required=True, default='draft')
     
    @api.model
    def create(self , vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('land.proposal') or '/'
        return super(LandProposal, self).create(vals)
     
    @api.onchange('acquisition_id')
    def onchange_acqisition(self):
        if self.acquisition_id:
            self.lease_cost=self.acquisition_id.lease_cost
            self.sale_cost= self.acquisition_id.sale_cost
            self.rent_type=self.acquisition_id.rent_type
            self.start_date=self.acquisition_id.start_date
            self.end_date=self.acquisition_id.end_date
            
    def total_qty(self,start_date,end_date,rent_type):    
        new_dict={} 
        if rent_type=='day':
            diff = end_date - start_date
            qty= diff.days 
            new_dict['qty']=qty or '0'
            new_dict['unit']='Day(s)'
        if rent_type=='week':
            diff = end_date - start_date
            qty= diff.days 
            if qty>=7:
                week=qty/7
                new_dict['qty']=round(week) or '0'
            new_dict['unit']='Week(s)'  
        if rent_type=='month':
            months=relativedelta(end_date,start_date).years * 12 + relativedelta(end_date,start_date).months
            if months:
                new_dict['qty']=months or '0'
            new_dict['unit']='Month(s)' 
        if rent_type=='year':
            years=relativedelta(end_date,start_date).years 
            if years:
                new_dict['qty']=years or '0'
            new_dict['unit']='Year(s)'                      
        return  new_dict        
    
    def for_sale(self):
        for proposal in self:
            if proposal.is_sale==False:
                raise UserError(_('Please check this property is available for sale?')) 
            partner = proposal.partner_id
            partner_addr = partner.address_get(['default', 'invoice', 'delivery', 'contact'])
            pricelist = partner.property_product_pricelist.id
            fpos = partner.property_account_position_id and partner.property_account_position_id.id or False
            payment_term = partner.property_payment_term_id and partner.property_payment_term_id.id or False
            new_ids = []
            vals = {
                'origin':proposal.name,
                'team_id': 1,
                'partner_id': partner.id,
                'proposal_id' :proposal.id,
                'acquisition_id':proposal.acquisition_id.id,
                'pricelist_id': pricelist,
                'partner_invoice_id': partner_addr['invoice'],
                'partner_shipping_id': partner_addr['delivery'],
                'date_order': fields.datetime.now(),
                'fiscal_position_id': fpos,
                'payment_term_id':payment_term,
                'is_sale':proposal.is_sale,
                }
            pro_sale_vals = {
                    'proposal_id' :proposal.id,
                    'name' : proposal.name or "" ,
                    'product_uom_qty' : 1,
                    'product_id' : 1,
                    'product_uom' : 1,
                    'price_unit':proposal.sale_cost or 0.0,
                    'is_sale':proposal.is_sale,
                    }
            vals.update({'order_line': [(0, 0, pro_sale_vals)]})
            new_id = self.env['sale.order'].create(vals)

            proposal.write({'state':'sold'})
#             proposal.acquisition_id.write({'state':'sold'})
            new_ids.append(new_id.id)

            if not new_ids:
                return {'type': 'ir.actions.act_window_close'}

            if len(new_ids)<=1:
                value = {
                    'domain': str([('id', 'in', new_ids)]),
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'sale.order',
                    'view_id': False,
                    'type': 'ir.actions.act_window',
                    'name' : _('Quotation'),
                    'res_id': new_ids and new_ids[0]
                }
            else:
                value = {
                    'domain': str([('id', 'in', new_ids)]),
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'res_model': 'sale.order',
                    'view_id': False,
                    'type': 'ir.actions.act_window',
                    'name' : _('Quotation'),
                    'res_id': new_ids
                }

            return value
        return True
     
    def for_lease(self):
        for proposal in self:
            if proposal.is_lease==False:
                raise UserError(_('Please check this property is available for lease?'))
            partner = proposal.partner_id
            partner_addr = partner.address_get(['default', 'invoice', 'delivery', 'contact'])
            pricelist = partner.property_product_pricelist.id
            fpos = partner.property_account_position_id and partner.property_account_position_id.id or False
            payment_term = partner.property_payment_term_id and partner.property_payment_term_id.id or False
            new_ids = []
            vals = {
                'origin':proposal.name,
                'proposal_id' :proposal.id,
                'acquisition_id':proposal.acquisition_id.id,
                'team_id': 1,
                'partner_id': partner.id,
                'pricelist_id': pricelist,
                'partner_invoice_id': partner_addr['invoice'],
                'partner_shipping_id': partner_addr['delivery'],
                'date_order': fields.datetime.now(),
                'fiscal_position_id': fpos,
                'payment_term_id':payment_term,
                'is_lease':proposal.is_lease,
                }
            new_dict=self.total_qty(proposal.start_date,proposal.end_date,proposal.rent_type)
            if new_dict.get('unit'):
                unit=new_dict.get('unit')
            if new_dict.get('qty'):
                qty=new_dict.get('qty')
            pro_sale_vals = {
                    'proposal_id' :proposal.id,
                    'name' : proposal.name or "" ,
                    'product_uom_qty' : qty or "",
                    'product_id' : 1,
                    'product_uom' : 1,
                    'unit':unit,
                    'price_unit':proposal.lease_cost or 0.0,
                    'from_date':proposal.start_date,
                    'to_date':proposal.end_date,
                    'is_lease':proposal.is_lease,
                    }
            vals.update({'order_line': [(0, 0, pro_sale_vals)]})
            new_id = self.env['sale.order'].create(vals)
            proposal.write({'state':'book'})
#             proposal.acquisition_id.write({'state':'book'})
            new_ids.append(new_id.id)
            if not new_ids:
                return {'type': 'ir.actions.act_window_close'}
            if len(new_ids)<=1:
                value = {
                    'domain': str([('id', 'in', new_ids)]),
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'sale.order',
                    'view_id': False,
                    'type': 'ir.actions.act_window',
                    'name' : _('Quotation'),
                    'res_id': new_ids and new_ids[0]
                }
            else:
                value = {
                    'domain': str([('id', 'in', new_ids)]),
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'res_model': 'sale.order',
                    'view_id': False,
                    'type': 'ir.actions.act_window',
                    'name' : _('Quotation'),
                    'res_id': new_ids
                }
            return value
        return True 
    
    def trans_cancel(self):
        for proposal in self:
#             sale_order=self.env['sale.order'].search([('proposal_id','=',proposal.id)])
#             if sale_order and sale_order[0].state=='draft':
#                 sale_order.action_cancel()
#                 proposal.write({'state':'cancel'})
#             if sale_order and sale_order[0].state not in ('draft','cancel'):
#                 raise UserError(_('You can not cancel this,because your transaction being processed'))
#             else:
            proposal.write({'state':'cancel'})
