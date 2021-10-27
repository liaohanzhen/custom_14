from odoo import models, fields
from dateutil.relativedelta import relativedelta

class CrearAdendumWizard(models.TransientModel):
    _name = 'crear.adendum.wizard'
    
    meses_adicionales = fields.Float('Meses adicionales')
    
    def confirm_crear_addedum(self):
        adendum_doc = self.env['adendum.adendum']
        active_ids = self._context.get('active_ids')
        active_model = self._context.get('active_model','')
        if active_model=='contract.contract':
            for rec in self.env['contract.contract'].browse(active_ids):
                date_end = rec.date_end
                date_final = None
                if date_end and self.meses_adicionales:
                    date_final = date_end + relativedelta(months=int(self.meses_adicionales))
                    
                vals = {'name': rec.name,
                        'partner_id': rec.partner_id.id,
                        'fecha_inicial': date_end,
                        'fecha_final': date_final,
                        'adendum_origen': rec.id,
                        'no_meses' : self.meses_adicionales,
                        'no_adendum' : rec.adendum_count_2,
                        }
                #rec.write({'date_end':date_final})
                adendum_doc.create(vals)
        return
    