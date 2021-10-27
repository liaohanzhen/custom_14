from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)


class RentalOrderLine(models.Model):
    _inherit = 'sale.order.line'

    check_stock_so = fields.Boolean(string="Stock en lineas", compute="check_stock_so_lines")
    ubicacion_exacta = fields.Char(string="Ubicación exacta")

    def check_stock_so_lines(self):
        for l in self:
            if l.product_id.qty_available == 0:
                l.check_stock_so == True
            else:
                l.check_stock_so == True

    def set_editar_precios(self):
        self.editar_precios = self.env['res.users'].has_group('structurall_module.groups_restrict_price_change')

    editar_precios = fields.Boolean(compute=set_editar_precios, string='Editar precios')

    def set_editar_descuentos(self):
        self.editar_descuentos = self.env['res.users'].has_group('structurall_module.editar_descuentos_group')

    editar_descuentos = fields.Boolean(compute=set_editar_descuentos, string='Editar Descuentos')

    @api.constrains('discount')
    def _check_discount(self):
        editar_descuentos = self.env['res.users'].has_group('structurall_module.editar_descuentos_group')
        res_config = self.env['res.config.settings'].sudo().search([], order='id desc', limit=1)
        descuento_maximo = res_config.descuento_maximo or False
        if editar_descuentos == True and descuento_maximo:
            for line in self:
                if line.discount > descuento_maximo:
                    raise ValidationError(_('Ingresa un descuento menor a ' + str(descuento_maximo)))


class RentalOrder(models.Model):
    _inherit = 'sale.order'

    contract_related_count = fields.Integer(string="Contrato", compute="_get_contratcts")
    contract_related = fields.Many2many("contract.contract", string='Contratos', compute="_get_contratcts",
                                        readonly=True, copy=False)
    estado_instalacion = fields.Many2one('res.country.state', string="Estado de instalación")

    # Campos KM y ciudad desde el wizard
    ciudad_destino = fields.Char(string="Ciudad destino")
    kms = fields.Float(string="Kms")

    # Campos Acta constitutiva
    nombre_representante_ac = fields.Char(string="Nombre del representante legal")
    testimonio_notarial_ac = fields.Char(string="Testimonio notarial")
    fecha_ac = fields.Date(string="Fecha")
    notaria_ac = fields.Char(string="Notaria")
    nombre_notario_ac = fields.Char(string="Nombre del notario")
    domicilio_ac = fields.Char(string="Domicilio")

    # Campos Poder notarial
    nombre_representante_pn = fields.Char(string="Nombre del representante legal")
    testimonio_notarial_pn = fields.Char(string="Testimonio notarial")
    fecha_pn = fields.Date(string="Fecha")
    notaria_pn = fields.Char(string="Notaria")
    nombre_notario_pn = fields.Char(string="Nombre del notario")
    domicilio_pn = fields.Char(string="Domicilio")

    @api.onchange('estado_instalacion')
    def set_pricelist(self):
        if self.estado_instalacion:
            pricelist = self.env['product.pricelist'].search([('estados', '=', self.estado_instalacion.id)],
                                                             order='id asc', limit=1)
            if pricelist:
                self.pricelist_id = pricelist.id

    #  def get_contract_related_count(self):
    #      count = self.env['contract.contract'].sudo().search_count([('name', '=', self.name)])
    #      self.contract_related_count = count

    def _get_contratcts(self):
        for order in self:
            contracts = self.env['contract.contract'].sudo().search([]).filtered(lambda r: r.so_rentals)
            contracts2 = contracts.filtered(lambda r: order.name in r.so_rentals)
            order.contract_related = contracts2
            order.contract_related_count = len(contracts2)

    def agregar_unidad(self):
        view = self.env.ref('structurall_module.agregar_unidad_wizard')
        ctx = self.env.context.copy()

        return {
            'name': 'Agregar Unidad',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'agregar.producto',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'context': ctx,
        }

    def action_crear_contrato(self):
        contract_order = self.env['contract.contract']
        contract_order_line_obj = self.env['contract.line']
        for rec in self:
            line_vals = []
            # Values for the first time invoice One2many
            primera_vals = []
            customer = rec.partner_id
            price_list = rec.pricelist_id
            order_lines = rec.order_line

            if rec.is_rental_order == True:
                contract_type = 'Renta'
            else:
                contract_type = 'Financiamiento'
            deposito_garantia = 0

            for line in order_lines:
                if line.name.lower().find('deposito') and line.name.lower().find('depósito') == -1:
                    if line.product_id.rent_ok == True and line.product_id.tracking == 'serial':
                        numero_series = []
                        for picking in self.picking_ids:
                            if picking.state == 'done':
                                for stock_line in picking.move_line_ids_without_package:
                                    if line.product_id.id == stock_line.product_id.id:
                                        numero_series += stock_line.lot_id[0]
                        for no_serie in numero_series:
                            line_vals.append((0, 0, {'product_id': line.product_id.id or False,
                                                     'name': line.name,
                                                     'quantity': 1,  # line.product_uom_qty,
                                                     'price_unit': line.price_unit,
                                                     'ubicacion_exacta': line.ubicacion_exacta,
                                                     'display_type': line.display_type,
                                                     'no_serie': no_serie.id,
                                                     }))
                    elif line.product_id.rent_ok == True and line.product_id.tracking != 'serial':
                        line_vals.append((0, 0, {'product_id': line.product_id.id or False,
                                                 'name': line.name,
                                                 'quantity': line.product_uom_qty,
                                                 'price_unit': line.price_unit,
                                                 'display_type': line.display_type,
                                                 'ubicacion_exacta': line.ubicacion_exacta,
                                                 }))
                    elif line.product_uom_qty > 0:
                        primera_vals.append((0, 0, {'product_id': line.product_id.id or False,
                                                    'name': line.name,
                                                    'quantity': line.product_uom_qty,
                                                    'price_unit': line.price_unit,
                                                    }))
                else:
                    deposito_garantia = deposito_garantia + line.price_subtotal

            vals = {  # 'name': rec.name,
                'partner_id': customer.id,
                'pricelist_id': price_list.id,
                'recurring_rule_type': 'monthly',
                'contract_line_fixed_ids': line_vals,
                'primera_factura_ids': primera_vals,
                'so_rentals': rec.name,
                'testimonio_notarial_ac': rec.testimonio_notarial_ac,
                'fecha_ac': rec.fecha_ac,
                'notaria_ac': rec.notaria_ac,
                'nombre_notario_ac': rec.nombre_notario_ac,
                'domicilio_ac': rec.domicilio_ac,
                'testimonio_notarial_pn': rec.testimonio_notarial_pn,
                'fecha_pn': rec.fecha_pn,
                'notaria_pn': rec.notaria_pn,
                'nombre_notario_pn': rec.nombre_notario_pn,
                'domicilio_pn': rec.domicilio_pn,
                'tipo_contrato': contract_type,
                'team_id': rec.team_id.id,
                'deposito_garantia': deposito_garantia,
                'payment_term_id': rec.payment_term_id.id,
            }

            contract_order.create(vals)

    def open_contract_related(self):
        return {
            'name': _('Contratos'),
            'domain': [('id', 'in', self.contract_related.ids)],
            'view_type': 'form',
            'res_model': 'contract.contract',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
        }
