# -*- coding: utf-8 -*-
from odoo import models, fields, api,_
import logging
_logger = logging.getLogger(__name__)

class AgregarProducto(models.TransientModel):
    _name = "agregar.producto"
    
    product_tmp_id = fields.Many2one('product.template',string="Unidad a rentar")
    unidades_producto  = fields.Float(string="Cantidad de unidades de producto", default=1)
    date_to = fields.Datetime(string="Date")
    date_from = fields.Datetime()
    rental = fields.Float(string="Renta")
    p_proteccion = fields.Float(string="P. proteccion")
    instalacion = fields.Float(string="Instalacion")
    kms = fields.Float(string="Kms")
    costo = fields.Float(string="Costo x Km")
    subtotal = fields.Float(string="Subtotal flete")
    escaleras = fields.Float(string="Escaleras")
    costo2 = fields.Float(string="Costo escalera")
    subtotal2 = fields.Float(string="Subtotal escalera")
    torres = fields.Float(string="Torres")
    costo3 = fields.Float(string="Costo torre")
    subtotal3 = fields.Float(string="Subtotal torres")
    total_producto = fields.Float(string="Total",readonly="1")
    tiempo_de_renta = fields.Selection( selection=[('menor', 'Menor a 6 meses'), 
                   ('mayor', 'Mayor a 6 meses'),],
        string=_('Tipo de contrato'),)

    ciudad_destino = fields.Char(string="Ciudad destino")


    @api.onchange('product_tmp_id', 'tiempo_de_renta', 'unidades_producto')
    def update_rental(self):
        ctx= self._context or {}
        product_tmp = self.product_tmp_id

        if ctx.get('active_id') and ctx.get('active_model','')=='sale.order' and product_tmp:
            order = self.env['sale.order'].browse(ctx.get('active_id'))
            pricelist = order.pricelist_id
            items = pricelist.item_ids.filtered(lambda x:x.product_tmpl_id.id==product_tmp.id)
            if self.tiempo_de_renta == 'mayor' and items and items[0].rental_price > 0:
                self.rental = (items[0].rental_price - (items[0].rental_price * 10 / 100) ) * self.unidades_producto
            else:
                self.rental = items and items[0].rental_price  * self.unidades_producto

        self.p_proteccion = self.rental * 0.03 #* self.unidades_producto

        if self.product_tmp_id:
            self.costo = self.product_tmp_id.costo_km


    #COSTO DE INSTALACIÓN IGUAL A CAMPO DE KM EN PRODUCTO
    @api.onchange('product_tmp_id', 'unidades_producto')
    def instalacion_chang(self):
        self.instalacion = self.product_tmp_id.costo_instalacion * self.unidades_producto


    @api.onchange('rental','p_proteccion','instalacion','subtotal','subtotal2','subtotal3')
    def sum_totals(self):
        self.total_producto = self.rental + self.p_proteccion + self.instalacion + self.subtotal + self.subtotal2 + self.subtotal3

    @api.onchange('kms', 'costo', 'unidades_producto')
    def kms_cost_calculation(self):
        self.subtotal = self.kms * self.product_tmp_id.costo_km * self.unidades_producto

    @api.onchange('escaleras', 'costo2')
    def escalera_cost_calculation(self):
        self.subtotal2 = self.escaleras * self.costo2

    @api.onchange('torres', 'costo3')
    def torres_cost_calculation(self):
        self.subtotal3 = self.torres * self.costo3

    def actualizar(self):
        model = self._context.get('active_model', False)
        active_ids = self._context.get('active_ids', False)
        sale_order = self.env[model].browse(active_ids)
         
        sale_order.update({'kms':self.kms,'ciudad_destino': self.ciudad_destino})



        if sale_order:
            vals = {'order_id': sale_order.id,
                'display_type': 'line_section',
                'name':self.product_tmp_id.name}
            sale_order.order_line.create(vals)
            #change_order_status = False

            stng_product_tmp_id = self.env['ir.config_parameter'].sudo().get_param('structurall_module.product_tmp_id')
            stng_product_tmp_id2 = self.env['ir.config_parameter'].sudo().get_param('structurall_module.product_tmp_id2')
            stng_product_tmp_id3 = self.env['ir.config_parameter'].sudo().get_param('structurall_module.product_tmp_id3')
            product_pricelist = sale_order.pricelist_id
            price = self.product_tmp_id.product_variant_id.with_context({'pricelist':product_pricelist.id}).price
            tax_id = self.product_tmp_id.product_variant_id.with_context({'taxes_id':product_pricelist.id}).taxes_id
            vals = {'order_id': sale_order.id,
                    'product_id': self.product_tmp_id.product_variant_id.id,
                    #'name': str(self.product_tmp_id.name) + ' - Km:' + str(self.kms) + ' - Ciudad destino:' + str(self.ciudad_destino),
                    'product_uom_qty': self.unidades_producto,
                    'price_unit': self.rental / self.unidades_producto,
                    'tax_id': tax_id.ids,
                    'pickup_date': self.date_from,
                    'return_date': self.date_to}
            sale_order.order_line.create(vals)
            #if self.product_tmp_id.product_variant_id.with_context(warehouse=sale_order.warehouse_id.id).qty_available <= 0:
            #    change_order_status = True

            if stng_product_tmp_id2:
                stng_product_tmp_id2 = self.env['product.template'].browse(int(stng_product_tmp_id2))
                price = stng_product_tmp_id2.product_variant_id.with_context({'pricelist':product_pricelist.id}).price
                tax_id = stng_product_tmp_id2.product_variant_id.with_context({'taxes_id':product_pricelist.id}).taxes_id
                vals = {'order_id': sale_order.id,
                    'product_id': stng_product_tmp_id2.product_variant_id.id,
                    'name': str(stng_product_tmp_id2.product_variant_id.name),
                    'price_unit': self.p_proteccion / self.unidades_producto,
                    'product_uom_qty': self.unidades_producto,
                    'tax_id': tax_id.ids,
                    'pickup_date': self.date_from,
                    'return_date': self.date_to}
                sale_order.order_line.create(vals)
                #if stng_product_tmp_id2.product_variant_id.with_context(warehouse=sale_order.warehouse_id.id).qty_available <= 0:
                #    change_order_status = True

            if stng_product_tmp_id:
                stng_product_tmp_id = self.env['product.template'].browse(int(stng_product_tmp_id))
                price = stng_product_tmp_id.product_variant_id.with_context({'pricelist':product_pricelist.id}).price
                tax_id = stng_product_tmp_id.product_variant_id.with_context({'taxes_id':product_pricelist.id}).taxes_id
                vals = {'order_id': sale_order.id,
                    'product_id': stng_product_tmp_id.product_variant_id.id,
                    'price_unit': (self.subtotal + self.instalacion) / self.unidades_producto,
                    'product_uom_qty': self.unidades_producto,
                    'name': str(stng_product_tmp_id.product_variant_id.name),
                    'tax_id': tax_id.ids,
                    'pickup_date': self.date_from,
                    'return_date': self.date_to}
                sale_order.order_line.create(vals)
                #if stng_product_tmp_id.product_variant_id.with_context(warehouse=sale_order.warehouse_id.id).qty_available <= 0:
                #    change_order_status = True

            if stng_product_tmp_id3:
                stng_product_tmp_id3 = self.env['product.template'].browse(int(stng_product_tmp_id3))
                price = stng_product_tmp_id3.product_variant_id.with_context({'pricelist':product_pricelist.id}).price
                tax_id = stng_product_tmp_id3.product_variant_id.with_context({'taxes_id':product_pricelist.id}).taxes_id
                vals = {'order_id': sale_order.id,
                    'product_id': stng_product_tmp_id3.product_variant_id.id,
                    'price_unit': ((self.rental + self.p_proteccion) * 1.16) / self.unidades_producto,
                    'product_uom_qty': self.unidades_producto,
                    'tax_id': tax_id.ids,
                    'pickup_date': self.date_from,
                    'return_date': self.date_to}
                sale_order.order_line.create(vals)
                #if stng_product_tmp_id3.product_variant_id.with_context(warehouse=sale_order.warehouse_id.id).qty_available <= 0:
                #    change_order_status = True

            #if change_order_status:
            #    sale_order.write({'state':'autorizacion'})

