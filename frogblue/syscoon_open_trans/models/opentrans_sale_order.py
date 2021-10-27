# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models

import requests
import datetime
from lxml import etree
from requests.structures import CaseInsensitiveDict


bmecat = 'http://www.bmecat.org/bmecat/2005'

"""
wir haben  die Einrichtung abgeschlossen. Nachfolgend für Sie die notwendigen Informationen, um die Bestellung übermitteln zu können.
Die XML Bestelldaten übermitteln Sie bitte an folgende URL: https:// b2b.frogblue.shop/Shop/DE/ThirdParty/ImportOrder
Im Request Header verwenden Sie bitte den Content-Type text/xml
Im Body übermitteln Sie dann die XML Daten.
Der Aufruf der Schnittstelle ist durch Basic Authentication abgesichert. Bitte verwenden Sie dafür folgenden Benutzernamen. Das Passwort schicke ich Ihnen in einer separaten E-Mail zu.

Benutzername: frogblue_openTrans
Wenn Sie als Response den StatusCode 200 erhalten, wurde die Bestellung erfolgreich in unser System importiert.
Bei einem anderen StatusCode ist ein Fehler aufgetreten.
Eine erfolgreich übermittelte Bestellung kann nicht nochmal mit derselben ORDER_ID übermittelt werden. In diesem Fall würden Sie als Response einen Fehler erhalten und die Information, dass eine Bestellung mit dieser ORDER_ID bereits vorhanden ist.
Wie bereits in der letzten E-Mail geschrieben, würde ich Sie bitten Herrn Kerz und mir eine kurze E-Mail zu schreiben, wenn Sie Ihre Tests durchführen. Wir prüfen dann den Import auch von unserer Seite her.
Sollten sich Fragen ergeben, so stehe ich Ihnen gerne zur Verfügung.

URL: https:// b2b.frogblue.shop/Shop/DE/ThirdParty/ImportOrder
Benutzername: frogblue_openTrans
Passwort: f9B0k8wHPPCE984kGs1E
"""

class OpenTransSaleOrder(models.TransientModel):
    _name = 'open.trans.sale.order'
    _description = 'OpenTrans Module for Sale Orders'

    def send_order_xml(self, order_id):
        order = self.create_order_xml(order_id)
        response = False
        responsecode = False
        statuscode = statustext = message = errors = False
        if not order_id.opentrans_order_not_send:
            response = self.transmit_order_xml(order)
        if response and response.status_code == 200:
            responsecode = response.status_code
            statuscode, statustext, message, errors = self.get_response_text(response.content)
        elif response and response.status_code != 200:
            responsecode = response.status_code
            statuscode, statustext, message, errors = self.get_response_text(response.content)
        return order, responsecode, statuscode, statustext, message, errors

    def create_order_xml(self, order_id):
        xml = self.make_order_xml(order_id)
        order = etree.tostring(xml, pretty_print = True, xml_declaration = True, encoding = 'UTF-8')
        return order

    def make_order_xml(self, sale_order_id):
        attr_qname = etree.QName('http://www.w3.org/2001/XMLSchema-instance', 'schemaLocation')
        nsmap = {
            None: 'http://www.opentrans.org/XMLSchema/2.1',
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'bmecat': 'http://www.bmecat.org/bmecat/2005',
            'xmime': 'http://www.w3.org/2005/05/xmlmime',
            'xsig': 'http://www.w3.org/2000/09/xmldsig#',
        }

        order = etree.Element('ORDER',
            {attr_qname: 'http://www.opentrans.org/XMLSchema/2.1 opentrans_2_1.xsd'},
            nsmap=nsmap)
        order.attrib['type'] = 'standard'
        order.attrib['version'] = '2.1'

        order_header = etree.SubElement(order, 'ORDER_HEADER')
        control_info = etree.SubElement(order_header, 'CONTROL_INFO')
        generator_info = etree.SubElement(control_info, 'GENERATOR_INFO')
        generator_info.text = 'frogblue Odoo'
        generation_date = etree.SubElement(control_info, 'GENERATION_DATE')
        generation_date.text = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

        order_info = etree.SubElement(order_header, 'ORDER_INFO')
        order_id = etree.SubElement(order_info, 'ORDER_ID')
        order_id.text = sale_order_id.name
        order_date = etree.SubElement(order_info, 'ORDER_DATE')
        order_date.text = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

        parties = etree.SubElement(order_info, 'PARTIES')
        party_buyer = etree.SubElement(parties, 'PARTY')
        party_buyer_bme_cat_party_id = etree.SubElement(
            party_buyer, etree.QName(bmecat, 'PARTY_ID'), 
            attrib={'type': 'supplier_specific'}
        )
        party_buyer_bme_cat_party_id.text = sale_order_id.partner_id.property_account_receivable_id.code
        party_buyer_role = etree.SubElement(party_buyer, 'PARTY_ROLE')
        party_buyer_role.text = 'buyer'
        party_buyer_address = etree.SubElement(party_buyer, 'ADDRESS')
        party_buyer_address_name = etree.SubElement(party_buyer_address, etree.QName(bmecat, 'NAME'))
        party_buyer_address_name.text = sale_order_id.partner_id.name
        if sale_order_id.partner_id.street2:
            party_buyer_address_name2 = etree.SubElement(party_buyer_address, etree.QName(bmecat, 'NAME2'))
            party_buyer_address_name2.text = sale_order_id.partner_id.street
        party_buyer_address_email = etree.SubElement(party_buyer_address, etree.QName(bmecat, 'EMAILS'))
        party_buyer_address_email_mail = etree.SubElement(party_buyer_address_email, etree.QName(bmecat, 'EMAIL'))
        if sale_order_id.partner_id.email:
            party_buyer_address_email_mail.text = sale_order_id.partner_id.email
        else:
            party_buyer_address_email_mail.text = 'sales@frogblue.com'
        party_buyer_street = etree.SubElement(party_buyer_address, etree.QName(bmecat, 'STREET'))
        if sale_order_id.partner_id.street2:
            party_buyer_street.text = sale_order_id.partner_id.street2
        else:
            party_buyer_street.text = sale_order_id.partner_id.street
        party_buyer_zip = etree.SubElement(party_buyer_address, etree.QName(bmecat, 'ZIP'))
        party_buyer_zip.text = sale_order_id.partner_id.zip
        party_buyer_city = etree.SubElement(party_buyer_address, etree.QName(bmecat, 'CITY'))
        party_buyer_city.text = sale_order_id.partner_id.city
        party_buyer_country = etree.SubElement(party_buyer_address, etree.QName(bmecat, 'COUNTRY_CODED'))
        party_buyer_country.text = sale_order_id.partner_id.country_id.code or 'DE'

        party_buyer_delivery = etree.SubElement(parties, 'PARTY')
        party_buyer_delivery_bme_cat_party_id = etree.SubElement(
            party_buyer_delivery, etree.QName(bmecat, 'PARTY_ID'), 
            attrib={'type': 'supplier_specific'}
        )
        party_buyer_delivery_bme_cat_party_id.text = str(sale_order_id.partner_shipping_id.id)
        party_buyer_delivery_role = etree.SubElement(party_buyer_delivery, 'PARTY_ROLE')
        party_buyer_delivery_role.text = 'delivery'
        party_buyer_delivery_address = etree.SubElement(party_buyer_delivery, 'ADDRESS')
        party_buyer_delivery_address_name = etree.SubElement(party_buyer_delivery_address, etree.QName(bmecat, 'NAME'))
        party_buyer_delivery_address_name.text = sale_order_id.partner_shipping_id.name or sale_order_id.partner_id.name
        if sale_order_id.partner_shipping_id.street2:
            party_buyer_delivery_address_name2 = etree.SubElement(party_buyer_delivery_address, etree.QName(bmecat, 'NAME2'))
            party_buyer_delivery_address_name2.text = sale_order_id.partner_shipping_id.street or sale_order_id.partner_id.street
        party_buyer_delivery_street = etree.SubElement(party_buyer_delivery_address, etree.QName(bmecat, 'STREET'))
        if sale_order_id.partner_shipping_id.street2:
            party_buyer_delivery_street.text = sale_order_id.partner_shipping_id.street2
        else:
            party_buyer_delivery_street.text = sale_order_id.partner_shipping_id.street
        party_buyer_delivery_zip = etree.SubElement(party_buyer_delivery_address, etree.QName(bmecat, 'ZIP'))
        party_buyer_delivery_zip.text = sale_order_id.partner_shipping_id.zip
        party_buyer_delivery_city = etree.SubElement(party_buyer_delivery_address, etree.QName(bmecat, 'CITY'))
        party_buyer_delivery_city.text = sale_order_id.partner_shipping_id.city
        party_buyer_delivery_country = etree.SubElement(party_buyer_delivery_address, etree.QName(bmecat, 'COUNTRY_CODED'))
        party_buyer_delivery_country.text = sale_order_id.partner_shipping_id.country_id.code or 'DE'

        party_buyer_invoice = etree.SubElement(parties, 'PARTY')
        party_buyer_invoice_bme_cat_party_id = etree.SubElement(
            party_buyer_invoice, etree.QName(bmecat, 'PARTY_ID'), 
            attrib={'type': 'supplier_specific'}
        )
        party_buyer_invoice_bme_cat_party_id.text = str(sale_order_id.partner_invoice_id.id)
        party_buyer_invoice_role = etree.SubElement(party_buyer_invoice, 'PARTY_ROLE')
        party_buyer_invoice_role.text = 'invoice_recipient'
        party_buyer_invoice_address = etree.SubElement(party_buyer_invoice, 'ADDRESS')
        party_buyer_invoice_address_name = etree.SubElement(party_buyer_invoice_address, etree.QName(bmecat, 'NAME'))
        party_buyer_invoice_address_name.text = sale_order_id.partner_invoice_id.name or sale_order_id.partner_id.name
        if sale_order_id.partner_invoice_id.street2:
            party_buyer_invoice_address_name2 = etree.SubElement(party_buyer_invoice_address, etree.QName(bmecat, 'NAME2'))
            party_buyer_invoice_address_name2.text = sale_order_id.partner_invoice_id.street or sale_order_id.partner_id.street
        party_buyer_invoice_street = etree.SubElement(party_buyer_invoice_address, etree.QName(bmecat, 'STREET'))
        if sale_order_id.partner_invoice_id.street2:
            party_buyer_invoice_street.text = sale_order_id.partner_invoice_id.street2
        else:
            party_buyer_invoice_street.text = sale_order_id.partner_invoice_id.street
        party_buyer_invoice_zip = etree.SubElement(party_buyer_invoice_address, etree.QName(bmecat, 'ZIP'))
        party_buyer_invoice_zip.text = sale_order_id.partner_invoice_id.zip
        party_buyer_invoice_city = etree.SubElement(party_buyer_invoice_address, etree.QName(bmecat, 'CITY'))
        party_buyer_invoice_city.text = sale_order_id.partner_invoice_id.city
        party_buyer_invoice_country = etree.SubElement(party_buyer_invoice_address, etree.QName(bmecat, 'COUNTRY_CODED'))
        party_buyer_invoice_country.text = sale_order_id.partner_invoice_id.country_id.code or 'DE'

        customer_order_reference = etree.SubElement(order_info, 'CUSTOMER_ORDER_REFERENCE')
        reference_order_id = etree.SubElement(customer_order_reference, 'ORDER_ID')
        reference_order_id.text = sale_order_id.client_order_ref or ''

        order_item_list = etree.SubElement(order, 'ORDER_ITEM_LIST')
        count = 1
        for line in sale_order_id.order_line:
            order_item = etree.SubElement(order_item_list, 'ORDER_ITEM')
            order_item_line = etree.SubElement(order_item, 'LINE_ITEM_ID')
            order_item_line.text = str(count)
            order_item_product = etree.SubElement(order_item, 'PRODUCT_ID')
            order_item_product_id = etree.SubElement(order_item_product, etree.QName(bmecat, 'SUPPLIER_PID'))
            if line.product_id.default_code == '900.000000':
                order_item_product_id.text = '100013'
            else:
                if '900' in line.product_id.default_code:
                    product_code = line.product_id.name.split(' ')
                    order_item_product_id.text = product_code[0]
                else:
                    order_item_product_id.text = line.product_id.default_code
            order_item_product_short = etree.SubElement(order_item_product, etree.QName(bmecat, 'DESCRIPTION_SHORT'))
            if '900' in line.product_id.default_code:
                product_code = line.product_id.name.split(' ')
                order_item_product_short.text = product_code[1][:150]
            else:
                order_item_product_short.text = line.product_id.name
            order_item_product_long = etree.SubElement(order_item_product, etree.QName(bmecat, 'DESCRIPTION_LONG'))
            order_item_product_long.text = line.name
            order_item_quantity = etree.SubElement(order_item_product, 'QUANTITY')
            order_item_quantity.text = str(line.product_uom_qty)
            order_item_price_fix = etree.SubElement(order_item, 'PRODUCT_PRICE_FIX')
            order_item_price_fix_amount = etree.SubElement(order_item_price_fix, etree.QName(bmecat, 'PRICE_AMOUNT'))
            order_item_price_fix_amount.text = str(line.price_unit)
            order_item_partial = etree.SubElement(order_item, 'PARTIAL_SHIPMENT_ALLOWED')
            if sale_order_id.picking_policy and sale_order_id.picking_policy == 'direct':
                order_item_partial.text = 'TRUE'
            else:
                order_item_partial.text = 'FALSE'
            count += 1

        if sale_order_id.payment_term_id:
            order_item = etree.SubElement(order_item_list, 'ORDER_ITEM')
            order_item_line = etree.SubElement(order_item, 'LINE_ITEM_ID')
            order_item_line.text = str(count)
            order_item_product = etree.SubElement(order_item, 'PRODUCT_ID')
            order_item_product_id = etree.SubElement(order_item_product, etree.QName(bmecat, 'SUPPLIER_PID'))
            order_item_product_id.text = '100012'
            order_item_product_short = etree.SubElement(order_item_product, etree.QName(bmecat, 'DESCRIPTION_SHORT'))
            order_item_product_short.text = 'Zahlart - ' + sale_order_id.payment_term_id.note
            order_item_quantity = etree.SubElement(order_item_product, 'QUANTITY')
            order_item_quantity.text = '1'
            order_item_price_fix = etree.SubElement(order_item, 'PRODUCT_PRICE_FIX')
            order_item_price_fix_amount = etree.SubElement(order_item_price_fix, etree.QName(bmecat, 'PRICE_AMOUNT'))
            order_item_price_fix_amount.text = '0.0'

        return order

    def transmit_order_xml(self, order):
        url = self.env.company.transmit_order_url #'https://b2b.frogblue.shop/Shop/DE/ThirdParty/ImportOrder'
        headers = CaseInsensitiveDict()
        headers['Content-Type'] = 'text/xml'
        response = requests.post(url, headers=headers, data=order,  auth=('frogblue_openTrans', 'f9B0k8wHPPCE984kGs1E'))
        return response

    def get_response_text(self, response):
        xml = etree.fromstring(response.replace(b'utf-16', b'utf-8'))
        statuscode = xml.xpath('//StatusCode').pop().text
        statustext = xml.xpath('//Status').pop().text
        message = xml.xpath('//Message').pop().text
        errors = xml.xpath('//Errors').pop().text
        return statuscode, statustext, message, errors
