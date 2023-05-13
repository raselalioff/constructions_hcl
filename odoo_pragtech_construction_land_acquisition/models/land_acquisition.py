from odoo import models, fields, api, _
from odoo.exceptions import UserError

class LandAcquisition(models.Model):
    _name = "land.acquisition"
    _description = "Land Acquisition"
    
    image = fields.Binary('Image')
    name = fields.Char('Name')
    ref_name = fields.Char(string='Land Ref Name', required=True)
    area_id = fields.Many2one('areas', 'Area',readonly=True,states={'new_draft': [('readonly', False)]})
    city = fields.Char('City',readonly=True,states={'new_draft': [('readonly', False)]})
    street = fields.Char('Street',readonly=True,states={'new_draft': [('readonly', False)]})
    street2 = fields.Char('Street2',readonly=True,states={'new_draft': [('readonly', False)]})
    township = fields.Char('Township',readonly=True,states={'new_draft': [('readonly', False)]})
    zip = fields.Char('Zip', size=10, change_default=True,readonly=True,states={'new_draft': [('readonly', False)]})
    country_id = fields.Many2one('res.country', 'Country', ondelete='restrict',readonly=True,states={'new_draft': [('readonly', False)]})
    state_id = fields.Many2one("res.country.state", 'states ID', ondelete='restrict',readonly=True,states={'new_draft': [('readonly', False)]})
    latitude = fields.Char('Latitude',readonly=True,states={'new_draft': [('readonly', False)]})
    longitude = fields.Char('Longitude',readonly=True,states={'new_draft': [('readonly', False)]})
    age_of_property = fields.Date('Age of PDate', default=fields.Date.context_today, help='Property Creation Date.',readonly=True,states={'new_draft': [('readonly', False)]})
    video_url = fields.Char('Video URL', help="//www.youtube.com/embed/mwuPTI8AT7M?rel=0",readonly=True,states={'new_draft': [('readonly', False)]})
    currency_id = fields.Many2one('res.currency','Currency',readonly=True,states={'new_draft': [('readonly', False)]})
    website_house = fields.Char('Website',readonly=True,states={'new_draft': [('readonly', False)]})
    start_date = fields.Date('start Date', help='Sale Date of the Property.',readonly=True,states={'new_draft': [('readonly', False)]})
    end_date = fields.Date('End Date',readonly=True,states={'new_draft': [('readonly', False)]})
    is_lease = fields.Boolean('Is Lease',readonly=True,states={'new_draft': [('readonly', False)]})
    lease_cost = fields.Float('Lease Cost',readonly=True,states={'new_draft': [('readonly', False)]})
    is_sale = fields.Boolean('Is Sale',readonly=True,states={'new_draft': [('readonly', False)]})
    sale_cost = fields.Float('Sale Cost',readonly=True,states={'new_draft': [('readonly', False)]})
    parent_id = fields.Many2one('land.acquisition', 'Parent Property',readonly=True,states={'new_draft': [('readonly', False)]})
    type_id = fields.Many2one('property.type', 'Property Type', help='Property Type.',readonly=True,states={'new_draft': [('readonly', False)]})
    income_acc_id = fields.Many2one('account.account', 'Income Account', help='Income Account of Property.',readonly=True,states={'new_draft': [('readonly', False)]})
    unit_price = fields.Float('Unit Price', help='Unit Price Per Sqft.',readonly=True,states={'new_draft': [('readonly', False)]})
    ground_rent = fields.Float('Ground Rent', help='Ground rent of Property.',default=0.0,readonly=True,states={'new_draft': [('readonly', False)]})
    total_price = fields.Float(string='Total Price', help='Total Price of Property, \nTotal Price = Unit Price * GFA (Sqft) .',readonly=True,states={'new_draft': [('readonly', False)]})
    rent_type = fields.Selection([('day', 'Days'), ('week', 'Weeks'), ('month', 'Months'), ('year', 'Year')],
                                'Rent Type', default='day',readonly=True,states={'new_draft': [('readonly', False)]})
    nearby_ids = fields.One2many('nearby.property','acquisition_id','Nearest Property',readonly=True,states={'new_draft': [('readonly', False)]})
    property_photo_ids = fields.One2many('property.photo', 'photo_id', 'Photos',readonly=True,states={'new_draft': [('readonly', False)]})
    property_phase_ids = fields.One2many('property.phase', 'phase_id', 'Phase',readonly=True,states={'new_draft': [('readonly', False)]})
    property_photo_ids = fields.One2many('property.photo', 'photo_id', 'Photos',readonly=True,states={'new_draft': [('readonly', False)]})
    contract_attachment_ids = fields.One2many('property.attachment', 'property_id', 'Document',readonly=True,states={'new_draft': [('readonly', False)]})
    similar_property_ids = fields.Many2many('land.acquisition', 'similar_acquisition_rel', 'acquisition_id', 'acquisition_rel_id', string="Similar Acquisition",readonly=True,states={'new_draft': [('readonly', False)]})
    description = fields.Html('Description',readonly=True,states={'new_draft': [('readonly', False)]})
    msg_static = fields.Text('Msg',readonly=True,states={'new_draft': [('readonly', False)]})
    owner_ids = fields.One2many('res.partner.owners','owner_id','Owners',readonly=True,states={'new_draft': [('readonly', False)]})
    note = fields.Text('Notes' , help='Additional Notes.',readonly=True,states={'new_draft': [('readonly', False)]})
    owner_total = fields.Float(compute='_compute_owner_total',readonly=True,states={'new_draft': [('readonly', False)]})
    state = fields.Selection([('new_draft', 'Booking Open'), ('draft', 'Available'),('book', 'Booked'),('sold', 'Sold'),('cancel', 'Cancel')], 'State',
                            required=True, default='new_draft')
    @api.model
    def default_get(self,default_fields):
        res = super(LandAcquisition, self).default_get(default_fields)
        docs=self.env['document.type'].search([])
        doc_list=[]
        if docs:
            for doc in docs:
                dc=(0,0,{'name':doc.id})
                doc_list.append(dc)
        res['contract_attachment_ids'] =doc_list
        return res
    
    @api.onchange('end_date')
    def onchange_end_date(self):
        for line in self:
            if line.start_date>line.end_date:
                raise UserError(_('Sale Date is greater than as End Date!!')) 
            
    def check_availability(self):
        for record in self:
            if record.is_lease==False and record.is_sale==False:
                raise UserError(_('Please Select At least one from Lease or Sale for this property!!')) 
            record.write({'state':'draft'})
            
    def trans_cancel(self):
        for acquisition in self:
            if acquisition.state and acquisition.state in('book','sold'):
                raise UserError(_('You can not cancel this,because your transaction being processed'))
            acquisition.write({'state':'cancel'}) 
            
    @api.depends('owner_ids','owner_ids.partnership')
    def _compute_owner_total(self):
        for owner in self:
            if owner.owner_ids:
                total=0
                for line in owner.owner_ids:
                    total+=line.partnership
                owner.owner_total = total
                if total>100:
                    raise UserError(_('Please Check Owners Partnership In This Property.'))
            else:
                owner.owner_total = 0
