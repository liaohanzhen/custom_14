from odoo import models, fields, _


class import_order(models.TransientModel):
    _name = 'import.order'
    _description = 'Import Order Wizard'

    order_id = fields.Many2one('sale.order', 'Sale Order')
    item_ids = fields.One2many('import.order.line', 'import_order_id', 'Items')
    invalid_code_ids = fields.Text('Invalid codes')

    def default_get(self, fields):
        res = super(import_order, self).default_get(fields)
        res['order_id'] = self._context.get('order_id', False)
        res['item_ids'] = self._context.get('item_ids', False)
        res['invalid_code_ids'] = self._context.get('item_ids', False)
        return res

    def wizard_view(self):
        view = self.env.ref('import_order_xls.view_order_import_wizard')

        return {
            'name': _('Order details'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'import.order',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': self.ids[0],
            'context': self.env.context,
        }

    def process_import(self, mode):
        items = self.item_ids
        order = self.order_id
        for item in items:
            line_id = item.line_id
            res = {}
            # res = self.env['sale.order.line']
            # res = self.env['sale.order.line'].product_id_change()
            res.update({'name': item.product_id.name})
            res.update({'invoice_status': 'upselling'})
            res.update({'price_unit': item.product_id.list_price})
            res.update({'product_uom': item.product_uom_id.id})

            tax_id = res.get('tax_id', False)
            if tax_id:
                res.update({'tax_id': [(6, 0, tax_id)]})

            if item.price:
                res.update({'price_unit': item.price, 'discount': item.discount or 0, })

            res.update({
                'product_id': item.product_id.id,
                'order_id': self.order_id.id,
                'product_uom_qty': item.quantity,
            })
            # res.pop('domain')
            if item.description:
                res.update({'name': item.description, })

            if mode == 'w':
                line_id.write(res)
            else:
                line_id = self.env['sale.order.line'].create(res)
        order.write({})
        return True

    def do_append(self):
        '''Append order items'''
        self.process_import(mode='c')
        return {'type': 'ir.actions.act_window_close'}

    def do_update(self):
        '''Update existing items'''
        self.process_import(mode='w')
        return {'type': 'ir.actions.act_window_close'}


class import_order_line(models.TransientModel):
    _name = 'import.order.line'
    _description = 'Import Order Items'

    import_order_id = fields.Many2one('import.order', 'Order')
    line_id = fields.Many2one('sale.order.line', 'Order Line')
    order_id = fields.Many2one('sale.order')
    description = fields.Char('Description')
    product_id = fields.Many2one('product.product', 'Product')
    product_name = fields.Char('Name')
    product_uom_id = fields.Many2one('product.uom', 'Unit of Measure')
    quantity = fields.Float('Quantity', digits='Product Unit of Measure', default=1.0)
    price = fields.Float('Price', digits='Product Unit of Measure', default=0.0)
    discount = fields.Float('Discount', digits='Product Unit of Measure', default=0.0)
