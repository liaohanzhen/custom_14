# -*- coding: utf-8 -*-

from odoo import models, fields, api

class CustomerSegment(models.Model):
    _name = 'customer.segment'
    
    name = fields.Char("Name", required="1")
    
     
class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model    
    def create(self, vals):
        if self._context.get('is_from_crm') and self._context.get('default_parent_id'):
            ctx = self._context.copy()
            vals['parent_id'] = ctx.pop('default_parent_id')
            self = self.with_context(ctx)
        return super(ResPartner, self).create(vals)
        
    
    @api.depends('product_acceptability','offer_and_demand_compatibility', 'relationship_status','relationship_quality', 'average_project_size','total_pipeline_size')
    def _client_rating_count(self):
        for partner in self:
            count = 0
            if partner.product_acceptability:
                count += 20 *int(partner.product_acceptability)/10.0
            if partner.offer_and_demand_compatibility:
                count +=15 * int(partner.offer_and_demand_compatibility)/10.0
            if partner.relationship_status:
                count +=15 * int(partner.relationship_status)/10.0
            if partner.relationship_quality:
                count +=15 * int(partner.relationship_quality)/10.0
            if partner.average_project_size:
                count +=20*int(partner.average_project_size)/10.0
            if partner.total_pipeline_size:
                count +=15 * int(partner.total_pipeline_size)/10.0    
            partner.client_rating_count = str(count)+'%'
    
    @api.depends('product_acceptability')
    def _compute_percentage_product_acceptability(self):
        for partner in self:
            #partner.percentage_product_acceptability = '[Ranking : %s/10.0 @20 % = '%(partner.product_acceptability)+str(20 *int(partner.product_acceptability)/10.0)+'%]'
            if partner.product_acceptability:
                partner.percentage_product_acceptability = ' [Ranking : '+partner.product_acceptability+'/10.0 @20 % = '+str(20 *int(partner.product_acceptability)/10.0)+'%]'
    
    @api.depends('offer_and_demand_compatibility')
    def _compute_percentage_offer_and_demand_compatibility(self):
        for partner in self:
            #partner.percentage_offer_and_demand_compatibility = str(15 *int(partner.offer_and_demand_compatibility)/10.0)+'%'
            if partner.offer_and_demand_compatibility:
                partner.percentage_offer_and_demand_compatibility = ' [Ranking : '+partner.offer_and_demand_compatibility+'/10.0 @15 % = '+str(15 *int(partner.offer_and_demand_compatibility)/10.0)+'%]'
            
    @api.depends('relationship_status')
    def _compute_percentage_relationship_status(self):
        for partner in self:
            #partner.percentage_relationship_status = str(15 *int(partner.relationship_status)/10.0)+'%'
            if partner.relationship_status:
                partner.percentage_relationship_status = ' [Ranking : '+partner.relationship_status+'/10.0 @15 % = '+str(15 *int(partner.relationship_status)/10.0)+'%]'

    @api.depends('relationship_quality')
    def _compute_percentage_relationship_quality(self):
        for partner in self:
            #partner.percentage_relationship_quality = str(15 *int(partner.relationship_quality)/10.0)+'%'
            if partner.relationship_quality:
                partner.percentage_relationship_quality = ' [Ranking : '+partner.relationship_quality+'/10.0 @15 % = '+str(15 *int(partner.relationship_quality)/10.0)+'%]'

    @api.depends('average_project_size')
    def _compute_percentage_average_project_size(self):
        for partner in self:
            #partner.percentage_average_project_size = str(20 *int(partner.average_project_size)/10.0)+'%'
            if partner.average_project_size:
                partner.percentage_average_project_size = ' [Ranking : '+partner.average_project_size+'/10.0 @20 % = '+str(20 *int(partner.average_project_size)/10.0)+'%]'
            
    @api.depends('total_pipeline_size')
    def _compute_percentage_total_pipeline_size(self):
        for partner in self:
            #partner.percentage_total_pipeline_size = str(15 *int(partner.total_pipeline_size)/10.0)+'%'
            if partner.total_pipeline_size:
                partner.percentage_total_pipeline_size = ' [Ranking : '+partner.total_pipeline_size+'/10.0 @15 % = '+str(15 *int(partner.total_pipeline_size)/10.0)+'%]'
            
    client_rating_count = fields.Char(compute="_client_rating_count",string="Client Rating Count", store=True)
    key_account_partner = fields.Boolean("Key Account/Strategic Partner")
    fax = fields.Char("Fax")
    customer_segment_ids = fields.Many2many("customer.segment",'customer_segment_partner_rel','partner_id','segment_id',string="Customer Segment")
    
    percentage_product_acceptability = fields.Char("Product acceptability %",compute="_compute_percentage_product_acceptability",store=True)
    percentage_offer_and_demand_compatibility = fields.Char("offer & demand compa. %",compute="_compute_percentage_offer_and_demand_compatibility",store=True)
    percentage_relationship_status = fields.Char("Relationship status %",compute="_compute_percentage_relationship_status",store=True)
    percentage_relationship_quality = fields.Char("Relationship quality %",compute="_compute_percentage_relationship_quality",store=True)
    percentage_average_project_size = fields.Char("Average project size %",compute="_compute_percentage_average_project_size",store=True)
    percentage_total_pipeline_size = fields.Char("Total pipeline size %",compute="_compute_percentage_total_pipeline_size",store=True)
    
    product_acceptability = fields.Selection([('10','Has already bought'),('8','High'),('6','Good'),('4','Average'),('2','Low'),('0','Will never buy')],string='Product/solution acceptability')
    offer_and_demand_compatibility = fields.Selection([('10','Totally compatible : no issue with demand satisfaction'),
                                                       ('8','High compatibility : demand can be easily satisfy'),
                                                       ('6','Good compatibility : some efforts to meet demand'),
                                                       ('4','Average compatibility : large efforts to meet demande'),
                                                       ('2','Low compatibility : unlikely to lead to opportunities'),
                                                       ('0','Not compatible at all')],string='Offer & demand compatibility')
    
    relationship_status = fields.Selection([('10','Projects in common'),
                                            ('8','All decision makers met and great exchanges'),
                                            ('6','Strong contact, several meetings'),
                                            ('4','First contact and quotation'),
                                            ('2','First contact without quotations'),
                                            ('0','No contact')],string='Relationship status')
    
    relationship_quality =fields.Selection([('10','Great relationship :  mutual trust,  common strategy, asks for advices'),
                                            ('8','Very good relationship : regular meetings, will for common development, advisor of our solution'),
                                            ('6','Good relation : really interested by our solution, common work on projects and good feeling'),
                                            ('4','Average relationship : common work on some projects, few calls and average feeling'),
                                            ('2','Never contacted'),
                                            ('0','Bad relationship : important issues or blacklisting')], 
                                           string='Relationship quality')
    
    average_project_size = fields.Selection([('10','More than 20 MWp'),
                                             ('8','5 - 20 MWp'),
                                             ('6','2 - 5 MWp'),
                                             ('4','500 kWp - 2 MWp'),
                                             ('2','100 - 500 kWp'),
                                             ('0','0 - 100 kWp')], string='Average project size')

    total_pipeline_size = fields.Selection([('10','More than 20 MWp'),
                                            ('8','5 - 20 MWp'),
                                            ('6','2 - 5 MWp'),
                                            ('4','500 kWp - 2 MWp'),
                                            ('2','100 - 500 kWp'),
                                            ('0','0 - 100 kWp')], string='Total pipeline size')

    def customer_rating_count(self):
        return True
    
    #To not force send mail immediately.
    @api.model
    def _notify(self, message, rdata, record, force_send=False, send_after_commit=True, model_description=False, mail_auto_delete=True):
        return super(ResPartner, self)._notify(message, rdata,record, False, send_after_commit=send_after_commit, model_description=model_description, mail_auto_delete=mail_auto_delete)
    

#     def _notify(self, message, force_send=False, send_after_commit=True, user_signature=True):
#         return super(ResPartner, self)._notify(message, False, send_after_commit=send_after_commit, user_signature=user_signature)
