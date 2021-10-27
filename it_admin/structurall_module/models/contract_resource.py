from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
from dateutil import relativedelta
from . import amount_to_text_es_MX
import base64

class Contract(models.Model):
    _inherit = 'contract.contract'

    name_serie = fields.Char("Name", required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))

    #Campos Acta constitutiva
    nombre_representante_ac = fields.Char(string="Nombre del representante legal")
    testimonio_notarial_ac = fields.Char(string="Testimonio notarial")
    fecha_ac = fields.Date(string="Fecha")
    notaria_ac = fields.Char(string="Notaria")
    nombre_notario_ac = fields.Char(string="Nombre del notario")
    domicilio_ac = fields.Char(string="Domicilio")
    ciudad_notario_ac = fields.Char(string="Ciudad notario")

    #Campos Poder notarial
    nombre_representante_pn = fields.Char(string="Nombre del representante legal")
    testimonio_notarial_pn = fields.Char(string="Testimonio notarial")
    fecha_pn = fields.Date(string="Fecha")
    notaria_pn = fields.Char(string="Notaria")
    nombre_notario_pn = fields.Char(string="Nombre del notario")
    domicilio_pn = fields.Char(string="Domicilio")
    ciudad_notario_pn = fields.Char(string="Ciudad notario")

    no_meses = fields.Integer(string="Meses",compute="check_meses")
    no_meses_original = fields.Integer(string="No Meses original", compute="check_meses_original")
    fecha_fin_original = fields.Date(string="Fecha fin original", compute="substract_meses")

    #No Verificador
    no_verificador = fields.Char(string="Número verificador")
    team_id = fields.Many2one('crm.team', string="Equipos de venta")
    primera_factura_ids = fields.One2many('primera.factura', 'contract_primera_ids', string='Primera Factura')
    so_rentals = fields.Char(string="SO / Rentals")
    adendum_count = fields.Integer(string="Adendum", compute="get_adendum_count")
    adendum_count_2 = fields.Integer(string="Adendum", compute="get_adendum_count_2")
    tipo_contrato =  fields.Selection(
        selection=[('Renta', 'Renta'), 
                   ('Financiamiento', 'Financiamiento'),],
        string=_('Tipo de contrato'),
    )
    deposito_garantia = fields.Float(string="Depósito en garantía")
    
    deposito_pagado = fields.Boolean(string="Deposito pagado")

    @api.constrains('no_verificador')
    def _check_your_field(self):
        if self.no_verificador and len(self.no_verificador) > 1:
            raise ValidationError('El número verificador no debe ser mayor a 1 carácter')

    #NUMBER OF MONTHS WITH THE SUM OF THE MONTHS ADDED VIA ADENDUM
    total_months_adendum = fields.Float(string="Meses agregados por adendum",compute="sum_all_months_in_adendum")

    #Search in the adendums and sum the number of months only for the adendum in state done if there is no adendum the value must be 0
    def sum_all_months_in_adendum(self):
        adendums = self.env['adendum.adendum'].search([('state','=','done'),('adendum_origen','=', self.id)])
        self.total_months_adendum = 0
        if self.adendum_count >= 1:
            for rec in adendums:
                self.total_months_adendum += rec.no_meses
        else:
            self.total_months_adendum = 0


    #GET NUMBER OF MONTHS BETWEEN THE date_start and date_end
    #def check_meses(self):
    #        date1 = self.date_start
    #        date2 = self.date_end
    #        r = relativedelta.relativedelta(date2, date1)
    #        if self.date_start and self.date_end:
    #            self.no_meses = r.months
    #        else:
    #            self.no_meses = 0

    def check_meses(self):
        #date1 = datetime(self.date_start).strftime("%A, %B %e, %Y")
        #date2 = datetime(self.date_end).strftime("%A, %B %e, %Y")
        date1 = self.date_start
        date2 = self.date_end
        if self.date_start and self.date_end:
            self.no_meses = (date2.year - date1.year) * 12 + (date2.month - date1.month)
        else:
            self.no_meses = 0

    #SUBSTRACT NUMBER OF MONTHS TO GET ORIGINAL DATE FOR THE ADENDUM REPORT
    def substract_meses(self):
        if self.no_meses and self.date_end:
            a_month = relativedelta.relativedelta(months=self.total_months_adendum)
            date_minus_month = self.date_end - a_month
            self.fecha_fin_original = date_minus_month
        else:
            self.fecha_fin_original = None

    #GET ORIGINAL NUMBER OF MONTHS BETWEEN THE date_start and fecha_fin_original
    def check_meses_original(self):
            date1 = self.date_start
            date2 = self.fecha_fin_original
            r = relativedelta.relativedelta(date2, date1)
            if self.date_start and self.total_months_adendum > 1:
                self.no_meses_original = self.no_meses - self.total_months_adendum
            else:
                self.no_meses_original = self.no_meses

    @api.depends('deposito_garantia', 'currency_id')
    def _get_amount_to_text(self):
        for record in self:
            record.amount_to_text = amount_to_text_es_MX.get_amount_to_text(record, record.deposito_garantia,record.currency_id.name)
        

    @api.model
    def _get_amount_2_text(self, deposito_garantia):
        return amount_to_text_es_MX.get_amount_to_text(self, deposito_garantia, self.currency_id.name)



    def get_adendum_count(self):
        count = self.env['adendum.adendum'].search_count([('adendum_origen', '=', self.id)])
        self.adendum_count = count

    def get_adendum_count_2(self):
        count = self.env['adendum.adendum'].search_count([('adendum_origen', '=', self.id)])
        self.adendum_count_2 = count + 1

    def action_crear_adendum(self):
        ctx = self._context.copy()
        return {
                'name': "Crear Adendum",
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'crear.adendum.wizard',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'context': ctx,
            }


    def open_adendum_related(self):
        return {
            'name': _('Adendum'),
            'domain': [('adendum_origen', '=', self.id)],
            'view_type': 'form',
            'res_model': 'adendum.adendum',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
        }

    @api.model
    def create(self, vals):
        if vals.get('name_serie', _('New')) == _('New') and vals.get('tipo_contrato') == 'Renta':
            vals['name_serie'] = self.env['ir.sequence'].next_by_code('contract.renta') or _('New')
        else:
            vals['name_serie'] = self.env['ir.sequence'].next_by_code('contract.sale') or _('New')
        vals['name'] = vals['name_serie']
        result = super(Contract, self).create(vals)
        return result

    @api.onchange('so_rentals')
    def _get_team_id(self):
        if self.so_rentals:
            if self.so_rentals.find(',') > 0:
               first = self.so_rentals.split(",")[0]
            else:
               first = self.so_rentals
            sale_orders = self.sudo().env['sale.order'].search([('name','=',first)], limit=1)
            if sale_orders:
               values = {'team_id': sale_orders.team_id.id}
               self.update(values)

    def create_invoice_from_contract(self):
        invoice_line_obj = self.env['account.move.line']
        invoice_obj = self.env['account.move']
        inv_line_fields = invoice_line_obj._fields.keys()
        ctx = self._context.copy()
        
        for contract in self:
            invoice_lines = []
            ctx.update({'default_type': 'out_invoice', 'move_type': 'out_invoice'})
            journal = contract.journal_id
            if not journal:
                journal = invoice_obj.with_context(ctx)._default_journal()
            partner = contract.partner_id
            company = contract.company_id or self.env.company
            invoice_vals = {
                'move_type':'out_invoice',
                'partner_id':partner.id,
                'currency_id' : journal.currency_id.id or journal.company_id.currency_id.id or company.currency_id.id,
                'company_id' : company.id,
                'journal_id' : journal.id,
            }
            
            customer_invoice = invoice_obj.with_context(ctx).new(invoice_vals)
            customer_invoice._onchange_partner_id()
            invoice_vals = customer_invoice._convert_to_write({name: customer_invoice[name] for name in customer_invoice._cache})
            invoice_vals.update({'journal_id' : journal.id,})
        
            for line in contract.contract_line_fixed_ids:
                line_data = invoice_line_obj.default_get(inv_line_fields)
                line_data.update({
                            'product_id':line.product_id.id,
                            'name': line.name or line.product_id.display_name,
                            'product_uom_id': line.uom_id.id,
                            'price_unit': line.price_unit,
                            'discount':line.discount,
                            'quantity': line.quantity or 1,
                            'contract_line_id' : line.id,
                            'tax_ids': [(6, 0, line.product_id.taxes_id.ids)],
                        })
                invoice_lines.append((0,0,line_data))
            
            for line in contract.primera_factura_ids:
                line_data = invoice_line_obj.default_get(inv_line_fields)
                line_data.update({
                            'product_id':line.product_id.id,
                            'name': line.name or line.product_id.display_name,
                            'price_unit': line.price_unit,
                            'quantity': line.quantity or 1,
                            'tax_ids': [(6, 0, line.product_id.taxes_id.ids)],
                        })
                invoice_lines.append((0,0,line_data))
                
            if invoice_lines:
                invoice_vals.update({'invoice_line_ids': invoice_lines})
                if 'line_ids' in invoice_vals:
                    invoice_vals.pop('line_ids')
            invoice_exist = invoice_obj.with_context(ctx).create(invoice_vals)
            
        return

    def action_contract_send(self):
        self.ensure_one()
        template = self.env.ref("contract.email_contract_template", False)
        if self.tipo_contrato == 'Renta':
            new_attachments = []
            isr_report_name = 'Contrato Arrendamiento'+ '.pdf'
            pdf_report_contrato = self.env.ref('structurall_module.report_contrato_persona_moral')._render_qweb_pdf(self.ids)[0]
            isr_pdf = base64.b64encode(pdf_report_contrato)
            attachment_id = self.env['ir.attachment'].sudo().create({'name': isr_report_name,'datas': isr_pdf,'res_model': self._name,'res_id': self.id,'type': 'binary'})
            new_attachments.append(attachment_id.id)
            isr_report_name = 'Pagare Structurall'+ '.pdf'
            pdf_report_contrato = self.env.ref('structurall_module.report_pagare_structurall')._render_qweb_pdf(self.ids)[0]
            isr_pdf = base64.b64encode(pdf_report_contrato)
            attachment_id = self.env['ir.attachment'].sudo().create({'name': isr_report_name,'datas': isr_pdf,'res_model': self._name,'res_id': self.id,'type': 'binary'})
            new_attachments.append(attachment_id.id)
            template.write({'attachment_ids':new_attachments})
        if self.tipo_contrato == 'Financiamiento':
            new_attachments = []
            isr_report_name = 'Contrato Financiamiento'+ '.pdf'
            pdf_report_contrato = self.env.ref('structurall_module.report_contrato_financiamiento_structurall')._render_qweb_pdf(self.ids)[0]
            isr_pdf = base64.b64encode(pdf_report_contrato)
            attachment_id = self.env['ir.attachment'].sudo().create({'name': isr_report_name,'datas': isr_pdf,'res_model': self._name,'res_id': self.id,'type': 'binary'})
            new_attachments.append(attachment_id.id)
            template.write({'attachment_ids':new_attachments})
        
            
        compose_form = self.env.ref("mail.email_compose_message_wizard_form")
        ctx = dict(
            default_model="contract.contract",
            default_res_id=self.id,
            default_use_template=bool(template),
            default_template_id=template and template.id or False,
            default_composition_mode="comment",
        )
        return {
            "name": _("Compose Email"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "mail.compose.message",
            "views": [(compose_form.id, "form")],
            "view_id": compose_form.id,
            "target": "new",
            "context": ctx,
        }


class ContractLine(models.Model):
    _inherit = "contract.line",

    ubicacion_exacta = fields.Char(string="Ubicación exacta")
    proyecto = fields.Char(string="Proyecto")
    es_caseta = fields.Boolean(string="Caseta")

    
class PrimeraFactura(models.Model):
    _name = "primera.factura"
    _description = "Tabla para primeras facturas"

    product_id = fields.Many2one('product.product',string="Producto")
    name = fields.Char(string="Descripción")
    quantity = fields.Float(string="Cantidad")
    price_unit = fields.Float(string="Precio unitario")
    unidad_medida = fields.Char(string="Unidad de medida")
    subtotal = fields.Float(string="Subtotal", compute="_subtotal_amount")
    contract_primera_ids = fields.Many2one('contract.contract',string="Contrato primera")

    @api.onchange('quantity', 'price_unit')
    def _subtotal_amount(self):
        for line in self:
            line.subtotal = line.price_unit * line.quantity
