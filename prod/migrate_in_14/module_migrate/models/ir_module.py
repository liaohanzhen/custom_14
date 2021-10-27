
from odoo import models, fields, api

class IrModuleModule(models.Model):
    _inherit='ir.module.module'
    
    to_migrate_to_14 = fields.Boolean('To migrate to 14', copy=False)
    
#     @api.multi
    def write(self, vals):
        res = super(IrModuleModule, self).write(vals)
        if 'to_migrate_to_14' in vals:
            for record in self:
                depends = record.downstream_dependencies()
                super(IrModuleModule, depends).write({'to_migrate_to_14' : record.to_migrate_to_14})
        return res