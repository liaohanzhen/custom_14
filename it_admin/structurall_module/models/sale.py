from odoo import models, api, fields, _
from odoo import exceptions
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
import logging
from odoo.exceptions import UserError
from datetime import datetime
_logger = logging.getLogger(__name__)
from datetime import timedelta

class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'
    
    def _create_payments(self):
        res = super(AccountPaymentRegister, self)._create_payments()
        ctx = self.env.context
        if ctx.get('active_id'):
            move = self.env['account.move'].browse(ctx.get('active_id'))
            if move.operating_unit_id:
                res['operating_unit_id'] = move.operating_unit_id.id
        return res

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    state = fields.Selection(selection_add=[('autorizacion', 'Autorizacion')], ondelete={'autorizacion': 'set default'})

    overdue_credit = fields.Boolean(
        compute='_get_overdue_credit', string="Saldos vencidos", type='Boolean',
        help="Indica que un cliente tiene saldos vencidos")
    autorizado = fields.Boolean(string="Autorizado", default = False, readonly=True)
    is_deliverd = fields.Boolean(compute='_compute_deliverd_done', store=True)

    def action_quotation_send(self):
        res = super(SaleOrder, self).action_quotation_send()
        if self.is_rental_order == True:
            template_id = self.env['ir.model.data'].get_object_reference('structurall_module', 'presupuesto_structurall_mail_template_sale')[1]
            ctx = res['context']
            ctx['default_template_id'] = template_id
            ctx['default_use_template'] = True
        return res

    @api.depends('picking_ids.state')
    def _compute_deliverd_done(self):
        for order in self:
            if order.picking_ids:
                check_done = any(order.picking_ids.filtered(lambda x: x.state != 'done'))
                if check_done:
                    order.is_deliverd = False
                else:
                    order.is_deliverd = True
            
    @api.model
    def debit_credit_maturity(self, movelines):
        debit_maturity, credit_maturity = 0.0, 0.0
        for line in movelines:
            limit_day = line.date_maturity
            _logger.info('limit day %s', limit_day)
            if limit_day <= fields.Date.today():
                # credit and debit maturity sums all aml
                # with late payments
                debit_maturity += line.debit
            credit_maturity += line.credit
        return debit_maturity, credit_maturity

    def _get_overdue_credit(self):
        moveline_obj = self.env['account.move.line']
        for partner in self:
            domain = self.movelines_domain(partner)
            movelines = moveline_obj.search(domain)
            _logger.info('pasa 02')
            debit_maturity, credit_maturity = self.debit_credit_maturity(
                movelines)
            balance_maturity = debit_maturity - credit_maturity
            #partner.overdue_credit = balance_maturity > 0.0
            _logger.info('balance_maturity %s', balance_maturity)

            if balance_maturity > 0.0:
                return True
            else:
                msg = _('Tiene saldos vencidos el cliente : %s') % (partner.partner_id.name)
                raise exceptions.Warning(msg)

    @api.model
    def movelines_domain(self, partner):
        """Return the domain for search the
        account.move.line for the user's company."""
        domain = [('partner_id', '=', partner.id),
                  ('company_id', '=', self.env.user.company_id.id),
#                  ('account_id.internal_type', '=', 'receivable'),
#                  ('move_id.state', '!=', 'draft'),
                  ('reconciled', '=', False)]
        return domain

    def action_confirm(self):
        #self._get_overdue_credit()
        return super(SaleOrder, self).action_confirm()

    def action_autorizar(self):
        #self.write({'autorizado': 'True'})
        self.write({'state': 'sent', 'autorizado': 'True'})


    def revisar_cotizacion(self):
        for order in self:
           products_stock = self.order_line.filtered(lambda r: r.product_id.type == 'product')
           if products_stock.filtered(lambda r: r.product_id.with_context(warehouse=self.warehouse_id.id).qty_available <= 0) or (self.estado_instalacion and self.estado_instalacion not in self.team_id.estados):
               self.write({'state': 'autorizacion'})
           else:
               self.write({'autorizado': 'True'})

    @api.model
    def create(self, vals):
        partner_id = vals.get('partner_id')
        #res_config = self.env['res.config.settings'].sudo().search([], order='id desc', limit=1)
        #dias_gracia = res_config.dias_gracia
        dias_gracia_config = self.env['res.company'].sudo().search([], order='id desc', limit=1)
        dias_gracia = dias_gracia_config.dias_gracia
        current_date = datetime.today()

        if partner_id:
            partner = self.env['res.partner'].browse(partner_id)
            facturas = self.sudo().env['account.move'].search([('move_type','=', 'out_invoice'),('state','=','posted'), ('payment_state','!=','paid'), ('partner_id','=', partner.id),('invoice_date_due','<', datetime.today() - timedelta(days=dias_gracia))])
            for factura in facturas:
                _logger.info('numero %s', factura.name)
                _logger.info('DIAS DE GRACIA DE CONFIGURACION %s', dias_gracia)

            if partner.autoizar_con_saldo_vencido == False and facturas:
                raise exceptions.Warning('Cliente con saldo vencido')

            
        res = super(SaleOrder, self).create(vals)
        return res

    def _write(self,vals):
        if vals.get('amount_total'):
            new_total = vals.get('amount_total')
            for order in self:
                if order.amount_total != new_total:
                    super(SaleOrder, order)._write({'autorizado': False})
        return super(SaleOrder, self)._write(vals)

    def write(self, vals):
        _logger.info('pasa 05')
        #res_config = self.env['res.config.settings'].sudo().search([], order='id desc', limit=1)
        #dias_gracia = res_config.dias_gracia
        dias_gracia_config = self.env['res.company'].sudo().search([], order='id desc', limit=1)
        dias_gracia = dias_gracia_config.dias_gracia


        if 'partner_id' in vals:
            partner = self.env['res.partner'].browse(vals['partner_id'])
            facturas = self.sudo().env['account.move'].search([('move_type','=', 'out_invoice'), ('state','=','posted'), ('payment_state','!=','paid'), ('partner_id','=', partner.id),('invoice_date_due','<', datetime.today() - timedelta(days=dias_gracia))])
            for factura in facturas:
                _logger.info('NOMBRE DE LA FACTURA: %s', factura.name)
                _logger.info('DIAS DE GRACIA DE CONFIGURACION %s', dias_gracia)

            if partner.autoizar_con_saldo_vencido == False and facturas:
                raise exceptions.Warning('Cliente con saldo vencido')

        else:
            for order in self:
                partner = order.partner_id
                facturas = self.sudo().env['account.move'].search([('move_type','=', 'out_invoice'), ('state','=','posted'), ('payment_state','!=','paid'), ('partner_id','=', partner.id),('invoice_date_due','<', datetime.today() - timedelta(days=dias_gracia))])
                for factura in facturas:
                    _logger.info('NOMBRE DE LA FACTURA3 %s', factura.name)

                if partner.autoizar_con_saldo_vencido == False and facturas:
                    raise exceptions.Warning('Cliente con saldo vencido')

        #vals['autorizado'] = False
        return super(SaleOrder, self).write(vals)
    
    def create_contact_action(self):
        contract_order = self.env['contract.contract']
        order = self.sorted(lambda x:x.create_date, reverse=True)[0]
        
        line_vals = []
        primera_vals = []
        deposito_garantia = 0
        for rec in self:
            #Values for the first time invoice One2many
            for line in rec.order_line:
                if line.name.lower().find('deposito') and line.name.lower().find('depósito') == -1: 
                    if line.product_id.rent_ok == True and line.product_id.tracking == 'serial':
                        for picking in self.picking_ids:
                            if picking.state == 'done':
                               for stock_line in picking.move_line_ids_without_package:
                                   _logger.info('aqui 0004')
                                   if line.product_id.id == stock_line.product_id.id:
                                        no_serie = stock_line.lot_id[0]
                        line_vals.append((0,0,{'product_id': line.product_id.id or False,
                                        'name': line.name,
                                        'quantity': line.product_uom_qty,
                                        'price_unit': line.price_unit,
                                        'display_type': line.display_type,
                                        'ubicacion_exacta': line.ubicacion_exacta,
                                        'no_serie': no_serie.id,
                                        }))
                    elif line.product_id.rent_ok == True and line.product_id.tracking != 'serial': 
                        line_vals.append((0,0,{'product_id': line.product_id.id or False,
                                        'name': line.name,
                                        'quantity': line.product_uom_qty,
                                        'price_unit': line.price_unit,
                                        'display_type': line.display_type,
                                        'ubicacion_exacta': line.ubicacion_exacta,
                                        }))
                    elif line.product_uom_qty > 0:
                        primera_vals.append((0,0,{'product_id': line.product_id.id or False,
                                        'name': line.name,
                                        'quantity': line.product_uom_qty,
                                        'price_unit': line.price_unit,
                                        }))
                else:
                    deposito_garantia = deposito_garantia + line.price_unit

        customer = order.partner_id
        price_list = order.pricelist_id
        so_rental_name = ','.join([order.name for order in self])
        
        if order.is_rental_order == True:
            contract_type = 'Renta'
        else:
            contract_type = 'Financiamiento'
            
        vals = {'name': order.name,
                'so_rentals' : so_rental_name,
                'partner_id': customer.id,
                'pricelist_id': price_list.id,
                'recurring_rule_type': 'monthly',
                'contract_line_fixed_ids': line_vals,
                'primera_factura_ids': primera_vals,
                #'so_origen': order.id,
                'testimonio_notarial_ac':order.testimonio_notarial_ac,
                'fecha_ac': order.fecha_ac,
                'notaria_ac':order.notaria_ac,
                'nombre_notario_ac':order.nombre_notario_ac,
                'domicilio_ac':order.domicilio_ac,
                'testimonio_notarial_pn':order.testimonio_notarial_pn,
                'fecha_pn': order.fecha_pn,
                'notaria_pn':order.notaria_pn,
                'nombre_notario_pn':order.nombre_notario_pn,
                'domicilio_pn':order.domicilio_pn,
                'tipo_contrato': contract_type,
                'team_id': order.team_id.id,
                'deposito_garantia': deposito_garantia,
                'payment_term_id': order.payment_term_id.id,
                }
        
        contract_order.create(vals)

    def unlink(self):
        for order in self:
            if not order.user_has_groups('sales_team.group_sale_manager'):
                raise UserError(_('No puedes eliminar este registro. Solo un administrador puede eliminarlo.'))
        return super(SaleOrder, self).unlink()

