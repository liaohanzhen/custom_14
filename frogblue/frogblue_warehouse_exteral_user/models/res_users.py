from odoo import api, fields, models


class Users(models.Model):
    _inherit = 'res.users'
    
    warehouse_ids = fields.Many2many('stock.warehouse', 'user_warehouse_rel', 'user_id', 'warehouse_id', string='Allowed Warehouse', help='Select Warehouse From This User')
    

class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'
    
    @api.model
    def create(self, values):
        self.env['ir.ui.menu'].clear_caches()
        return super(IrUiMenu, self).create(values)

    def write(self, values):
        self.env['ir.ui.menu'].clear_caches()
        return super(IrUiMenu, self).write(values)
    
    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        if self.env.user == self.env.ref('base.user_root'):
            return super(IrUiMenu, self).search(args, offset=0, limit=None, order=order, count=False)
        else:
            menus = super(IrUiMenu, self).search(args, offset=0, limit=None, order=order, count=False)
            if menus:
                menus_list = self.browse()
                if self.env.user.has_group('frogblue_warehouse_exteral_user.warehouse_exteral_user'):
                    stock_menu = self.env.ref('stock.menu_stock_root')
                    stock_menus = super(IrUiMenu, self).search([('parent_id', 'child_of', stock_menu.id)], offset=0, limit=None, order=order, count=False)
                    barcode_menu = self.env.ref('stock_barcode.stock_barcode_menu') 
                    menus_list = barcode_menu + stock_menus
                    
                    for menu in menus:
                        if not menu in menus_list:
                            menus -= menu
                        
                if offset:
                    menus = menus[offset:]
                if limit:
                    menus = menus[:limit]
            return len(menus) if count else menus
