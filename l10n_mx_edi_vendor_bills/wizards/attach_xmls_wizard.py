# Copyright 2017, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import base64
from lxml import etree, objectify
from datetime import datetime

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_is_zero, float_round


TYPE_CFDI22_TO_CFDI33 = {
    'ingreso': 'I',
    'egreso': 'E',
    'traslado': 'T',
    'nomina': 'N',
    'pago': 'P',
}


class AttachXmlsWizard(models.TransientModel):
    _name = 'attach.xmls.wizard'
    _description = "Attach xmls"


    @api.model
    def _default_journal(self):
        move_type = 'in_invoice' if self._context.get(
            'l10n_mx_edi_invoice_type') == 'in' else 'out_invoice'
        return self.env['account.move'].with_context(
            default_move_type=move_type)._get_default_journal()

    @api.model
    def _get_journal_domain(self):
        move_type = 'purchase' if self._context.get(
            'l10n_mx_edi_invoice_type') == 'in' else 'sale'
        return [('type', '=', move_type)]

    @api.model
    def _get_account_domain(self):
        return [('company_id', '=', self.env.company.id)]


    dragndrop = fields.Char()
    account_id = fields.Many2one(
        'account.account',
        help='Optional field to define the account that will be used in all '
        'the lines of the invoice.\nIf the field is not set, the wizard will '
        'take the account by default.',
        domain=_get_account_domain)
    journal_id = fields.Many2one(
        'account.journal', required=True,
        default=_default_journal,
        domain=_get_journal_domain,
        help='This journal will be used in the invoices generated with this '
        'wizard.')
    omit_cfdi_related = fields.Boolean(
        help='Use this option when the CFDI attached do not have a CFDI '
        'related and is a Refund (Only as exception)',
        default=True)
    product_create = fields.Boolean(
        help='Use this option to allow the importer to also create new products '
        'when they are not found in database.',
        default=False)


    @staticmethod
    def _xml2capitalize(xml):
        """Receive 1 lxml etree object and change all attrib to Capitalize.
        """
        def recursive_lxml(element):
            for attrib, value in element.attrib.items():
                new_attrib = "%s%s" % (attrib[0].upper(), attrib[1:])
                element.attrib.update({new_attrib: value})

            for child in element.getchildren():
                child = recursive_lxml(child)
            return element
        return recursive_lxml(xml)

    @staticmethod
    def _l10n_mx_edi_convert_cfdi32_to_cfdi33(cfdi_etree):
        """Convert a xml from cfdi32 to cfdi33
        :param xml: The xml 32 in lxml.objectify object
        :return: A xml 33 in lxml.objectify object
        """
        if cfdi_etree.get('version', None) not in ('3.2', '3.0', '2.2', '2.0') or cfdi_etree.get(
            'Version', None) == '3.3':
            return cfdi_etree
        # TODO: Process negative taxes "Retenciones" node
        # TODO: Process payment term
        cfdi_etree = AttachXmlsWizard._xml2capitalize(cfdi_etree)
        cfdi_etree.attrib.update({
            'TipoDeComprobante': TYPE_CFDI22_TO_CFDI33[
                cfdi_etree.attrib['tipoDeComprobante']],
            # 'Version': '3.2',
            # By default creates Payment Complement since that the imported
            # invoices are most imported for this propose if it is not the case
            # then modified manually from odoo.
            'MetodoPago': 'PPD',
        })
        return cfdi_etree

    def get_cfdi_node(self, cfdi_etree, attribute='tfd:TimbreFiscalDigital[1]', namespaces={'tfd': 'http://www.sat.gob.mx/TimbreFiscalDigital'}):
        ''' Helper to extract relevant data from CFDI 3.3 nodes.
        By default this method will retrieve tfd, Adjust parameters for other nodes
        :param cfdi_etree:  The cfdi etree object.
        :param attribute:   tfd.
        :param namespaces:  tfd.
        :return:            A python dictionary or None.
        '''
        if not hasattr(cfdi_etree, 'Complemento'):
            return {}
        node = cfdi_etree.Complemento.xpath(attribute, namespaces=namespaces)
        return node[0] if node else {}

    @staticmethod
    def collect_taxes(taxes_xml):
        """ Get tax data of the Impuesto node of the xml and return
        dictionary with taxes datas
        :param taxes_xml: Impuesto node of xml
        :type taxes_xml: etree
        :return: A list with the taxes data dict
        :rtype: list
        """
        taxes = []
        tax_codes = {'001': 'ISR', '002': 'IVA', '003': 'IEPS'}
        for rec in taxes_xml:
            tax_xml = rec.get('Impuesto', '')
            tax_xml = tax_codes.get(tax_xml, tax_xml)
            amount_xml = float(rec.get('Importe', '0.0'))
            rate_xml = float_round(
                float(rec.get('TasaOCuota', '0.0')) * 100, 4)
            if 'Retenciones' in rec.getparent().tag:
                amount_xml = amount_xml * -1
                rate_xml = rate_xml * -1

            taxes.append({
                'tax': tax_xml,
                'rate': rate_xml,
                'amount': amount_xml
            })
        return taxes

    def get_cfdi_taxes(self, cfdi_etree):
        if not hasattr(cfdi_etree, 'Impuestos'):
            return {}
        tax_obj = self.env['account.tax']
        type_tax_use = 'purchase' if self._context.get(
            'l10n_mx_edi_invoice_type') == 'in' else 'sale'
        taxes_dict = {
            'wrong_taxes': [],
            'taxes_ids': {},
            'withno_account': [],
            'total_amount': 0.0
        }
        taxes = []

        if cfdi_etree.get('Version') == "3.2":
            if hasattr(cfdi_etree.Impuestos, 'Traslados'):
                for rec in cfdi_etree.Impuestos.Traslados.Traslado:
                    taxes_dict['total_amount'] += float(rec.get('importe', 0.0))
                    tax_name = rec.get('impuesto')
                    tax_percent = float(rec.get('tasa'))
                    tax_group_id = self.env['account.tax.group'].search(
                        [('name', 'ilike', tax_name)])
                    tax_domain = [
                        ('type_tax_use', '=', type_tax_use),
                        ('company_id', '=', self.env.company.id),
                        ('tax_group_id', 'in', tax_group_id.ids),
                        ('amount_type', '=', 'percent'),
                        ('amount', '=', tax_percent)]
                    tax = tax_obj.search(tax_domain, limit=1)
                    if not tax:
                        taxes_dict['wrong_taxes'].append('%s(%s%%)' % (tax_name, tax_percent))
                    repartition_id = self.env['account.tax.repartition.line'].search([
                        ('tax_id', '=', tax.id),
                        ('repartition_type', '=', 'tax'),
                        ('account_id', '!=', False)], limit=1)
                    taxes_dict['taxes_ids']['old'] = []
                    taxes_dict['taxes_ids']['old'].append((0, 0, {
                        'tax_id': tax.id,
                        'account_id': repartition_id.account_id.id,
                        'name': tax_name
                    }))
            if hasattr(cfdi_etree.Impuestos, 'Retenciones'):
                for rec in cfdi_etree.Impuestos.Retenciones.Retencion:
                    taxes_dict['total_amount'] -= float(rec.get('importe', 0.0))
        if cfdi_etree.get('Version') == "3.3":
            taxes_dict['total_amount'] += (float(cfdi_etree.Impuestos.get('TotalImpuestosRetenidos', 0.0)) +
                float(cfdi_etree.Impuestos.get('TotalImpuestosTrasladados', 0.0)))

        for index, rec in enumerate(cfdi_etree.Conceptos.Concepto):
            if not hasattr(rec, 'Impuestos'):
                continue
            taxes_dict['taxes_ids'][index] = []
            taxes_xml = rec.Impuestos
            if hasattr(taxes_xml, 'Traslados'):
                taxes = self.collect_taxes(taxes_xml.Traslados.Traslado)
            if hasattr(taxes_xml, 'Retenciones'):
                taxes += self.collect_taxes(taxes_xml.Retenciones.Retencion)

            for tax in taxes:
                tax_name = '%s(%s%%)' % (tax['tax'], tax['rate'])
                tax_group_id = self.env['account.tax.group'].search(
                    [('name', 'ilike', tax['tax'])])
                domain = [('tax_group_id', 'in', tax_group_id.ids),
                          ('type_tax_use', '=', type_tax_use)]
                if type_tax_use == 'purchase':
                    if -10.67 <= tax['rate'] <= -10.66:
                        domain.append(('amount', '<=', -10.66))
                        domain.append(('amount', '>=', -10.67))
                    else:
                        domain.append(('amount', '=', tax['rate']))
                
                tax_get = tax_obj.search(domain, limit=1, order='id asc')
                if not tax_group_id or not tax_get:
                    taxes_dict['wrong_taxes'].append(tax_name)
                    continue
                # TODO review if this validation of account in taxes is correct                    account_id = tax_obj
                repartition_id = self.env['account.tax.repartition.line'].search([
                    ('tax_id', '=', tax_get.id),
                    ('repartition_type', '=', 'tax'),
                    ('account_id', '!=', False)], limit=1)
                account_id = repartition_id.id and repartition_id.account_id
                if not account_id.id:
                    taxes_dict['withno_account'].append(
                        tax_name if tax_name else tax['tax'])
                else:
                    tax['id'] = tax_get.id
                    tax['account'] = account_id.id
                    tax['name'] = tax_name if tax_name else tax['tax']
                    taxes_dict['taxes_ids'][index].append(tax)
        return taxes_dict

    def get_cfdi_local_taxes(self, cfdi_etree):
        '''
        :param cfdi_etree:  The cfdi etree object.
        :return:            A python dictionary or None.
        '''
        local_taxes = self.get_cfdi_node(cfdi_etree,
            'implocal:ImpuestosLocales',
            {'implocal': 'http://www.sat.gob.mx/implocal'})
        if not local_taxes:
            return {}
        type_tax_use = 'purchase' if self._context.get(
            'l10n_mx_edi_invoice_type') == 'in' else 'sale'
        taxes_dict = {
            'wrong_taxes': [],
            'taxes_ids': [],
            'withno_account': [],
            'total_amount': 0.0
        }
        tax_obj = self.env['account.tax']
        if hasattr(local_taxes, 'RetencionesLocales'):
            for local_ret in local_taxes.RetencionesLocales:
                tax_name = local_ret.get('ImpLocRetenido')
                tax_percent = float(local_ret.get('TasadeRetencion')) * -1
                tax = tax_obj.search([
                    '&',
                    ('type_tax_use', '=', type_tax_use),
                    '|',
                    ('name', '=', tax_name),
                    ('amount', '=', tax_percent)], limit=1)
                if not tax:
                    taxes_dict['wrong_taxes'].append(tax_name)
                    continue
                elif not tax.account_id:
                    taxes_dict['withno_account'].append(tax_name)
                    continue
                taxes_dict['taxes_ids'].append((0, 0, {
                    'tax_id': tax.id,
                    'account_id': tax.account_id.id,
                    'name': tax_name,
                    'amount': float(local_ret.get('Importe')) * -1,
                }))
                taxes_dict['total_amount'] = taxes_dict['total_amount'] + float(local_taxes.get('Importe'))
        if hasattr(local_taxes, 'TrasladosLocales'):
            for local_tras in local_taxes.TrasladosLocales:
                tax_name = local_tras.get('ImpLocTrasladado')
                tax_percent = float(local_tras.get('TasadeTraslado'))
                tax = tax_obj.search([
                    '&',
                    ('type_tax_use', '=', type_tax_use),
                    '|',
                    ('name', '=', tax_name),
                    ('amount', '=', tax_percent)], limit=1)
                if not tax:
                    taxes_dict['wrong_taxes'].append(tax_name)
                    continue
                elif not tax.invoice_repartition_line_ids:
                    taxes_dict['withno_account'].append(tax_name)
                    continue
                taxes_dict['taxes_ids'].append((0, 0, {
                    'tax_id': tax.id,
                    'name': tax_name,
                    'amount': float(local_tras.get('Importe')),
                }))
                taxes_dict['total_amount'] = taxes_dict['total_amount'] + float(local_tras.get('Importe'))
        return taxes_dict

    def get_cfdi_serie_folio(self, cfdi_etree):
        xml_serie = cfdi_etree.get('Serie', False)
        xml_folio = cfdi_etree.get('Folio', False)
        xml_sefo = ''
        if xml_serie or xml_folio:
            xml_sefo = '%s%s' % (cfdi_etree.get('Serie', ''), cfdi_etree.get('Folio', ''))
        return xml_sefo

    def get_cfdi_date(self, cfdi_etree):
        date = cfdi_etree.get('Fecha', '').split('T')
        date = datetime.strptime(str(date[0]), '%Y-%m-%d')
        return date

    def get_cfdi_currency(self, cfdi_etree):
        currency = cfdi_etree.get('Moneda', 'MXN')
        mxn = ['mxp', 'mxn', 'mn', 'peso', 'pesos', 'peso mexicano', 'pesos mexicanos', 'nacional', 'nal', 'm.n.', '$', '2013']
        usd = ['dolar', 'dólar', 'dólares', 'dolares']
        currency = 'MXN' if currency.lower() in mxn else currency
        currency = 'USD' if currency.lower() in usd else currency
        return currency

    def get_cfdi_cfdi_related_uuid(self, cfdi_etree):
        # TODO This method just considers one related uuid and it can contain
        # several uuids
        uuid = False
        if hasattr(cfdi_etree, 'CfdiRelacionados'):
            uuid = {'type': cfdi_etree.CfdiRelacionados.get('TipoRelacion', '01')}
            uuid.update({'uuid': cfdi_etree.CfdiRelacionados.CfdiRelacionado.get('UUID').upper()})
        return uuid

    def _l10n_mx_edi_prepare_cfdi_dict(self, xml64):
        ''' Helper to extract relevant data from the CFDI.
        :param xml:     The xml b64 file.
        :return:        A python dictionary.
        :rtype:         dict
        '''
        if isinstance(xml64, bytes):
            xml64 = xml64.decode()
        xml_str = base64.b64decode(xml64.replace('data:text/xml;base64,', ''))
        xml_str = xml_str.replace(b'xmlns:schemaLocation', b'xsi:schemaLocation')
        cfdi_etree = objectify.fromstring(xml_str)
        cfdi_etree = self._l10n_mx_edi_convert_cfdi32_to_cfdi33(cfdi_etree)
        tfd_node = self.get_cfdi_node(cfdi_etree)
        # Try Nommina 1.0
        payslip_node = self.get_cfdi_node(
            cfdi_etree,
            attribute='nomina:Nomina',
            namespaces={'nomina':'http://www.sat.gob.mx/nomina'},
        )
        # Try Nommina 1.2
        if payslip_node is None:
            payslip_node = self.get_cfdi_node(
                cfdi_etree,
                attribute='nomina12:Nomina',
                namespaces={'nomina12':'http://www.sat.gob.mx/nomina12'},
            )

        return {
            'fiscal_regime': cfdi_etree.Emisor.get('RegimenFiscal', ''),
            'issuer_rfc': cfdi_etree.Emisor.get('Rfc', cfdi_etree.Emisor.get('rfc')).upper(),
            'issuer_name': cfdi_etree.Emisor.get('Nombre', ''),
            'receiver_rfc': cfdi_etree.Receptor.get('Rfc', cfdi_etree.Receptor.get('rfc')).upper(),
            'receiver_name': cfdi_etree.Receptor.get('Nombre',''),
            'usage': cfdi_etree.Receptor.get('UsoCFDI', False),
            'cfdi_type': cfdi_etree.get('TipoDeComprobante', False),
            'version': cfdi_etree.get('Version', ''),
            'amount_total': float(cfdi_etree.get('Total', cfdi_etree.get('total', 0.0))),
            'amount_subtotal': float(cfdi_etree.get('SubTotal', 0.0)),
            'global_discount': cfdi_etree.get('Descuento', False),
            'datetime': cfdi_etree.get('Fecha', '').replace('T', ' '),
            
            'date': self.get_cfdi_date(cfdi_etree),
            'sefo': self.get_cfdi_serie_folio(cfdi_etree),
            'currency': self.get_cfdi_currency(cfdi_etree),
            'related_cfdi_uuid': self.get_cfdi_cfdi_related_uuid(cfdi_etree),
            
            'payment_form': cfdi_etree.get('FormaDePago', cfdi_etree.get('FormaPago')),
            'payment_method': cfdi_etree.get('MetodoPago'),
            'payment_term': cfdi_etree.get('CondicionesDePago', False),
            'bank_account': cfdi_etree.get('NumCtaPago'),
            'sello': cfdi_etree.get('sello', cfdi_etree.get('Sello', 'No identificado')),
            'certificate_number': cfdi_etree.get('noCertificado', cfdi_etree.get('NoCertificado')),
            'expedition': cfdi_etree.get('LugarExpedicion'),

            'lines': cfdi_etree.Conceptos.Concepto,

            'taxes': self.get_cfdi_taxes(cfdi_etree),
            'local_taxes': self.get_cfdi_local_taxes(cfdi_etree),

            'stamp_date': tfd_node.get('FechaTimbrado', '').replace('T', ' '),
            'certificate_sat_number': tfd_node.get('NoCertificadoSAT', ''),
            'uuid': tfd_node.get('UUID', '').upper(),
            'sello_sat': tfd_node.get('selloSAT', tfd_node.get('SelloSAT', 'No identificado')),
            
            'payslip': payslip_node,

            'cfdi_etree': cfdi_etree,
        }

    @api.model
    def remove_wrong_file(self, files):
        wrong_file_dict = self.check_xml(files)
        remove_list = []
        if 'wrongfiles' in wrong_file_dict.keys():
            for key in wrong_file_dict['wrongfiles']:
                value_keys = wrong_file_dict['wrongfiles'][key].keys()
                if 'uuid_duplicated' in value_keys:
                    remove_list.append(key)
        return remove_list
    
    @api.model
    def create_partner(self, xml64, key):
        """ It creates the supplier dictionary, getting data from the XML
        Receives an xml decode to read and returns a dictionary with data """
        try:
            cfdi_dict = self._l10n_mx_edi_prepare_cfdi_dict(xml64)
        except BaseException as exce:
            return {
                key: False, 'xml64': xml64, 'where': 'CreatePartner',
                'error': [exce.__class__.__name__, str(exce)]}

        # Check if partner exists from a previously created invoice
        partner = self.env['res.partner'].search([
            '|', ('name', '=', cfdi_dict['issuer_name']), ('vat', '=', cfdi_dict['issuer_rfc']), 
            '|', ('company_id', '=', False), ('company_id', '=', self.env.company.id)])
        if partner:
            return partner

        partner = self.env['res.partner'].sudo().create({
            'name': cfdi_dict['issuer_name'],
            'company_type': 'company',
            'vat': cfdi_dict['issuer_rfc'],
            'country_id': self.env.ref('base.mx').id,
            'supplier_rank': 1,
            'customer_rank': 0,
        })
        msg = _('This partner was created when invoice %s was created from '
                'a XML file. Please verify that the datas of partner are '
                'correct.') % (cfdi_dict['sefo'])
        partner.message_post(subject=_('Info'), body=msg)
        return partner

    def create_invoice(self, supplier, currency_id, taxes, cfdi_dict):
        """ Create supplier invoice from xml file
        :param xml: xml file etree with the datas of purchase
        :type xml: etree
        :param supplier: supplier partner
        :type supplier: res.partner
        :param currency_id: payment currency of the purchase
        :type currency_id: res.currency
        :param taxes: Datas of taxes
        :type taxes: list
        :return: the Result of the invoice creation
        :rtype: dict
        """
        move_obj = self.env['account.move']
        journal = self._context.get('journal_id', False)
        journal = self.env['account.journal'].browse(
            journal) if journal else move_obj.with_context(
                default_move_type=cfdi_dict['move_type'])._get_default_journal()
        msg = (_('Some products are not found in the database, and the account '
                 'that is used as default is not configured in the journal, '
                 'please set default account in the journal '
                 '%s to create the invoice.') % journal.name)

        prod_obj = self.env['product.product']
        prod_sup_obj = self.env['product.supplierinfo']
        sat_code_obj = self.env['product.unspsc.code']
        uom_obj = self.env['uom.uom']

        invoice_line_ids = []
        product_create = self._context.get('product_create', False)
        account_id = self._context.get('account_id', False)

        for idx, rec in enumerate(cfdi_dict['lines']):
            amount = float(rec.get('Importe', '0.0'))
            discount = 0.0
            if rec.get('Descuento') and amount:
                discount = (float(rec.get('Descuento', '0.0')) / amount) * 100
            if not rec.get('Descuento') and amount and cfdi_dict['global_discount']:
                discount = float(cfdi_dict['global_discount']) * 100 / cfdi_dict['amount_subtotal']
            name = rec.get('Descripcion', '')
            if name.splitlines():
                name = name.splitlines()[0]
            price = float(rec.get('ValorUnitario'))
            quantity = float(rec.get('Cantidad', 1.0))
            uom = rec.get('Unidad', '')
            uom_id = self.env.ref('uom.product_uom_unit')
            product_id = sat_exist = False
            
            if cfdi_dict['version'] == '3.2':
                # Global tax used for each line since that a manual tax line
                # won't have base amount assigned.
                line_taxes = [tax['tax_id'] for tax in taxes.get('old', [])]

                uom_exist = uom_obj.with_context(
                    lang='es_MX').search([('name', '=ilike', uom)], limit=1)
                uom_id = uom_exist if uom_exist else uom_id

            if cfdi_dict['version'] == '3.3':
                line_taxes = [tax['id'] for tax in taxes.get(idx, [])]
                xml_sat_code_product = rec.get('ClaveProdServ', False)
                xml_sat_code_uom = rec.get('ClaveUnidad', False)
                sat_exist = sat_code_obj.search([
                    ('code', '=', xml_sat_code_uom),
                    ('applies_to', '=', 'uom')], limit=1)
                if sat_exist:
                    uom_exist = uom_obj.with_context(lang='es_MX').search([
                        ('unspsc_code_id', '=', sat_exist.id)], limit=1)
                    uom_id = uom_exist if uom_exist else uom_id
                    # TODO Evaluate if this logic will be reimplemented in the future
                    # elif not uom_exist:
                    #    uom_vals = {
                    #        'name':sat_exist.name,
                    #        'category_id':1,
                    #        'factor':1.00, 'rounding':0.01,
                    #        'active':True, 'uom_type':'smaller',
                    #        'l10n_mx_edi_code_sat_id':sat_exist.id}
                    #    uom_id = uom_obj.create(uom_vals)

                # Cases for most frecuent mexican suppliers: CFE, gas stations, Telmex, Telcel...
                if xml_sat_code_product in self._get_fuel_codes():
                    tax = taxes.get(idx)[0] if taxes.get(idx, []) else {}
                    quantity = 1.0
                    price = tax.get('amount') / (tax.get('rate') / 100)
                    invoice_line_ids.append((0, 0, {
                        'account_id': account_id if account_id else journal.default_account_id.id,
                        'name': _('FUEL - IEPS'),
                        'quantity': quantity,
                        'product_uom_id': uom_id.id,
                        'price_unit': float(rec.get('Importe', 0)) - price}))

                # Look for SAT subclass or parent class
                sat_exist = sat_code_obj.search([
                    ('code', '=', xml_sat_code_product),
                    ('applies_to', '=', 'product')], limit=1)
                if not sat_exist:
                    sat_exist = sat_code_obj.search([
                        ('code', '=', xml_sat_code_product[:-2] + '00'),
                        ('applies_to', '=', 'product')], limit=1)
                    if not sat_exist:
                        sat_exist = self.env.ref('product_unspsc.unspsc_code_01010101')
                # False Deep Search Logic
                if sat_exist and sat_exist.product_count in range(0, 1) and \
                        sat_exist.deep_search == False:
                    product_exist = prod_obj.search([
                        ('unspsc_code_id', '=', sat_exist.id)])
                    product_id = product_exist if product_exist else product_id
                elif sat_exist and sat_exist.product_count > 1 and \
                        sat_exist.deep_search == False:
                    sat_exist.sudo().update({'deep_search': True})

            # Main Logic for matching products
            if not product_id:
                product_exist = prod_sup_obj.search([('product_name', '=ilike', name)], limit=1)
                if product_exist:
                    product_id = product_exist.product_id
                elif not product_exist:
                    product_exist = prod_obj.search([
                        ('description_purchase', '=ilike', name)], limit=1)
                    if product_exist:
                        product_id = product_exist
                    elif not product_exist:
                        product_exist = prod_obj.search([
                            ('name', '=ilike', name)], limit=1)
                        if product_exist:
                            product_id = product_exist
                        elif not product_exist and product_create == True:
                            product_vals = {
                                'name': name,
                                'description_purchase': name,
                                'list_price': price,
                                'type': 'service',
                                'uom_id': uom_id.id,
                                'uom_po_id': uom_id.id,
                                'l10n_mx_edi_code_sat_id': sat_exist.id if sat_exist else False}
                            # 'taxes_id':False,
                            # 'supplier_taxes_id':[(6,0,tax_ids)]}
                            product_exist = prod_obj.create(product_vals)
                            product_id = product_exist

            if not account_id and product_id:
                if cfdi_dict['import_type'] == 'in':
                    account_id = product_id.property_account_expense_id.id or \
                        product_id.categ_id.property_account_expense_categ_id.id
                elif cfdi_dict['import_type'] == 'out':
                    account_id = product_id.property_account_income_id.id or \
                        product_id.categ_id.property_account_income_categ_id.id
            elif not account_id and not product_id:
                account_id = journal.default_account_id.id
            if not account_id:
                return {
                    'key': False,
                    'where': 'CreateInvoice',
                    'error': [_('Account to set in the lines not found.<br/>'), msg]
                }

            default_analytic = self.env['account.analytic.default'].account_get(
                product_id=product_id.id if product_id else False, 
                partner_id=supplier.id,
                user_id=self.env.uid,
                #date=cfdi_dict['date'],
                company_id=self.env.company.id) or False

            invoice_line_ids.append((0, 0, {
                'product_id': product_id.id if product_id else False,
                'account_id': account_id,
                'analytic_account_id': default_analytic.analytic_id.id if default_analytic else False,
                'name': name,
                'quantity': quantity,
                'product_uom_id': uom_id.id,
                'tax_ids': [(6, 0, line_taxes)],
                'price_unit': price,
                'discount': discount
            }))

        payment_form = self.env['l10n_mx_edi.payment.method'].search(
            [('code', '=', cfdi_dict['payment_form'])], limit=1)
        payment_term = False
        if cfdi_dict['payment_term']:
            payment_term = self.env['account.payment.term'].search([
                ('name', '=ilike', cfdi_dict['payment_term'])], limit=1)
        vals = {
            'partner_id': supplier.id,
            'invoice_payment_term_id': payment_term.id if payment_term else 1,
            'l10n_mx_edi_payment_method_id': payment_form.id if payment_form else self.env.ref('l10n_mx_edi.payment_method_otros'),
            'l10n_mx_edi_payment_policy': cfdi_dict['payment_method'],
            'l10n_mx_edi_usage': cfdi_dict['usage'] if cfdi_dict['usage'] else 'P01',
            'invoice_date': cfdi_dict['date'],
            'currency_id': currency_id.id,
            'invoice_line_ids': invoice_line_ids,
            'move_type': cfdi_dict['move_type'],
            'l10n_mx_edi_post_time': cfdi_dict['datetime'],
            'journal_id': journal.id,
            'check_tax': cfdi_dict['taxes'].get('total_amount', 0.0),
            'check_total': cfdi_dict['amount_total'],
        }

        if cfdi_dict['import_type'] == 'in':
            vals.update({'payment_reference': cfdi_dict['sefo']})
        elif cfdi_dict['import_type'] == 'out':
            vals.update({'name': cfdi_dict['sefo']})
        
        if cfdi_dict['sefo'] == '':
            vals.pop('payment_reference', None)

        invoice_id = move_obj.create(vals)

        #local_taxes = self.get_cfdi_local_taxes(xml).get('taxes', [])
        # if local_taxes:
        #     invoice_id.write({
        #         'tax_line_ids': local_taxes,
        #     })

        xml_str = etree.tostring(cfdi_dict['cfdi_etree'], pretty_print=True, encoding='UTF-8')
        attachment = self.env['account.edi.format']._create_invoice_cfdi_attachment(invoice_id, base64.encodebytes(xml_str))
        self.env['account.edi.document'].create({
            'move_id': invoice_id.id,
            'edi_format_id': self.env.ref('l10n_mx_edi.edi_cfdi_3_3').id,
            'attachment_id': attachment.id,
            'state': 'sent'
        })
        if cfdi_dict['cfdi_type'] == 'E' and cfdi_dict['related_cfdi_uuid']:
            invoice_id._l10n_mx_edi_write_cfdi_origin(
                cfdi_dict['related_cfdi_uuid']['type'],
                cfdi_dict['related_cfdi_uuid']['uuid'])
            related_invoices = move_obj.search([
                ('partner_id', '=', supplier.id), ('move_type', '=', 'in_invoice')])
            related_invoices = related_invoices.filtered(
                lambda inv: inv.l10n_mx_edi_cfdi_uuid == cfdi_dict['related_cfdi_uuid']['uuid'])
            # TODO update core fields: reversed_entry_id, reversal_move_id
            #related_invoices.write({
            #    'refund_invoice_ids': [(4, invoice_id.id, 0)]
            #})
        invoice_id.l10n_mx_edi_update_sat_status()
        return {'key': True, 'invoice_id': invoice_id.id}

    def validate_documents(self, key, cfdi_dict):
        """ Validate the incoming or outcoming document before create or
        attach the xml to invoice
        :param key: Name of the document that is being validated
        :type key: str
        :param cfdi_dict: A dictionary containing an lxml object from 
            an xml string file
        :type cfdi_dict: dict
        :return: Result of the validation of the CFDI and the invoices created.
        :rtype: dict
        """
        wrongfiles = {}
        invoices = {}
        xml_related_uuid = related_invoice = False

        if cfdi_dict['import_type'] == 'in':
            cfdi_dict.update({'move_type': 'in_invoice' if cfdi_dict['cfdi_type'] == 'I' else 'in_refund'})
        elif cfdi_dict['import_type'] == 'out':
            cfdi_dict.update({'move_type': 'out_invoice' if cfdi_dict['cfdi_type'] == 'I' else 'out_refund'})
        
        domain_xml_type = [('move_type', '=', cfdi_dict['move_type'])]

        domain = None
        if cfdi_dict['import_type'] == 'in':
            domain = [('vat', '=', cfdi_dict['issuer_rfc'])]
        elif cfdi_dict['import_type'] == 'out':
            domain = [('vat', '=', cfdi_dict['receiver_rfc'])] if cfdi_dict['receiver_rfc'] not in ['XEXX010101000', 'XAXX010101000'] else \
                [('name', '=ilike', cfdi_dict['receiver_name']), 
                ('vat', '=', cfdi_dict['receiver_rfc'])]
        exist_partner_related = self.env['res.partner'].search(domain, limit=1, order='id asc')
        domain = [('partner_id', '=', exist_partner_related.id)] if exist_partner_related else []

        # First look for UUID
        move_obj = self.env['account.move']
        uuid_dupli = cfdi_dict['uuid'] in move_obj.search(domain).mapped('l10n_mx_edi_cfdi_uuid')

        # Then look for Reference and manage duplicated
        domain += domain_xml_type
        domain += [('invoice_date', '=', cfdi_dict['date']),
            ('l10n_mx_edi_post_time', '=', cfdi_dict['datetime'])]
        if cfdi_dict['import_type'] == 'in':
            domain += [('payment_reference', '=', cfdi_dict['sefo'])]
        elif cfdi_dict['import_type'] == 'out':
            domain += [('name', '=', cfdi_dict['sefo'])]
        invoice = move_obj.search(domain, limit=1)
        # TODO shall I keep this logic?
        #reference_count = move_obj.search_count(domain)
        #invoice = None
        #if reference_count and reference_count == 1:
        #    domain += [('invoice_date', '=', cfdi_dict['date'])]
        #    invoice = move_obj.search(domain, limit=1)
        #elif reference_count and reference_count > 1:
        #    domain += [('invoice_date', '=', cfdi_dict['date']), ('l10n_mx_edi_post_time', '=', cfdi_dict['datetime'])]
        #    invoice = move_obj.search(domain, limit=1)

        exist_currency = self.env['res.currency'].search([('name', '=', cfdi_dict['currency'])], limit=1)

        cfdi_dict['taxes']['wrong_taxes'] = cfdi_dict['taxes'].get('wrong_taxes', []) + \
            cfdi_dict['local_taxes'].get('wrong_taxes', [])
        cfdi_dict['taxes']['withno_account'] = cfdi_dict['taxes'].get('withno_account', []) + \
            cfdi_dict['local_taxes'].get('withno_account', [])

        xml_amount_tax = cfdi_dict['taxes'].get('total_amount', 0.0) + \
            cfdi_dict['local_taxes'].get('total_amount', 0.0)

        inv = move_obj
        inv_id = False
        reference_multi = invoice if invoice and cfdi_dict['uuid'] != invoice.l10n_mx_edi_cfdi_uuid else False  # noqa
        if reference_multi and not reference_multi.l10n_mx_edi_cfdi_uuid:
            inv = reference_multi
            inv_id = inv.id
            reference_multi = False
            inv.l10n_mx_edi_update_sat_status()
        xml_status = inv.l10n_mx_edi_sat_status
        inv_emitter_vat = (inv and inv.commercial_partner_id.vat or '').upper()
        inv_receiver_vat = (self.env.company.vat or '').upper()
        inv_amount = inv.amount_total
        inv_amount_tax = inv.amount_tax
        inv_folio = inv.payment_reference

        omit_cfdi_related = self._context.get('omit_cfdi_related')
        if omit_cfdi_related == False and cfdi_dict['cfdi_type'] == 'E' and cfdi_dict['related_cfdi_uuid'] != '':
            related_invoice = cfdi_dict['related_cfdi_uuid'] in move_obj.search([
                ('move_type', '=', 'in_invoice')]).mapped('l10n_mx_edi_cfdi_uuid')

        errors = [
            (not cfdi_dict['uuid'] and cfdi_dict['version'] in ('3.0', '3.2', '3.3'),
                {'unsigned': True}),
            # TODO restore this error after accounting is completed
            #(cfdi_dict['version'] != '3.3', {'version': True}),
            (xml_status == 'cancelled',
                {'cancelled': (True, cfdi_dict['sefo'])}),
            ((cfdi_dict['uuid'] and uuid_dupli),
                {'uuid_duplicated': cfdi_dict['uuid']}),
            ((inv_receiver_vat != cfdi_dict['receiver_rfc']),
                {'rfc': (cfdi_dict['receiver_rfc'], inv_receiver_vat)}),
            ((not inv_id and reference_multi),
                {'reference_multi': (cfdi_dict['issuer_name'], cfdi_dict['sefo'])}),
            ((not inv_id and not exist_partner_related),
                {'supplier': cfdi_dict['issuer_name']}),
            ((not inv_id and cfdi_dict['currency'] and not exist_currency),
                {'currency': cfdi_dict['currency']}),
            ((not inv_id and cfdi_dict['taxes'].get('wrong_taxes', False)),
                {'taxes': cfdi_dict['taxes'].get('wrong_taxes', False)}),
            ((not inv_id and cfdi_dict['taxes'].get('withno_account', False)),
                {'taxes_wn_accounts': cfdi_dict['taxes'].get('withno_account', False)}),
            ((inv_id and inv_folio != cfdi_dict['sefo']),
                {'folio': (cfdi_dict['sefo'], inv_folio)}),
            ((inv_id and inv_emitter_vat != cfdi_dict['issuer_rfc']),
                {'rfc_supplier': (cfdi_dict['issuer_rfc'], inv_emitter_vat)}),
            ((inv_id and not float_is_zero(float(inv_amount) - float(cfdi_dict['amount_total']), precision_digits=2)),
                {'amount': (cfdi_dict['amount_total'], inv_amount)}),
            ((inv_id and not float_is_zero(float(inv_amount_tax) - float(
                xml_amount_tax), precision_digits=2)),
                {'amount_tax': (xml_amount_tax, inv_amount_tax, cfdi_dict['sefo'])}),
            ((xml_related_uuid and not related_invoice),
                {'invoice_not_found': xml_related_uuid}),
            ((omit_cfdi_related == False and cfdi_dict['cfdi_type'] == 'E' and not xml_related_uuid),
                {'no_xml_related_uuid': cfdi_dict['uuid']})
        ]

        msg = {}
        for error in errors:
            if error[0]:
                msg.update(error[1])
        if msg:
            msg.update({'xml64': True})
            wrongfiles.update({key: msg})
            return {'wrongfiles': wrongfiles, 'invoices': invoices}

        if not inv_id:
            invoice_status = self.create_invoice(
                exist_partner_related, exist_currency,
                cfdi_dict['taxes'].get('taxes_ids', {}), cfdi_dict)

            if invoice_status['key'] is False:
                del invoice_status['key']
                invoice_status.update({'xml64': True})
                wrongfiles.update({key: invoice_status})
                return {'wrongfiles': wrongfiles, 'invoices': invoices}

            del invoice_status['key']
            invoices.update({key: invoice_status})
            return {'wrongfiles': wrongfiles, 'invoices': invoices}

        xml_str = etree.tostring(cfdi_dict['cfdi_etree'], pretty_print=True, encoding='UTF-8')
        attachment = self.env['account.edi.format']._create_invoice_cfdi_attachment(inv, base64.encodebytes(xml_str))
        EdiDocument = self.env['account.edi.document']
        exists_edi_document = EdiDocument.search([
            ('move_id', '=', inv.id), 
            ('edi_format_id', '=', self.env.ref('l10n_mx_edi.edi_cfdi_3_3').id),
        ])
        if exists_edi_document and not exists_edi_document.attachment_id:
            exists_edi_document.write({'attachment_id': attachment.id})        
        else:
            EdiDocument.create({
            'move_id': inv.id,
            'edi_format_id': self.env.ref('l10n_mx_edi.edi_cfdi_3_3').id,
            'attachment_id': attachment.id,
            'state': 'sent'
        })
        inv.payment_reference = cfdi_dict['sefo']
        invoices.update({key: {'invoice_id': inv.id}})
        return {'wrongfiles': wrongfiles, 'invoices': invoices}

    @api.model
    def check_xml(self, files):
        """ Validate the attributes in the xml before create invoice
        or attach xml to it
        :param files:        dictionary of CFDIs in b64
        :type files:         dict
        :return:             the Result of the CFDI validation
        :rtype:              dict
        """
        if not isinstance(files, dict):
            raise UserError(_("Something went wrong. The parameter for XML "
                              "files must be a dictionary."))
        wrongfiles = {}
        invoices = {}
        outgoing_docs = {}

        for key, xml64 in files.items():
            try:
                cfdi_dict = self._l10n_mx_edi_prepare_cfdi_dict(xml64)
                cfdi_dict.update({'import_type': self._context.get('l10n_mx_edi_invoice_type')})
            except (AttributeError, SyntaxError) as exce:
                wrongfiles.update({
                    key: {
                        'xml64': xml64, 'where': 'CheckXML',
                        'error': [exce.__class__.__name__, str(exce)]
                    }
                })
                continue

            if cfdi_dict['cfdi_type'] == 'E':
                outgoing_docs.update({
                    key: {
                        'xml64': xml64,
                        'xml': cfdi_dict['cfdi_etree'], 
                        'cfdi_dict': cfdi_dict
                    }
                })
                continue
            elif cfdi_dict['cfdi_type'] != 'I' or cfdi_dict['payslip']:
                wrongfiles.update({
                    key: {
                        'xml64': xml64,
                        'cfdi_type': True
                    }
                })
                continue

            # Check the incoming documents
            validated_documents = self.validate_documents(key, cfdi_dict)
            
            wrongfiles.update(validated_documents.get('wrongfiles'))

            if wrongfiles.get(key, False) and \
                wrongfiles[key].get('xml64', False):
                wrongfiles[key]['xml64'] = xml64

            invoices.update(validated_documents.get('invoices'))

        # Check the outgoing documents
        for key, value in outgoing_docs.items():
            xml64 = value.get('xml64')
            xml = value.get('xml')
            validated_documents = self.validate_documents(key, value.get('cfdi_dict'))

            wrongfiles.update(validated_documents.get('wrongfiles'))

            if wrongfiles.get(key, False) and \
                wrongfiles[key].get('xml64', False):
                wrongfiles[key]['xml64'] = xml64

            invoices.update(validated_documents.get('invoices'))

        return {'wrongfiles': wrongfiles, 'invoices': invoices}

    @api.model
    def _get_fuel_codes(self):
        """Return the codes that can be used in FUEL"""
        return [str(r) for r in range(15101500, 15101513)]
