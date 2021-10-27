# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import Warning

class QualityPoint(models.Model):
    _inherit = "quality.point"
    
    quality_check_percent = fields.Float("Quality Check %")
    source_location_ids = fields.Many2many("stock.location",'quality_point_stock_location_source_rel','point_id','location_id',"Source Locations")
    dest_location_ids = fields.Many2many("stock.location",'quality_point_stock_location_destination_rel','point_id','location_id',"Destination Locations")
    
    @api.constrains("quality_check_percent")
    def _check_quality_check_percent(self):
        if self.quality_check_percent > 100 or self.quality_check_percent < 0:
            raise Warning("Quality Check percentage must be between 0 to 100")
    
    def check_execute_now(self):
        self.ensure_one()
        if self.measure_frequency_type == 'all' and self.quality_check_percent:
            
            return True
        return super(QualityPoint, self).check_execute_now()